#!/usr/bin/python3

import os
import sys
import yaml
from cerberus import Validator, errors
from cerberus.errors import BasicErrorHandler
from pcchecks import Regex, icons_check, toc_check, nbsp_check, checks, nesting_in_modules_check, add_res_section_module_check, add_res_section_assembly_check
import re
import subprocess


class CustomErrorHandler(BasicErrorHandler):
    """Custom error messages."""
    messages = errors.BasicErrorHandler.messages.copy()
    messages[errors.REQUIRED_FIELD.code] = "key is missing"
    messages[errors.UNKNOWN_FIELD.code] = "unsupported key"
    messages[errors.NOT_NULLABLE.code] = "value can't be empty"


def printing_build_yml_error(msg, *files):
    print('\nERROR: Your build.yml contains the following {}:\n'.format(msg))
    for file in files:
        if file:
            print('\t', file)


class Report():
    """Create and print report. thank u J."""

    def __init__(self):
        """Create placeholder for problem description."""
        self.report = {}
        self.count = 0

    def create_report(self, category, file_path):
        """Generate report."""
        self.count += 1
        if not category in self.report:
            self.report[category] = []
        self.report[category].append(file_path)

    def print_report(self):

        """Print report."""
        separator = "\n\t"

        for category, files in self.report.items():
            print("\nERROR: {} found in the following files:".format(category))
            print('\t' + separator.join(files))


def get_yaml_size(yaml_file):
    """Test if build.yml is empty."""
    if os.path.getsize(yaml_file) == 0:
        print("\nYour build.yml file is empty; exiting...")
        sys.exit(2)


