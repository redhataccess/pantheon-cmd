#!/usr/libexec/platform-python

import glob
import os
import yaml


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


def get_files(yaml_file_location):

    content_list = []
    content_duplicates = []

    with open(yaml_file_location, 'r') as f:

        main_yaml_file = yaml.safe_load(f)

    # Generate unique list of assemblies
    if "assemblies" in main_yaml_file:

        for assembly in main_yaml_file["assemblies"]:

            for assembly_file in glob.glob(assembly):

                if assembly_file not in content_list:

                    content_list.append(assembly_file)

                else:

                    content_duplicates.append(assembly_file)

    # Generate unique list of modules
    if "modules" in main_yaml_file:

        for module in main_yaml_file["modules"]:

            for module_file in glob.glob(module):

                if module_file not in content_list:

                    content_list.append(module_file)

                else:

                    content_duplicates.append(module_file)

    return content_list, content_duplicates


def get_content(yaml_file_location):
    content_list, content_duplicates = get_files(yaml_file_location)
    return(sorted(content_list, key=str.lower))


def get_duplicates(yaml_file_location):
    content_list, content_duplicates = get_files(yaml_file_location)
    return(sorted(content_duplicates, key=str.lower))
