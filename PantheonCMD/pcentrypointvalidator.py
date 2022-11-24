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
    nonexistent_entry_point = []

    for entry in entry_point_list:
        if not os.path.isfile(entry):
            nonexistent_entry_point.append(entry)

    if nonexistent_entry_point:
        print_message(nonexistent_entry_point, 'entry point', 'does not exist in your repository')
        sys.exit(2)


def remove_attribute_files(files):
    for file in files[:]:
        itemized_path = file.split(os.sep)

        attribute_file = False

        for item in itemized_path:
            if item.startswith('_'):
                attribute_file = True
                files.remove(file)
                break

    return files


def sub_attributes_in_path(files):

    files = [re.sub(Regex.ATTRIBUTE, "**", file) for file in files]

    wildcard = re.compile(r'[*?\[\]]')
    content_files = []

    for item in files:
        if wildcard.search(item):
            expanded_items = glob.glob(item)
            if expanded_items:
                for expanded_item in expanded_items:
                    content_files.append(expanded_item)
            else:
                continue
        else:
            content_files.append(item)

    return content_files


def smth(entry_point_list):
    for entry in entry_point_list:
        path_to_entry_point = os.path.dirname(os.path.abspath(entry))

        with open(entry, 'r') as file:
            original = file.read()
            stripped = Regex.MULTI_LINE_COMMENT.sub('', original)
            stripped = Regex.SINGLE_LINE_COMMENT.sub('', stripped)

            included_files = re.findall(Regex.INCLUDED_CONTENT, stripped)

            if included_files:
                included_files = remove_attribute_files(included_files)
                included_files = sub_attributes_in_path(included_files)

            for include in included_files:
                print(include)


def validate_entry_point_files(entry_point_list):
    # exit if the provided path doesn't exist
    get_nonexisting_entry_points(entry_point_list)
    smth(entry_point_list)
