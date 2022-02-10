#!/usr/bin/python3

import re
import os
import subprocess
from pcchecks import Regex
from pcmsg import Report, print_report_message


def get_modules():
    command = ("find rhel-8/modules/identity-management/ -type f -name '*.adoc'")
    process = subprocess.run(command, stdout=subprocess.PIPE, shell=True).stdout
    modules = process.strip().decode('utf-8').split('\n')

    return modules


def validate_nesting(modules_found):
    nesting_prefix = []
    nesting_no_prefix = []

    for path in modules_found:
        with open(path, "r") as file:
            original = file.read()
            stripped = Regex.MULTI_LINE_COMMENT.sub('', original)
            stripped = Regex.SINGLE_LINE_COMMENT.sub('', stripped)

            includes = re.findall(Regex.INCLUDED_CONTENT, stripped)

            if includes:
                for item in includes:
                    filename = os.path.basename(item)
                    if filename.startswith(("assembly", "con", "proc", "ref")):
                        nesting_prefix.append(path)
                    else:
                        path_to_include = os.path.dirname(path)
                        item = path_to_include + '/' + item

                        with open(item, 'r') as file:
                            original = file.read()
                            stripped = Regex.MULTI_LINE_COMMENT.sub('', original)
                            stripped = Regex.SINGLE_LINE_COMMENT.sub('', stripped)

                            if re.findall(Regex.CONTENT_TYPE, stripped):
                                nesting_no_prefix.append(path)

    return nesting_prefix + nesting_no_prefix


def get_unique_nested_content(report, modules_found):
    unique_nested_content = []

    nested_content = validate_nesting(modules_found)

    for item in nested_content:
        if item not in unique_nested_content:
            unique_nested_content.append(item)

            report.create_report('nesting in modules. nesting', item)


def validate_modules():
    report = Report()
    modules = get_modules()
    get_unique_nested_content(report, modules)

    return report


def trytry():
    a = validate_modules()
    print_report_message(a, 'pantheon2.yml')


trytry()
