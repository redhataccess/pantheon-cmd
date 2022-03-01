#!/usr/bin/python3

import os
import sys
import yaml
from cerberus import Validator, errors
from cerberus.errors import BasicErrorHandler
from pcchecks import Regex, icons_check, toc_check, nbsp_check
from pcvalidator import Report
import glob
import re
import subprocess


class CustomErrorHandler(BasicErrorHandler):
    """Custom error messages."""
    messages = errors.BasicErrorHandler.messages.copy()
    messages[errors.REQUIRED_FIELD.code] = "key is missing"
    messages[errors.UNKNOWN_FIELD.code] = "unsupported key"
    messages[errors.NOT_NULLABLE.code] = "value can't be empty"


def printing_build_yml_error(msg, *files):
    print('\nERROR: Your build.yml contains the following files or directories that do not {}:\n'.format(msg))
    for file in files:
        if file:
            print('\t', file)


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


def get_md5sum(file_path):
    command = ("md5sum  " + file_path + " | cut -d\  -f1")
    process = subprocess.run(command, stdout=subprocess.PIPE, shell=True).stdout
    md5sum = process.strip().decode('utf-8').split('\n')

    return md5sum


def get_unique_files(files):
    md5sum_list = []
    unique_files = []

    for file in files:
        md5sum = get_md5sum(file)
        if md5sum not in md5sum_list:
            md5sum_list.append(md5sum)
            unique_files.append(file)

    return unique_files


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
        printing_build_yml_error("exist in your repository", missing_attribute_files)

    if exiting_attribute_files:
        for item in attribute_files:
            file_name = os.path.basename(item)
            file_path = os.path.dirname(item)
            if not file_path.startswith("_"):
                if "/_" not in file_path:
                    if not file_name.startswith("_"):
                        printing_build_yml_error("follow the attribute naming conventions. Attribute files or directory they are stored in should start with an undescore", item)

        attribute_validation = validate_attribute_files(exiting_attribute_files)

        if attribute_validation.count != 0:
            attribute_validation.print_report()


def get_content_list(yaml_doc):
    missing_includes = get_missing_files(yaml_doc, 'included')
    missing_excludes = get_missing_files(yaml_doc, 'excluded')

    if missing_includes or missing_excludes:
        printing_build_yml_error("exist in your repository", missing_includes, missing_excludes)

    included = get_exitsing_files(yaml_doc, 'included')
    excluded = get_exitsing_files(yaml_doc, 'excluded')

    unique_includes = get_unique_files(included)
    unique_excludes = get_unique_files(excluded)

    md5sum_exc_list = []
    unique_files = []

    for item in unique_excludes:
        md5sum_exc = get_md5sum(item)
        md5sum_exc_list.append(md5sum_exc)

    for item in unique_includes:
        md5sum_inc = get_md5sum(item)
        if md5sum_inc not in md5sum_exc_list:
            unique_files.append(item)

    return unique_files


def sort_content_list(yaml_doc):
    prefix_assembly = []
    prefix_modules = []
    unidentifiyed_content = []

    content_list = get_content_list(yaml_doc)

    for item in content_list:
        if item.endswith('.adoc'):
            file_name = os.path.basename(item)
            if file_name.startswith('assembly'):
                prefix_assembly.append(item)
            elif file_name.startswith(("proc_", "con_", "ref_", "proc-", "con-", "ref-")):
                prefix_modules.append(item)
            else:
                unidentifiyed_content.append(item)

    return prefix_assembly, prefix_modules, unidentifiyed_content


def yaml_validation(yaml_file):
    """Validate build.yml; get path to attributes while we're at it."""
    # define path to script
    path_to_script = os.path.dirname(os.path.realpath(__file__))
    # load schema
    schema = eval(open(path_to_script + '/schema.py', 'r').read())
    # load build.yml
    loaded_yaml = load_doc(yaml_file)

    get_yaml_size(yaml_file)
    get_yaml_errors(schema, loaded_yaml)
    get_attribute_file_errors(loaded_yaml)

    sort_content_list(loaded_yaml)
