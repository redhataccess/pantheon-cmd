#!/usr/bin/python3

import subprocess
import re
from pcchecks import Regex


def get_current_branch(path=None):
    command = 'git rev-parse --abbrev-ref HEAD'.split()
    current_branch = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=path).stdout.read()
    return current_branch.strip().decode('utf-8')


def get_target_branch(path=None):
    command = 'git rev-parse --abbrev-ref origin/HEAD'.split()
    target_branch = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=path).stdout.read()
    return target_branch.strip().decode('utf-8')


def get_changed_files(path=None):
    target_branch = get_target_branch()
    current_branch = get_current_branch()
    out = []
    buff = []

    command = ("git diff --diff-filter=ACM --name-only " + target_branch + "..." + current_branch + " -- '*.adoc' ':!*master.adoc'")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
    changed_files = process.communicate()[0].decode("utf-8")

    # converting the string into a list
    for item in changed_files:
        if item == '\n':
            out.append(''.join(buff))
            buff = []
        else:
            buff.append(item)
    else:
        if buff:
            out.append(''.join(buff))

    return out


def get_prefix_assemblies(files_found):
    prefix_assembly_files = []

    for file in files_found:
        if re.findall(Regex.prefix_assemblies, file):
            prefix_assembly_files.append(file)

    return(sorted(prefix_assembly_files, key=str.lower))


def get_prefix_modules(files_found):
    prefix_module_files = []

    for file in files_found:
        if re.findall(Regex.prefix_modules, file):
            prefix_module_files.append(file)

    return(sorted(prefix_module_files, key=str.lower))


def get_no_prefix_files(files_found):
    no_prefix_files = []

    for file in files_found:
        if not re.findall(Regex.prefix_assemblies, file) and not re.findall(Regex.prefix_modules, file):
            no_prefix_files.append(file)

    return no_prefix_files


def get_no_prefefix_file_type(no_prefix_files):
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
    no_prefix_module_type, no_prefix_assembly_type, undetermined_file_type = get_no_prefefix_file_type(no_prefix_files)

    return(sorted(no_prefix_module_type, key=str.lower))


def get_no_prefix_assemblies(no_prefix_files):
    no_prefix_module_type, no_prefix_assembly_type, undetermined_file_type = get_no_prefefix_file_type(no_prefix_files)

    return(sorted(no_prefix_assembly_type, key=str.lower))


def get_all_modules(files_found, no_prefix_files):
    prefix_module_files = get_prefix_modules(files_found)
    no_prefix_module_type = get_no_prefix_modules(no_prefix_files)

    return prefix_module_files + no_prefix_module_type


def get_all_assemblies(files_found, no_prefix_files):
    prefix_assemblies = get_prefix_assemblies(files_found)
    no_prefix_assembly_type = get_no_prefix_assemblies(no_prefix_files)

    return prefix_assemblies + no_prefix_assembly_type


def get_undetermined_files(no_prefix_files):
    no_prefix_module_type, no_prefix_assembly_type, undetermined_file_type = get_no_prefefix_file_type(no_prefix_files)

    return(sorted(undetermined_file_type, key=str.lower))
