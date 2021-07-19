#!/usr/libexec/platform-python

import glob
import os
import yaml
import re


# Check if the current working tree contains a pantheon2.yml file
def get_yaml_file():
    path_components = os.getcwd().split(os.sep)

    while path_components:
        yaml_location = os.sep.join(path_components) + os.sep + 'pantheon2.yml'
        if os.path.exists(yaml_location):
            return yaml_location

        path_components.pop()

    return None


# Count the number of assemblies and modules in a pantheon2.yml file
def count_content(yaml_file_location):

    # Initialize dictionary
    content_counts = {'assemblies': 0, 'modules': 0}

    # Parse the main YAML file
    with open(yaml_file_location + 'pantheon2.yml', 'r') as f:

        main_yaml_file = yaml.safe_load(f)

    # Count assemblies
    for assembly in main_yaml_file["assemblies"]:

        content_counts['assemblies'] += len(glob.glob(assembly))

    # Count modules
    for module in main_yaml_file["modules"]:

        content_counts['modules'] += len(glob.glob(module))

    return content_counts


# Get content subset
def get_content_subset(files):

    content_list = []

    for content_file in glob.glob(files):

        if content_file.endswith('.adoc') and content_file not in content_list:

            content_list.append(content_file)

    return(sorted(content_list, key=str.lower))


def get_files(main_yaml_file, *arguments):

    content_list = []
    content_duplicates = []
    wildcards = re.compile(r'[*?\[\]]')

    # modules and assemblies as arguments
    for argument in arguments:
        if argument not in main_yaml_file:
            continue

        for item in main_yaml_file[argument]:
            # checks if string has a wildcard to use glob.glob
            if wildcards.search(item):
                files = glob.glob(item)
            else:
                files = [item]

            for file in files:
                if file not in content_list:
                    content_list.append(file)
                else:
                    content_duplicates.append(file)
    return content_list, content_duplicates


def get_content(yaml_file_location):
    with open(yaml_file_location, 'r') as f:
        main_yaml_file = yaml.safe_load(f)
        content_list, content_duplicates = get_files(main_yaml_file, "assemblies", "modules")
    return(sorted(content_list, key=str.lower))


def get_duplicates(yaml_file_location):
    with open(yaml_file_location, 'r') as f:
        main_yaml_file = yaml.safe_load(f)
        content_list, content_duplicates = get_files(main_yaml_file, "assemblies", "modules")
    return(sorted(content_duplicates, key=str.lower))


def get_existence(content_list):
    files_found = []
    files_not_found = []

    for item in content_list:
        if os.path.exists(item):
            files_found.append(item)
        else:
            files_not_found.append(item)
    return files_found, files_not_found


def get_not_exist(content_list):
    files_found, files_not_found = get_existence(content_list)
    return(sorted(files_not_found, key=str.lower))


def get_exist(content_list):
    files_found, files_not_found = get_existence(content_list)
    return(sorted(files_found, key=str.lower))


def get_existing_modules(yaml_file_location):
    modules_found = []

    with open(yaml_file_location, 'r') as f:
        main_yaml_file = yaml.safe_load(f)
        content_list, content_duplicates = get_files(main_yaml_file, "modules")
    content_list = sorted(content_list, key=str.lower)

    for item in content_list:
        if os.path.exists(item):
            modules_found.append(item)
    return(sorted(modules_found, key=str.lower))


def get_existing_assemblies(yaml_file_location):
    assemblies_found = []

    with open(yaml_file_location, 'r') as f:
        main_yaml_file = yaml.safe_load(f)
        content_list, content_duplicates = get_files(main_yaml_file, "assemblies")
    content_list = sorted(content_list, key=str.lower)

    for item in content_list:
        if os.path.exists(item):
            assemblies_found.append(item)
    return(sorted(assemblies_found, key=str.lower))
