#!/usr/bin/python3

import glob
import os
import re
import yaml


# Check if the current working tree contains a pantheon2.yml file
def get_yaml_file():
    path_components = os.getcwd().split(os.sep)

class PantheonRepo():
    """Class for processing information about Pantheon V2 repositories."""


    def __init__(self):
        """Default constructor; finds pantheon2.yml, if any."""

        self.repo_location = None

        path_components = os.getcwd().split(os.sep)

        while path_components:
            self.repo_location = os.sep.join(path_components) + os.sep
            if os.path.exists(self.repo_location + 'pantheon2.yml'):
                break
            path_components.pop()

        self.yaml_file_location = '' if self.repo_location == None else self.repo_location + 'pantheon2.yml'


    def is_pantheon_repo(self):
        """Returns whether the repo is a valid Pantheon V2 repository."""
        return False if self.repo_location == None else True


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


    def get_files(self, main_yaml_file, *arguments):
        """Returns a sorted list of the modules and assemblies specified in a pantheon2.yml file."""
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
                    content_files = glob.glob(item)
                else:
                    content_files = [item]

                for content_file in content_files:
                    if content_file not in content_list:
                        content_list.append(content_file)
                    else:
                        content_duplicates.append(content_file)
        return content_list, content_duplicates


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

    def get_existing_modules(self):
        """Returns modules found in a pantheon2.yml file that exist as files."""
        modules_found = []

        with open(self.yaml_file_location, 'r') as f:
            yaml_file = yaml.safe_load(f)
            content_list, content_duplicates = self.get_files(yaml_file, "modules")
        content_list = sorted(content_list, key=str.lower)

        for item in content_list:
            if os.path.exists(item):
                modules_found.append(item)

        return(sorted(modules_found, key=str.lower))


    def get_existing_assemblies(self):
        """Returns assemblies found in a pantheon2.yml file that exist as files."""
        assemblies_found = []

        with open(self.yaml_file_location, 'r') as f:
            yaml_file = yaml.safe_load(f)
            content_list, content_duplicates = self.get_files(yaml_file, "assemblies")
        content_list = sorted(content_list, key=str.lower)

        for item in content_list:
            if os.path.exists(item):
                assemblies_found.append(item)

        return(sorted(assemblies_found, key=str.lower))


def get_content_subset(content_files):
    """Returns a sorted list of modules and assemblies in arbitrary path 'content_files'."""
    content_list = []

    for content_file in glob.glob(content_files):
        if content_file.endswith('.adoc') and content_file not in content_list:
            content_list.append(content_file)

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
