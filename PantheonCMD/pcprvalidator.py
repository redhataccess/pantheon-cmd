#!/usr/bin/python3

from pygit2 import Repository
import subprocess
import re
from pcchecks import Regex


# get the name of the current branch
current_branch = Repository('.').head.shorthand


def get_changed_files():
    """Return a list of the files that werre change on the PR."""

    command = ("git diff --diff-filter=ACM --name-only origin/HEAD..." + current_branch + " -- '*.adoc' ':!*master.adoc'")
    process = subprocess.run(command, stdout=subprocess.PIPE, shell=True).stdout
    changed_files = process.strip().decode('utf-8').split('\n')

    return changed_files


def get_prefix_assemblies(files_found):
    """Return a sorted list of assemblies with a prefix."""
    prefix_assembly_files = []

    for file in files_found:
        if re.findall(Regex.PREFIX_ASSEMBLIES, file):
            prefix_assembly_files.append(file)

    return(sorted(prefix_assembly_files, key=str.lower))


def get_prefix_modules(files_found):
    """Return a sorted list of modules with a prefix."""
    prefix_module_files = []

    for file in files_found:
        if re.findall(Regex.PREFIX_MODULES, file):
            prefix_module_files.append(file)

    return(sorted(prefix_module_files, key=str.lower))


def get_no_prefix_files(files_found):
    """Return a list of files that have no prefix."""
    no_prefix_files = []

    for file in files_found:
        if not re.findall(Regex.PREFIX_ASSEMBLIES, file) and not re.findall(Regex.PREFIX_MODULES, file):
            no_prefix_files.append(file)

    return no_prefix_files


def get_no_prefefix_file_type(no_prefix_files):
    """Return a list of files determined to be assemblies or modules, and undetermined files."""
    no_prefix_module_type = []
    no_prefix_assembly_type = []
    undetermined_file_type = []

    for path in no_prefix_files:
        with open(path, "r") as file:
            original = file.read()
            stripped = Regex.MULTI_LINE_COMMENT.sub('', original)
            stripped = Regex.SINGLE_LINE_COMMENT.sub('', stripped)
            stripped = Regex.CODE_BLOCK_DASHES.sub('', stripped)
            stripped = Regex.CODE_BLOCK_DOTS.sub('', stripped)
            stripped = Regex.INTERNAL_IFDEF.sub('', stripped)

            if re.findall(Regex.MODULE_TYPE, stripped):
                no_prefix_module_type.append(path)

            if re.findall(Regex.INCLUDE, stripped):
                no_prefix_assembly_type.append(path)

            if not re.findall(Regex.MODULE_TYPE, stripped) and not re.findall(Regex.INCLUDE, stripped):
                undetermined_file_type.append(path)

    return no_prefix_module_type, no_prefix_assembly_type, undetermined_file_type


def get_no_prefix_modules(no_prefix_files):
    """Return a sorted list of no prefix modules."""
    no_prefix_module_type, no_prefix_assembly_type, undetermined_file_type = get_no_prefefix_file_type(no_prefix_files)

    return(sorted(no_prefix_module_type, key=str.lower))


def get_no_prefix_assemblies(no_prefix_files):
    """Return a sorted list of no prefix assemblies."""
    no_prefix_module_type, no_prefix_assembly_type, undetermined_file_type = get_no_prefefix_file_type(no_prefix_files)

    return(sorted(no_prefix_assembly_type, key=str.lower))


def get_all_modules(files_found, no_prefix_files):
    """Return a list of all modules."""
    prefix_module_files = get_prefix_modules(files_found)
    no_prefix_module_type = get_no_prefix_modules(no_prefix_files)

    return prefix_module_files + no_prefix_module_type


def get_all_assemblies(files_found, no_prefix_files):
    """Return a list of all assemblies."""
    prefix_assemblies = get_prefix_assemblies(files_found)
    no_prefix_assembly_type = get_no_prefix_assemblies(no_prefix_files)

    return prefix_assemblies + no_prefix_assembly_type


def get_undetermined_files(no_prefix_files):
    """Return a list of undetermined files."""
    no_prefix_module_type, no_prefix_assembly_type, undetermined_file_type = get_no_prefefix_file_type(no_prefix_files)

    return(sorted(undetermined_file_type, key=str.lower))
