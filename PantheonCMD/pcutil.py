#!/usr/bin/python3

import glob
import os
import re
import yaml


class PantheonRepo():
    """Class for processing information about Pantheon V2 repositories."""


    def __init__(self, repo_location):
        """Default constructor; accepts repo location and initializes YAML file location."""

        self.repo_location = repo_location
        self.yaml_file_location = repo_location + "pantheon2.yml"


    def count_content(self):
        """Counts the number of assemblies and modules in a pantheon2.yml file."""
        # Initialize dictionary
        content_counts = {'assemblies': 0, 'modules': 0}

        # Parse the main YAML file
        with open(self.yaml_file_location + 'pantheon2.yml', 'r') as f:
            yaml_file = yaml.safe_load(f)

        # Count assemblies
        for assembly in yaml_file["assemblies"]:
            content_counts['assemblies'] += len(glob.glob(assembly))

        # Count modules
        for module in yaml_file["modules"]:
            content_counts['modules'] += len(glob.glob(module))

        return content_counts


    def get_content(self):
        """Returns a sorted list of the modules and assemblies specified in a pantheon2.yml file."""
        with open(self.yaml_file_location, 'r') as f:
            yaml_file = yaml.safe_load(f)
            content_list, content_duplicates = self.get_files(yaml_file, "assemblies", "modules")

        return sorted(content_list, key=str.lower)


    def get_duplicates(self):
        """Returns duplicate entries of modules and assemblies found in a pantheon2.yml file."""
        with open(self.yaml_file_location, 'r') as f:
            yaml_file = yaml.safe_load(f)
            content_list, content_duplicates = self.get_files(yaml_file, "assemblies", "modules")

        return sorted(content_duplicates, key=str.lower)


    def get_existing_content(self, content_type):
        """Returns content found in a pantheon2.yml file that exist as files."""
        content_found = []

        with open(self.yaml_file_location, 'r') as f:
            yaml_file = yaml.safe_load(f)
            content_list, content_duplicates = self.get_files(yaml_file, content_type)
        content_list = sorted(content_list, key=str.lower)

        for item in content_list:
            if os.path.exists(item):
                content_found.append(item)

        return(sorted(content_found, key=str.lower))


    def get_files(self, main_yaml_file, *arguments):
        """Returns a sorted list of the modules and assemblies specified in a pantheon2.yml file."""
        content_files = []
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
                    if glob.glob(item):
                        content_files.append(item)
                    else:
                        content_files.append(item)
                else:
                    content_files = [item]

                for content_file in content_files:
                    if content_file not in content_list:
                        content_list.append(content_file)
                    else:
                        content_duplicates.append(content_file)
        return content_list, content_duplicates


    def get_missing_yaml_keys(self):
        key_missing = []

        with open(self.yaml_file_location, 'r') as f:
            data = yaml.safe_load(f)
            keys = data.keys()

            # check if all required keys exist in the yml file
            required_keys = (['server', 'repository', 'variants', 'assemblies', 'modules', 'resources'])
            for key in required_keys:
                if not key in keys:
                    key_missing.append(key)

        return(sorted(key_missing, key=str.lower))


def get_content_subset(content_files):
    """Returns a sorted list of modules and assemblies in arbitrary path 'content_files'."""
    content_list = []
    wildcards = re.compile(r'[*?\[\]]')

    # Handle wildcard searches - directories and sets of files
    if wildcards.search(content_files):
        expanded_file_list = glob.glob(content_files)
        if expanded_file_list:
            for expanded_file in expanded_file_list:
                if expanded_file.endswith('.adoc'):
                    if expanded_file not in content_list:
                        content_list.append(expanded_file)
    # Handle individual files
    else:
        if content_files.endswith('.adoc'):
            if content_files not in content_list:
                content_list.append(content_files)

    return sorted(content_list, key=str.lower)


def get_existence(content_list):
    """Checks whether the files specified in a set of content exist as files."""
    files_found = []
    files_not_found = []

    for item in content_list:
        if os.path.exists(item):
            files_found.append(item)
        else:
            files_not_found.append(item)

    return files_found, files_not_found


def get_not_exist(content_list):
    """Returns a sorted list of the files specified in a set of content that do not exist as files."""
    files_found, files_not_found = get_existence(content_list)

    return(sorted(files_not_found, key=str.lower))


def get_exist(content_list):
    """Returns a sorted list of the files specified in a set of content that do exist as files."""
    files_found, files_not_found = get_existence(content_list)

    return(sorted(files_found, key=str.lower))


def is_pantheon_repo():
    """Returns whether the repo is a valid Pantheon V2 repository."""

    path_components = os.getcwd().split(os.sep)
    repo_location = None

    while path_components:
        if os.path.exists(os.sep.join(path_components) + os.sep + 'pantheon2.yml'):
            repo_location = os.sep.join(path_components) + os.sep
            break
        path_components.pop()

    return repo_location
