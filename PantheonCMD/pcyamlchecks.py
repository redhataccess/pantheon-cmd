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
    """Print error message."""
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
    """Validate build.yml against a schema abd report errors."""
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
    """Get attribute files specifiyed in build.yml."""
    attribute_files = []

    for variant in yaml_doc['variants']:
        for item in variant['attributes']:
            attribute_files.append(item)

    return attribute_files


def get_existence(files):
    """Return a list of found files and a list of not found files."""
    files_found = []
    files_not_found = []

    for item in files:
        if os.path.exists(item):
            files_found.append(item)
        else:
            files_not_found.append(item)

    return files_found, files_not_found


def get_files_bash(file_path):
    """Expand filepaths."""
    command = ("find  " + file_path + " -type f 2>/dev/null")
    process = subprocess.run(command, stdout=subprocess.PIPE, shell=True).stdout
    files = process.strip().decode('utf-8').split('\n')

    return files


def get_files(yaml_doc, var):
    """Get files listed in the build.yml."""
    content_list = []
    missing_files = []

    for yaml_dict in yaml_doc['variants']:
        for subkey in yaml_dict['files']:
            if subkey != var:
                continue

            for include in yaml_dict['files'][var]:
                content = get_files_bash(include)
                if not content:
                    continue

                if '' in content:
                    missing_files.append(include)
                    continue

                for i in content:
                    if i not in content_list:
                        content_list.append(i)

    return content_list, missing_files


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
    """Report errors found with attribute files."""
    attribute_files = get_attribute_files(yaml_doc)
    missing_attribute_files, exiting_attribute_files = get_existence(attribute_files)

    if missing_attribute_files:
        printing_build_yml_error("attribute files that do not exist in your repository", missing_attribute_files)

    if exiting_attribute_files:
        for item in exiting_attribute_files:
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
    """Get unique file list of content excluding attributes"""
    # get unique file list through realpath
    unique_files = []

    for file in files:
        if file.endswith('adoc'):
            real_path = os.path.realpath(file)
            if real_path not in unique_files:
                unique_files.append(real_path)

    # convert realpath back to relative path
    relative_path_files = []

    pwd = os.getcwd()
    for i in unique_files:
        relative_path = os.path.relpath(i, pwd)
        relative_path_files.append(relative_path)

    # remove attribute files from list
    files = []

    for item in relative_path_files:
        file_name = os.path.basename(item)
        file_path = os.path.dirname(item)
        if file_path.startswith("_"):
            continue
        elif "/_" in file_path:
            continue
        elif file_name.startswith("_"):
            continue
        else:
            files.append(item)

    return files


def get_content_list(yaml_doc):
    """Get a unique list of included files with removed excludes."""
    included, fake_path_includes = get_files(yaml_doc, 'included')
    excluded, fake_path_excludes = get_files(yaml_doc, 'excluded')

    unique_includes = get_realpath(included)
    unique_excludes = get_realpath(excluded)

    for item in unique_includes:
        if item in unique_excludes:
            unique_includes.remove(item)

    return unique_includes


def get_fake_path_files(yaml_doc):
    """Error out on fake filepaths in build.yml"""
    included, fake_path_includes = get_files(yaml_doc, 'included')
    excluded, fake_path_excludes = get_files(yaml_doc, 'excluded')

    missing_files = fake_path_excludes + fake_path_includes
    if missing_files:
        printing_build_yml_error("files or directories that do not exist in your repository", missing_files)


def sort_prefix_files(yaml_doc):
    """Get a list of assemblies, modulesa, and unidentifiyed files."""
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


def file_validation(yaml_doc):
    """Validate all files."""
    prefix_assembly, prefix_modules, undefined_content = sort_prefix_files(yaml_doc)

    all_files = prefix_assembly + prefix_modules + undefined_content

    undetermined_file_type = []
    confused_files = []

    report = Report()

    for path in all_files:
        with open(path, 'r') as file:
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

            if path in undefined_content:
                if re.findall(Regex.MODULE_TYPE, stripped):
                    nesting_in_modules_check(report, stripped, path)
                    add_res_section_module_check(report, stripped, path)

                elif re.findall(Regex.ASSEMBLY_TYPE, stripped):
                    add_res_section_assembly_check(report, stripped, path)

                else:
                    undetermined_file_type.append(path)

            if path in prefix_assembly:
                if re.findall(Regex.MODULE_TYPE, stripped):
                    confused_files.append(path)
                    nesting_in_modules_check(report, stripped, path)
                    add_res_section_module_check(report, stripped, path)
                else:
                    add_res_section_assembly_check(report, stripped, path)

            if path in prefix_modules:
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
    """Execute yml and general validation and report errors."""
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
