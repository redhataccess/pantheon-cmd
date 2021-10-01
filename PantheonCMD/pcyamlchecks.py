#!/usr/bin/python3

import os
import sys
import yaml
from cerberus import Validator, errors
from cerberus.errors import BasicErrorHandler
from pcchecks import Regex, icons_check, toc_check
from pcvalidator import Report
import glob


class CustomErrorHandler(BasicErrorHandler):
    """Custom error messages."""
    messages = errors.BasicErrorHandler.messages.copy()
    messages[errors.REQUIRED_FIELD.code] = "key is missing"
    messages[errors.UNKNOWN_FIELD.code] = "unsupported key"
    messages[errors.NOT_NULLABLE.code] = "value can't be empty"


def get_yaml_size(yaml_file):
    """Test if pv2.yml is empty."""
    if os.path.getsize(yaml_file) == 0:
        print("\nYour pantheon2.yml file is empty; exiting...")
        sys.exit(2)


def load_doc(yaml_file):
    """Load pv2.yml and test for syntax errors."""
    with open(yaml_file, 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError:
            print("There's a syntax error in your pantheon2.yml file. Please fix it and try again.\nTo detect an error try running yaml lint on your pantheo2.yml file.")
            sys.exit(2)


def get_attribute_file_validation_results(attribute_file):
    """Validate attributes file."""
    report = Report()

    for path in attribute_file:
        with open(path, 'r') as file:
            original = file.read()
            stripped = Regex.MULTI_LINE_COMMENT.sub('', original)
            stripped = Regex.SINGLE_LINE_COMMENT.sub('', stripped)
            stripped = Regex.CODE_BLOCK_DASHES.sub('', stripped)
            stripped = Regex.CODE_BLOCK_DOTS.sub('', stripped)
            stripped = Regex.INTERNAL_IFDEF.sub('', stripped)

            icons_check(report, stripped, path)
            toc_check(report, stripped, path)

    return report


def get_yaml_errors(yaml_schema, yaml_doc):

    # load validator with custom error handler
    v = Validator(yaml_schema, error_handler=CustomErrorHandler())

    # validate the pv2.yml with schema
    v.validate(yaml_doc, yaml_schema)

    if v.errors:
        print("\nFAIL: there is an error in your yaml file:")
        for key in v.errors.keys():
            print("\n\t'{}' {}".format(key, ', '.join(str(item) for item in v.errors[key])))
        sys.exit(2)

    else:

        path_does_not_exist = []
        path_exists = []

        for item in yaml_doc['resources']:
            path_to_images_dir = os.path.split(item)[0]
            if not glob.glob(path_to_images_dir):
                path_does_not_exist.append(item)

        for variant in yaml_doc['variants']:
            if not os.path.exists(variant['path']):
                path_does_not_exist.append(variant['path'])
            else:
                path_exists.append(variant['path'])

    if path_does_not_exist:
        print('\nFAIL: Your pantheon2.yml contains the following files or directories that do not exist in your repository:\n')
        for path in path_does_not_exist:
            print('\t', path)
        sys.exit(2)
    else:
        attribute_file_validation = get_attribute_file_validation_results(path_exists)
        if attribute_file_validation.count != 0:
            print("\nYour attributes file has the following errors:\n")
            attribute_file_validation.print_report()


def yaml_validation(pv2_yaml_file):
    """Validate pv2.yml; get path to attributes while we're at it."""
    # define path to script
    path_to_script = os.path.dirname(os.path.realpath(__file__))
    # load schema
    schema = eval(open(path_to_script + '/schema.py', 'r').read())
    # load pv2.yml
    loaded_yaml = load_doc(pv2_yaml_file)

    get_yaml_size(pv2_yaml_file)
    get_yaml_errors(schema, loaded_yaml)
