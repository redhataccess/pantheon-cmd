#!/usr/bin/python3

import subprocess
import os
import sys
import re
from pcchecks import Regex
from pcvalidator import validation
from pcmsg import print_message, print_report_message
from pcutil import get_exist


if subprocess.call(["git", "branch"], stderr=subprocess.STDOUT, stdout=open(os.devnull, 'w')) != 0:
    print('Not a git repository; existing...')
    sys.exit(1)
else:
    command = ("git rev-parse --abbrev-ref HEAD")
    process = subprocess.run(command, stdout=subprocess.PIPE, shell=True).stdout
    current_branch = process.strip().decode('utf-8').split('\n')
    current_branch = ' '.join([str(elem) for elem in current_branch])


def get_mr():
    if current_branch == 'master':
        print('On master. Exiting...')
        sys.exit(1)
    elif current_branch == 'main':
        print('On main. Exiting...')
        sys.exit(1)


def get_changed_files():
    """Return a list of the files that werre change on the PR."""

    command = ("git diff --diff-filter=ACM --name-only origin/HEAD..." + str(current_branch) + " -- ':!*master.adoc' | xargs -I '{}' realpath --relative-to=. $(git rev-parse --show-toplevel)/'{}' | grep '.*\.adoc'")
    process = subprocess.run(command, stdout=subprocess.PIPE, shell=True).stdout
    changed_files = process.strip().decode('utf-8').split('\n')

    return changed_files


def get_prefix_assemblies(files_found):
    """Return a sorted list of assemblies with a prefix."""
    prefix_assembly_files = []

    for file in files_found:
        file_name = os.path.basename(file)
        if file_name.startswith('assembly'):
            prefix_assembly_files.append(file)

    return(sorted(prefix_assembly_files, key=str.lower))


def get_prefix_modules(files_found):
    """Return a sorted list of modules with a prefix."""
    prefix_module_files = []

    for file in files_found:
        file_name = os.path.basename(file)
        if file_name.startswith(('proc', 'con', 'ref')):
            prefix_module_files.append(file)

    return(sorted(prefix_module_files, key=str.lower))


def get_no_prefix_files(files_found):
    """Return a list of files that have no prefix."""
    no_prefix_files = []

    for file in files_found:
        file_name = os.path.basename(file)
        if not file_name.startswith(('proc', 'con', 'ref', 'assembly')):
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

            content_type = re.findall(Regex.CONTENT_TYPE, original)

            if content_type in (['PROCEDURE'], ['CONCEPT'], ['REFERENCE']):
                no_prefix_module_type.append(path)

            if content_type == ['ASSEMBLY']:
                no_prefix_assembly_type.append(path)

            if not content_type:
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


def validate_merge_request_files():
    get_mr()
    changed_files = get_changed_files()
    files_found = get_exist(changed_files)
    no_prefix_files = get_no_prefix_files(files_found)
    modules_found = get_all_modules(files_found, no_prefix_files)
    assemblies_found = get_all_assemblies(files_found, no_prefix_files)
    undetermined_file_type = get_undetermined_files(no_prefix_files)

    if undetermined_file_type:
        print_message(undetermined_file_type, 'Merge Request', 'contains the following files that can not be classified as modules or assemblies')

    validate = validation(files_found, modules_found, assemblies_found)

    print_report_message(validate, 'Merge Request')
