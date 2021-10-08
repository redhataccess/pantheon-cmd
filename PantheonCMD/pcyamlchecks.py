#!/usr/bin/python3

import os
import sys
import glob
import re
import yaml
import pprint
from cerberus import Validator, errors
from cerberus.errors import BasicErrorHandler
from pcchecks import Regex, icons_check, toc_check
from pcvalidator import Report


class CustomErrorHandler(BasicErrorHandler):
    """Custom error messages."""
    messages = errors.BasicErrorHandler.messages.copy()
    messages[errors.REQUIRED_FIELD.code] = "key is missing"
    messages[errors.UNKNOWN_FIELD.code] = "unsupported key"
    messages[errors.NOT_NULLABLE.code] = "value can't be empty"


class Printing():

    def __init__(self):
        self.report = {}
        self.count = 0

    def create_report(self, message, items):
        """Generate report."""
        self.count += 1
        if not message in self.report:
            self.report[message] = []
        self.report[message].append(items)

    def print_report(self):
        separator = "\n\t"

        for message, items in self.report.items():
            print('\nFAIL: {} contains the following files or directories that do not exist in your repository:\n'.format(message))
            for item in items:
                print('\t' + separator.join(item))


def get_yaml_size(yaml_file):
    """Test if pv2.yml is empty."""
    if os.path.getsize(yaml_file) == 0:
        print("\nYour {} file is empty; exiting...".format(yaml_file))
        sys.exit(2)


