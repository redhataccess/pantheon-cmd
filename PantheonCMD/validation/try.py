#!/usr/bin/python3

import subprocess
import re
from pcchecks import Regex


def get_adoc_files():
    command = ("find . -type f -name '*.adoc'")
    process = subprocess.run(command, stdout=subprocess.PIPE, shell=True).stdout
    adoc_files = process.strip().decode('utf-8').split('\n')

    return adoc_files



path = 'rhel-8/common-content/_attributes.adoc'

with open(path, 'r') as file:
    attribute_list = []
    for line in file:
        line = file.readline()
        if line.startswith(r':'):
            attributes = re.findall(Regex.ATTRIBUTE, line)
            for attribute in attributes:
                if attribute not in attribute_list:
                    attribute_list.append(attribute)



def get_attributes(stripped_file):
    all_attributes = []
    attributes = re.findall(Regex.ATTRIBUTE, stripped_file)
    for attribute in attributes:
        if attribute not in all_attributes:
            all_attributes.append(attribute)

    return attributes


def get_attributes_list(adoc_files_found):
    attribute_list = []

    for item in adoc_files_found:
        with open(item, 'r') as file:
            attribute_list = []

            for line in file:
                line = file.readline()
                if line.startswith(r':'):
                    attributes = re.findall(Regex.ATTRIBUTE, line)
                    for attribute in attributes:
                        if attribute not in attribute_list:
                            attribute_list.append(attribute)

    return attributes


adoc_files = get_adoc_files()
print(get_attributes_list(adoc_files))
