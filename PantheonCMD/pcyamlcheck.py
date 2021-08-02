#!/usr/bin/python3

import os
import yaml
from pcutil import PantheonRepo


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
            print("\nFAIL: the following {}:".format(message))
            for item in items:
                print('\t' + separator.join(item))


def empty_key_check(report, yaml_file, keys):
    empty_keys = []

    for key in keys:
        if yaml_file[key] == None:
            empty_keys.append(key)
    if empty_keys:
        report.create_report('values are empty', sorted(empty_keys, key=str.lower))


def path_to_images_dir_check(report, yaml_file):
    false_dir = []

    for item in (yaml_file['resources']):
        path_to_images_dir = os.path.split(item)[0]
        if not os.path.exists(path_to_images_dir):
            false_dir.append(path_to_images_dir)
    if false_dir:
        report.create_report('files or directories do not exist in your repository', sorted(false_dir, key=str.lower))


def variant_values_check(report, yaml_file, required_values):
    varriant_values_none = []
    cannonical_is_not_true = []
    path_does_not_exist = []

    for variant_values in yaml_file['variants']:
        for item in required_values:
            if variant_values[item] == None:
                varriant_values_none.append(item)
                report.create_report('values are empty', sorted(varriant_values_none, key=str.lower))

        if variant_values['canonical'] != None:
            if variant_values['canonical'] != True:
                cannonical_is_not_true.append('cannonical')
                report.create_report('value is not set to True', sorted(cannonical_is_not_true, key=str.lower))

        if variant_values['path'] != None:
            if not os.path.exists(variant_values['path']):
                path_does_not_exist.append(variant_values['path'])
                report.create_report('files or directories do not exist in your repository', path_does_not_exist)


def yaml_validator(self):
    report = Printing()

    with open(self.yaml_file_location, 'r') as f:
        data = yaml.safe_load(f)

        required_keys = (['server', 'repository', 'variants', 'assemblies', 'modules', 'resources'])

        required_variant_values = (['name', 'path', 'canonical'])

        empty_key_check(report, data, required_keys)
        path_to_images_dir_check(report, data)
        variant_values_check(report, data, required_variant_values)

    return report