def load_doc(yaml_file):
    """Load build.yml and test for syntax errors."""
    with open(yaml_file, 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError:
            print("There's a syntax error in your build.yml file. Please fix it and try again.\nTo detect an error try running yaml lint on your build.yml file.")
            sys.exit(2)


def get_yaml_errors(yaml_schema, yaml_doc):
    # load validator with custom error handler
    v = Validator(yaml_schema, error_handler=CustomErrorHandler())
    # validate the build.yml with schema
    v.validate(yaml_doc, yaml_schema)

    if v.errors:
        print("ERROR: there is an error in your yaml file:")
        for key in v.errors.keys():
            print("\n\t'{}' {}".format(key, ', '.join(str(item) for item in v.errors[key])))
        sys.exit(2)


def get_attribute_files(yaml_doc):
    attribute_files = []

    for variant in yaml_doc['variants']:
        for item in variant['attributes']:
            attribute_files.append(item)

    return attribute_files


def get_existence(files):
    files_found = []
    files_not_found = []

    for item in files:
        if os.path.exists(item):
            files_found.append(item)
        else:
            files_not_found.append(item)

    return files_found, files_not_found


def get_not_exist(content_list):
    files_found, files_not_found = get_existence(content_list)

    return files_not_found


def get_exist(content_list):
    files_found, files_not_found = get_existence(content_list)

    return files_found


def get_files(yaml_doc, var):
    content_list = []
    missing_files = []

    for yaml_dict in yaml_doc['variants']:
        for include in yaml_dict['files'][var]:
            content = get_files_bash(include)
            if content:
                if '' in content:
                    missing_files.append(include)
                else:
                    for i in content:
                        if i not in content_list:
                            content_list.append(i)

    return content_list, missing_files


def get_missing_files(yaml_doc, var):
    content_list, missing_files = get_files(yaml_doc, var)
    return missing_files


def get_exitsing_files(yaml_doc, var):
    content_list, missing_files = get_files(yaml_doc, var)
    return content_list


def get_files_bash(file_path):
    command = ("find  " + file_path + " -type f 2>/dev/null")
    process = subprocess.run(command, stdout=subprocess.PIPE, shell=True).stdout
    files = process.strip().decode('utf-8').split('\n')

    return files


def validate_attribute_files(attribute_files):
    """Validate attributes file."""
    report = Report()

    for path in attribute_files:
        with open(path, 'r') as file:
            original = file.read()
            stripped = Regex.MULTI_LINE_COMMENT.sub('', original)
            stripped = Regex.SINGLE_LINE_COMMENT.sub('', stripped)

            icons_check(report, stripped, path)
            toc_check(report, stripped, path)
            nbsp_check(report, stripped, path)

    return report


def get_attribute_file_errors(yaml_doc):
    attribute_files = get_attribute_files(yaml_doc)
    missing_attribute_files = get_not_exist(attribute_files)
    exiting_attribute_files = get_exist(attribute_files)

    if missing_attribute_files:
        printing_build_yml_error("attribute files that do not exist in your repository", missing_attribute_files)

    if exiting_attribute_files:
        for item in attribute_files:
            file_name = os.path.basename(item)
            file_path = os.path.dirname(item)
            if not file_path.startswith("_"):
                if "/_" not in file_path:
                    if not file_name.startswith("_"):
                        printing_build_yml_error("files or directories that do not follow the attribute naming conventions. Attribute files or directory they are stored in should start with an undescore", item)

        attribute_validation = validate_attribute_files(exiting_attribute_files)

        if attribute_validation.count != 0:
            attribute_validation.print_report()


def get_realpath(files):
    unique_files = []

    for file in files:
        real_path = os.path.realpath(file)
        if real_path not in unique_files:
            unique_files.append(real_path)

    files = []

    pwd = os.getcwd()
    for i in unique_files:
        relative_path = os.path.relpath(i, pwd)
        files.append(relative_path)

    return files


def get_content_list(yaml_doc):
    included = get_exitsing_files(yaml_doc, 'included')
    excluded = get_exitsing_files(yaml_doc, 'excluded')

    unique_includes = get_realpath(included)
    unique_excludes = get_realpath(excluded)

    for item in unique_includes:
        if item in unique_excludes:
            unique_includes.remove(item)

    return unique_includes


def get_fake_path_files(yaml_doc):
    missing_includes = get_missing_files(yaml_doc, 'included')
    missing_excludes = get_missing_files(yaml_doc, 'excluded')

    missing_files = missing_excludes + missing_includes
    if missing_files:
        printing_build_yml_error("files or directories that do not exist in your repository", missing_files)


def sort_prefix_files(yaml_doc):
    prefix_assembly = []
    prefix_modules = []
    undefined_content = []

    content_list = get_content_list(yaml_doc)

    for item in content_list:
        if item.endswith('.adoc'):
            file_name = os.path.basename(item)
            if file_name.startswith('assembly'):
                prefix_assembly.append(item)
            elif file_name.startswith(("proc_", "con_", "ref_", "proc-", "con-", "ref-")):
                prefix_modules.append(item)
            else:
                undefined_content.append(item)

    return prefix_assembly, prefix_modules, undefined_content


def get_prefix_assemblies(yaml_doc):
    prefix_assembly, prefix_modules, undefined_content = sort_prefix_files(yaml_doc)

    return prefix_assembly


def get_prefix_modules(yaml_doc):
    prefix_assembly, prefix_modules, undefined_content = sort_prefix_files(yaml_doc)

    return prefix_modules


def get_undefined_content(yaml_doc):
    prefix_assembly, prefix_modules, undefined_content = sort_prefix_files(yaml_doc)

    return undefined_content


def file_validation(yaml_doc):
    undefined_content = get_undefined_content(yaml_doc)
    undetermined_file_type = []
    report = Report()

    for path in undefined_content:
        with open(path, 'r') as file:
            original = file.read()
            stripped = Regex.MULTI_LINE_COMMENT.sub('', original)
            stripped = Regex.SINGLE_LINE_COMMENT.sub('', stripped)
            stripped = Regex.CODE_BLOCK_DASHES.sub('', stripped)
            stripped = Regex.CODE_BLOCK_TWO_DASHES.sub('', stripped)
            stripped = Regex.CODE_BLOCK_DOTS.sub('', stripped)
            stripped = Regex.INTERNAL_IFDEF.sub('', stripped)

            if re.findall(Regex.MODULE_TYPE, stripped):
                checks(report, stripped, original, path)
                icons_check(report, stripped, path)
                toc_check(report, stripped, path)
                nesting_in_modules_check(report, stripped, path)
                add_res_section_module_check(report, stripped, path)

            elif re.findall(Regex.ASSEMBLY_TYPE, stripped):
                checks(report, stripped, original, path)
                icons_check(report, stripped, path)
                toc_check(report, stripped, path)
                add_res_section_assembly_check(report, stripped, path)

            else:
                undetermined_file_type.append(path)

    confused_files = []

    prefix_assemblies = get_prefix_assemblies(yaml_doc)

    for path in prefix_assemblies:
        with open(path, "r") as file:
            original = file.read()
            stripped = Regex.MULTI_LINE_COMMENT.sub('', original)
            stripped = Regex.SINGLE_LINE_COMMENT.sub('', stripped)
            stripped = Regex.CODE_BLOCK_DASHES.sub('', stripped)
            stripped = Regex.CODE_BLOCK_TWO_DASHES.sub('', stripped)
            stripped = Regex.CODE_BLOCK_DOTS.sub('', stripped)
            stripped = Regex.INTERNAL_IFDEF.sub('', stripped)
            checks(report, stripped, original, path)
            icons_check(report, stripped, path)
            toc_check(report, stripped, path)

            if re.findall(Regex.MODULE_TYPE, stripped):
                confused_files.append(path)
                nesting_in_modules_check(report, stripped, path)
                add_res_section_module_check(report, stripped, path)
            else:
                add_res_section_assembly_check(report, stripped, path)

    prefix_modules = get_prefix_modules(yaml_doc)
    for path in prefix_modules:
        with open(path, "r") as file:
            original = file.read()
            original = file.read()
            stripped = Regex.MULTI_LINE_COMMENT.sub('', original)
            stripped = Regex.SINGLE_LINE_COMMENT.sub('', stripped)
            stripped = Regex.CODE_BLOCK_DASHES.sub('', stripped)
            stripped = Regex.CODE_BLOCK_TWO_DASHES.sub('', stripped)
            stripped = Regex.CODE_BLOCK_DOTS.sub('', stripped)
            stripped = Regex.INTERNAL_IFDEF.sub('', stripped)
            checks(report, stripped, original, path)
            icons_check(report, stripped, path)
            toc_check(report, stripped, path)

            if re.findall(Regex.ASSEMBLY_TYPE, stripped):
                confused_files.append(path)
                add_res_section_assembly_check(report, stripped, path)
            else:
                nesting_in_modules_check(report, stripped, path)
                add_res_section_module_check(report, stripped, path)

    if confused_files:
        printing_build_yml_error("files that have missmathed name prefix and content type tag. Content type tag takes precident. The files were checked according to the tag", confused_files)

    if undetermined_file_type:
        printing_build_yml_error('files that can not be classifiyed as modules or assemblies', undetermined_file_type)

    return report


def yaml_validation(yaml_file):
    # define path to script
    path_to_script = os.path.dirname(os.path.realpath(__file__))
    # load schema
    schema = eval(open(path_to_script + '/schema.py', 'r').read())
    # load build.yml
    loaded_yaml = load_doc(yaml_file)

    get_yaml_size(yaml_file)
    get_yaml_errors(schema, loaded_yaml)
    get_attribute_file_errors(loaded_yaml)
    get_fake_path_files(loaded_yaml)
    validation = file_validation(loaded_yaml)

    if validation.count != 0:
        validation.print_report()
