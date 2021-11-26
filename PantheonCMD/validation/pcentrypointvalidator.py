#!/usr/bin/python3

import argparse
import re
import os
from validation.pcchecks import Regex
import sys
from pcutil import get_exist, get_not_exist
from validation.pcprvalidator import get_no_prefix_files, get_all_modules, get_all_assemblies, get_undetermined_files
from validation.pcvalidator import validation
from validation.pcmsg import print_message, print_report_message

parser = argparse.ArgumentParser()


def get_nonexisting_entry_points(entry_point_list):
    nonexistent_files = get_not_exist(entry_point_list)

    if nonexistent_files:
        print_message(nonexistent_files, 'entry point', 'does not exist in your repository')
        sys.exit(2)


def get_includes(entry_points):
    path_to_includes = []

    for entry in entry_points:
        path_to_entry_point = os.path.dirname(os.path.abspath(entry))

        with open(entry, 'r') as file:
            original = file.read()
            stripped = Regex.MULTI_LINE_COMMENT.sub('', original)
            stripped = Regex.SINGLE_LINE_COMMENT.sub('', stripped)

            included_files = re.findall(Regex.INCLUDED_CONTENT, stripped)

            if included_files:

                for include in included_files[:]:
                    if include.startswith('_'):
                        included_files.remove(include)

                for i in included_files:
                    path_to_includes.append(os.path.join(path_to_entry_point, i))

    return path_to_includes


def get_level_one_includes(files):
    path_to_level_one_includes = get_includes(files)

    return path_to_level_one_includes


def get_level_two_includes(files):
    path_to_level_two_includes = get_includes(files)

    return path_to_level_two_includes


def get_level_three_includes(files):
    path_to_level_three_includes = get_includes(files)

    return path_to_level_three_includes


def get_level_four_includes(files):
    path_to_level_four_includes = get_includes(files)

    return path_to_level_four_includes


def get_concatenated_includes(entry_point_list):
    existing_entry_points = get_exist(entry_point_list)
    level_one_includes = get_level_one_includes(existing_entry_points)
    level_two_includes = get_level_two_includes(level_one_includes)
    level_three_includes = get_level_three_includes(level_two_includes)
    level_four_includes = get_level_four_includes(level_three_includes)
    no_prefix_level_four_includes = get_no_prefix_files(level_four_includes)
    level_four_modules = get_all_modules(level_four_includes, no_prefix_level_four_includes)
    level_four_assemblies = get_all_assemblies(level_four_includes, no_prefix_level_four_includes)

    all_includes = level_one_includes + level_two_includes + level_three_includes + level_four_modules

    return all_includes, level_four_assemblies


def get_level_four_assemblies(entry_point_list):
    all_includes, level_four_assemblies = get_concatenated_includes(entry_point_list)

    return level_four_assemblies


def get_all_includes(entry_point_list):
    all_includes, level_four_assemblies = get_concatenated_includes(entry_point_list)

    for entry in entry_point_list:
        if not entry.endswith('master.adoc'):
            all_includes = all_includes + entry_point_list

    for include in all_includes:
        if os.path.basename(include).startswith('_'):
            all_includes.remove(include)

    return all_includes


def validate_entry_point_files(entry_point_list):
    # exit if entry point doesn't exist
    get_nonexisting_entry_points(entry_point_list)
    existing_entry_points = get_exist(entry_point_list)
    includes = get_all_includes(entry_point_list)
    no_prefix_files = get_no_prefix_files(includes)
    modules_found = get_all_modules(includes, no_prefix_files)
    assemblies_found = get_all_assemblies(includes, no_prefix_files)
    undetermined_file_type = get_undetermined_files(no_prefix_files)
    level_four_assemblies = get_level_four_assemblies(existing_entry_points)

    if level_four_assemblies:
        print_message(level_four_assemblies, 'entry point', 'contains unsupported level of nesting for the following files')

    if undetermined_file_type:
        print_message(undetermined_file_type, 'entry point', 'contains the following files that can not be classified as modules or assemblies')

    validate = validation(includes, modules_found, assemblies_found)
    print_report_message(validate, 'entry point')