def load_doc(yaml_file):
    """Load pv2.yml and test for syntax errors."""
    with open(yaml_file, 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError:
            print("There's a syntax error in your {0} file. Please fix it and try again.\nTo detect an error try running yaml lint on your {0} file.".format(yaml_file))
            sys.exit(2)


def get_yaml_errors(yaml_schema, yaml_doc, path):
    # load validator with custom error handler
    v = Validator(yaml_schema, error_handler=CustomErrorHandler())
    # validate the pv2.yml with schema
    v.validate(yaml_doc, yaml_schema)

    if v.errors:
        print("\nFAIL: there is an error in your {} file:".format(path))
        for key in v.errors.keys():
            print("\n\t'{}' {}".format(key, ', '.join(str(item) for item in v.errors[key])))
            sys.exit(2)


def get_resources_existence(yaml_doc):
    path_does_not_exist = []

    for item in yaml_doc['resources']:
        path_to_images_dir = os.path.split(item)[0]
        if not glob.glob(path_to_images_dir):
            path_does_not_exist.append(item)

    if path_does_not_exist:
        print('\nFAIL: Your pantheon2.yml contains the following files or directories that do not exist in your repository:\n')
        for path in path_does_not_exist:
            print('\t', path)
        sys.exit(2)


def get_variants_yaml(yaml_doc):
    variants_do_not_exist = []
    variants_exist = []

    for item in yaml_doc['variants']:
        if not glob.glob(item):
            variants_do_not_exist.append(item)
            print('\nFAIL: {} contains the following files or directories that do not exist in your repository:\n'.format('variants yaml'))
            for path in variants_do_not_exist:
                print('\t', path)
            sys.exit(2)

        else:
            for path in glob.glob(item):
                variants_exist.append(path)

    return variants_exist


def get_attribute_files(var_yaml_doc):
    path_does_not_exist = []
    path_exists = []

    for item in var_yaml_doc['path']:
        if not os.path.exists(item):
            path_does_not_exist.append(item)
            print('\nFAIL: {} contains the following files or directories that do not exist in your repository:\n'.format('variants yaml'))
            for path in path_does_not_exist:
                print('\t', path)
            sys.exit(2)
        else:
            path_exists.append(item)

    return path_exists


def get_variant_attribute_path(yaml_var_doc):
    path_does_not_exist = []
    path_exists = []

    for item in yaml_var_doc['path']:
        if not os.path.exists(item):
            path_does_not_exist.append(item)
        else:
            path_exists.append(item)

    if path_does_not_exist:
        print('\nFAIL: Your {} contains the following files or directories that do not exist in your repository:\n'.format('variants yaml'))
        for path in path_does_not_exist:
            print('\t', path)
        sys.exit(2)
    else:
        attribute_file_validation = get_attribute_file_validation_results(path_exists)
        if attribute_file_validation.count != 0:
            print("\nYour attributes file has the following errors:\n")
            attribute_file_validation.print_report()
        else:
            return path_exists


def get_attribute_file_validation(attribute_file):
    """Validate attributes file."""
    report = Report()
    attributes = []

    for path in attribute_file:
        with open(path, 'r') as file:
            original = file.read()
            stripped = Regex.MULTI_LINE_COMMENT.sub('', original)
            stripped = Regex.SINGLE_LINE_COMMENT.sub('', stripped)

            icons_check(report, stripped, path)
            toc_check(report, stripped, path)

        with open(path, 'r') as file:
            attributes.append(parse_attributes(file.readlines()))

    return report, attributes


def get_attribute_file_validation_results(attribute_file):
    report, attributes = get_attribute_file_validation(attribute_file)

    return report


def get_attributes(attribute_file):
    report, attributes = get_attribute_file_validation(attribute_file)

    return attributes


def yaml_validation(yaml_file):
    """Validate pv2.yml; get path to attributes while we're at it."""
    # define path to script
    path_to_script = os.path.dirname(os.path.realpath(__file__))
    # load schema
    schema = eval(open(path_to_script + '/schema.py', 'r').read())
    # load pv2.yml
    loaded_yaml = load_doc(yaml_file)

    get_yaml_size(yaml_file)
    get_yaml_errors(schema, loaded_yaml, yaml_file)
    get_resources_existence(loaded_yaml)


def parse_attributes(attributes):
    """Read an attributes file and parse values into a key:value dictionary."""

    final_attributes = {}

    for line in attributes:
        if re.match(r'^:\S+:.*', line):
            attribute_name = line.split(":")[1].strip()
            attribute_value = line.split(":")[2].strip()
            final_attributes[attribute_name] = attribute_value

    return final_attributes


def variant_yaml_validation(yaml_file):
    # define path to script
    path_to_script = os.path.dirname(os.path.realpath(__file__))
    loaded_yaml = load_doc(yaml_file)
    var_yaml = get_variants_yaml(loaded_yaml)
    schema2 = eval(open(path_to_script + '/schemavar.py', 'r').read())

    variant_yaml_files = get_variants_yaml(loaded_yaml)

    result = {}

    for item in variant_yaml_files:
        get_yaml_size(item)

        with open(item, 'r') as file:
            try:
                var_yaml = yaml.safe_load(file)

                get_yaml_errors(schema2, var_yaml, item)
                attributes_exist = get_variant_attribute_path(var_yaml)

                if attributes_exist:
                    result[item] = get_attributes(attributes_exist)

            except yaml.YAMLError:
                print("There's a syntax error in your {0} file. Please fix it and try again.\nTo detect an error try running yaml lint on your {0} file.".format(item))
                sys.exit(2)

    return result


pattern = re.compile('\{([^}]+)\}')

original = variant_yaml_validation('/home/levi/rhel-8-docs/pantheon2.yml')


pattern = re.compile('\{([^}]+)\}')


def resolve_attributes(text, dictionary):
    while True:
        attributes = pattern.findall(text)

        if not any(key in dictionary for key in attributes):
            return text

        for attribute in attributes:
            if attribute in dictionary:
                text = text.replace(f'{{{attribute}}}', dictionary[attribute])


def resolve_dictionary(dictionary):
    result = {}

    for key, value in dictionary.items():
        result[key] = resolve_attributes(value, dictionary)

    return result


def resolve_all(dictionary):
    result = {}

    for yml_file, items in dictionary.items():
        new_items = []

        for i in items:
            new_items.append(resolve_dictionary(i))

        result[yml_file] = new_items

    return result


'''pp = pprint.PrettyPrinter(width=41, compact=True)
pp.pprint(resolve_all(original))'''
