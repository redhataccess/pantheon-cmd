#!/usr/libexec/platform-python

import glob
import os
import yaml


# Check if the current working tree contains a pantheon2.yml file
def get_yaml_file():

    is_pantheon_repo = False

    path_components = os.getcwd().split(os.sep)

    path_base = ""

    # Iterate through the paths to PWD and see if one contains the file
    for path_component in path_components:

        path_base = path_base + path_component + os.sep

        if os.path.exists(path_base + 'pantheon2.yml'):

            is_pantheon_repo = True

            yaml_location = path_base

            break

    return yaml_location


# Count the number of assemblies and modules in a pantheon2.yml file
def count_content(yaml_file_location):

    # Initialize dictionary
    content_counts = {'assemblies': 0, 'modules': 0}

    # Parse the main YAML file
    with open(yaml_file_location + 'pantheon2.yml', 'r') as f:

        main_yaml_file = yaml.load(f)

    # Count assemblies
    for assembly in main_yaml_file["assemblies"]:

        content_counts['assemblies'] += len(glob.glob(assembly))

    # Count modules
    for module in main_yaml_file["modules"]:

        content_counts['modules'] += len(glob.glob(module))

    return content_counts
