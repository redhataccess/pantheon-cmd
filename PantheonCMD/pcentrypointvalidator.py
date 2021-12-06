#!/usr/bin/python3

from pcutil import get_not_exist
from pcmsg import print_message
import sys
import os
import re
from pcchecks import Regex
from pcprvalidator import get_all_assemblies, get_all_modules, get_no_prefix_files, get_undetermined_files
import glob


from pcmsg import print_report_message
from pcvalidator import validation


def get_nonexisting_entry_points(entry_point_list):
    nonexistent_files = get_not_exist(entry_point_list)

    if nonexistent_files:
        print_message(nonexistent_files, 'entry point', 'does not exist in your repository')
        sys.exit(2)


def get_full_path_to_includes_with_attributes(files):
    wildcard_sub = []
    full_path = []

    for item in files:
        attribute = re.findall(Regex.ATTRIBUTE, item)
        if attribute:
            replace = re.sub(Regex.ATTRIBUTE, "**", item)

            wildcard_sub.append(replace)

    for i in wildcard_sub:
        full_path.append(glob.glob(i, recursive=True))

    return full_path


def get_unique_entries(list):
    unique = []

    for i in list:
        if not unique:
            unique.append(i)
        else:
            for x in unique:
                if not os.path.samefile(i, x):
                    unique.append(i)

    return unique


def get_includes(files):
    """Retreives full paths to included files from an entry point."""
    includes_with_attributes = []
    path_to_includes = []
    path_to_includes_with_attributes = []
    includes_found = []
    includes_not_found = {}
    unique_entries_includes_with_attributes = []

    for entry in files:
        path_to_entry_point = os.path.dirname(os.path.abspath(entry))

        # check existence

        with open(entry, 'r') as file:
            original = file.read()
            stripped = Regex.MULTI_LINE_COMMENT.sub('', original)
            stripped = Regex.SINGLE_LINE_COMMENT.sub('', stripped)

            included_files = re.findall(Regex.INCLUDED_CONTENT, stripped)

            if included_files:

                for include in included_files[:]:
                    itemized_path = include.split(os.sep)

                    attribute_in_path = False
                    attribute_file = False

                    for item in itemized_path:
                        if item.startswith('_'):
                            attribute_file = True
                            included_files.remove(include)
                            break
                        if item.startswith('{'):
                            attribute_in_path = True
                            included_files.remove(include)
                            includes_with_attributes.append(include)
                            break

                for include in included_files:
                    full_path = os.path.join(path_to_entry_point, include)
                    if os.path.exists(full_path):
                        includes_found.append(full_path)
                    else:
                        includes_not_found.setdefault(entry, {})[include] = 1

    for include in includes_with_attributes:
        path_to_includes_with_attributes.append(os.path.join(path_to_entry_point, include))

    path_to_includes_with_attributes = get_full_path_to_includes_with_attributes(path_to_includes_with_attributes)

    for i in path_to_includes_with_attributes:
        unique_entries_includes_with_attributes.append(get_unique_entries(i))

    return includes_found, includes_not_found, unique_entries_includes_with_attributes


def get_includes_recursively(files):

    lvl_1_includes_found, lvl_1_includes_not_found, lvl_1_includes_with_attributes = get_includes(files)

    lvl_2_includes_found, lvl_2_includes_not_found, lvl_2_includes_with_attributes = get_includes(lvl_1_includes_found)

    lvl_3_includes_found, lvl_3_includes_not_found, lvl_3_includes_with_attributes = get_includes(lvl_2_includes_found)

    lvl_4_includes_found, lvl_4_includes_not_found, lvl_4_includes_with_attributes = get_includes(lvl_3_includes_found)

    includes_found = lvl_1_includes_found + lvl_2_includes_found + lvl_3_includes_found + lvl_4_includes_found

    #includes_not_found = lvl_1_includes_not_found + lvl_2_includes_not_found + lvl_3_includes_not_found + lvl_3_includes_not_found + lvl_4_includes_not_found

    includes_not_found = {**lvl_1_includes_not_found , **lvl_2_includes_not_found, **lvl_3_includes_not_found, **lvl_4_includes_not_found}

    includes_with_attributes = lvl_1_includes_with_attributes + lvl_2_includes_with_attributes + lvl_3_includes_with_attributes + lvl_4_includes_with_attributes
    includes_with_attributes = [j for i in includes_with_attributes for j in i]

    for i in includes_with_attributes:
        print(type(i))

    # only valid for entry point
    for file in files:
        file_name = os.path.basename(file)
        if not file_name == 'master.adoc':
            includes_found.append(file)

    return includes_found, includes_not_found, includes_with_attributes


def validate_entry_point_files(entry_point_list):
    get_nonexisting_entry_points(entry_point_list)

    all_includes_found, all_includes_not_found, all_includes_with_attributes = get_includes_recursively(entry_point_list)

    no_prefix_files = get_no_prefix_files(all_includes_found)

    all_assemblies = get_all_assemblies(all_includes_found, no_prefix_files)
    all_modules = get_all_modules(all_includes_found, no_prefix_files)
    all_undetermined_files = get_undetermined_files(no_prefix_files)

    if all_includes_not_found:
        for key, value in all_includes_not_found.items():
            print(f'{os.path.basename(key)} contains the following includes that do not exist in your repository:')
            for v in value:
                print('\t', v)

    validate = validation(all_includes_found, all_modules, all_assemblies)

    print_report_message(validate, 'entry point')
