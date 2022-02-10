#!/usr/bin/python3

import subprocess
from validation.pcmsg import Report, print_report_message
from validation.pcentrypointvalidator import get_exist, get_level_four_assemblies


def get_assemblies():
    command = ("find rhel-8/assemblies/ -type f -name '*.adoc'")
    process = subprocess.run(command, stdout=subprocess.PIPE, shell=True).stdout
    assemblie = process.strip().decode('utf-8').split('\n')

    return assemblie


def validate_nesting(report, assemblie_found):
    existing_entry_points = get_exist(assemblie_found)
    level_four_assemblies = get_level_four_assemblies(existing_entry_points)

    for item in level_four_assemblies:
        report.create_report('nesting in assemblies. nesting', item)


def validate_assemblies():
    report = Report()
    assemblies = get_assemblies()
    validate_nesting(report, assemblies)

    return report


def trytry():
    a = validate_assemblies()
    print_report_message(a, 'pantheon2.yml')


trytry()
