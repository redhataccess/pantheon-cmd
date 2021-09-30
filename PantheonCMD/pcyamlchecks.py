#!/usr/bin/python3

import os
import yaml
import sys
import glob


def get_yaml_size(yaml_file):
    """Check the size of the yaml file"""
    if os.path.getsize(yaml_file) == 0:
        return True


def get_yaml_syntax_errors(yaml_file):
    """Check the syntax of the yaml file"""

    with open(yaml_file, 'r') as file:

        try:
            yaml.safe_load(file)
        except yaml.YAMLError:
            return True


def get_missing_yaml_keys(yaml_file):
    empty_keys = []
    missing_key = []
    missing_variant_keys = []
    missing_variant_value = []
    path_does_not_exist = []
    path_exists = []

    required_keys = (['server', 'repository', 'variants', 'assemblies', 'modules', 'resources'])
    required_variant_keys = (['name', 'path', 'canonical'])

    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)
        keys = data.keys()

        for key in required_keys:
            if key not in keys:
                missing_key.append(key)
            else:
                if data[key] is None:
                    empty_keys.append(key)

        if 'resources' in keys:
            if data['resources'] is not None:
                for item in data['resources']:
                    path_to_images_dir = os.path.split(item)[0]
                    if not glob.glob(path_to_images_dir):
                        path_does_not_exist.append(item)

        itemized_required_keys = []
        existing_variant_keys = []
        itemized_existing_variant_keys = []

        if 'variants' in keys:
            if data['variants'] is not None:
                for variant_key in required_variant_keys:
                    itemized_required_keys.append(variant_key)

                    for variant in data['variants']:
                        existing_variant_keys.append(variant)

                        if variant[variant_key] is None:
                            missing_variant_value.append(variant_key)

                        if variant['path'] is not None:

                            if not os.path.exists(variant['path']):
                                path_does_not_exist.append(variant['path'])
                            else:
                                path_exists.append(variant['path'])

                for item in existing_variant_keys:
                    for i in item:
                        itemized_existing_variant_keys.append(i)

                for item in itemized_required_keys:
                    if item not in itemized_existing_variant_keys:
                        missing_variant_keys.append(item)

    return missing_key, empty_keys, missing_variant_keys, missing_variant_value, path_does_not_exist, path_exists


def checks(yaml_file, report):
    missing_keys, empty_keys, missing_variant_keys, missing_variant_value, path_does_not_exist, path_exists = get_missing_yaml_keys(yaml_file)

    if missing_keys:
        report.create_report('file is missing the following keys', missing_keys)

    if empty_keys:
        report.create_report('file is missing the following values', empty_keys)


    if missing_variant_keys:
        report.create_report('file is missing the following keys under "variants"', missing_variant_keys)


    if missing_variant_value:
        report.create_report('file is missing the following keys under "variants"', missing_variant_value)


    if path_does_not_exist:
        report.create_report('file contains the following file or directory that doesn not exist in your repository"', path_does_not_exist)





def get_missing_keys(yaml_file, report):
    """Return missing keys."""
    missing_keys, empty_keys, missing_variant_keys, missing_variant_value, path_does_not_exist, path_exists = get_missing_yaml_keys(yaml_file)

    if missing_keys:
        report.create_report('file is missing the following keys', missing_keys)


def get_empty_values(yaml_file, report):
    """Return empty keys."""
    missing_keys, empty_keys, missing_variant_keys, missing_variant_value, path_does_not_exist, path_exists = get_missing_yaml_keys(yaml_file)

    if empty_keys:
        report.create_report('file is missing the following values', empty_keys)


def get_missing_variant_keys(yaml_file, report):
    """Return missing variant keys."""
    missing_keys, empty_keys, missing_variant_keys, missing_variant_value, path_does_not_exist, path_exists = get_missing_yaml_keys(yaml_file)

    if missing_variant_keys:
        report.create_report('file is missing the following keys under "variants"', missing_variant_keys)


def get_missing_variant_value(yaml_file, report):
    """Return missing variant values."""
    missing_keys, empty_keys, missing_variant_keys, missing_variant_value, path_does_not_exist, path_exists = get_missing_yaml_keys(yaml_file)

    if missing_variant_value:
        report.create_report('file is missing the following values under "variants"', missing_variant_value)


def get_nonexistent_path(yaml_file, report):
    """Return wrong path."""
    missing_keys, empty_keys, missing_variant_keys, missing_variant_value, path_does_not_exist, path_exists = get_missing_yaml_keys(yaml_file)

    if path_does_not_exist:
        report.create_report('file contains the following file or directory that doesn not exist in your repository', path_does_not_exist)
