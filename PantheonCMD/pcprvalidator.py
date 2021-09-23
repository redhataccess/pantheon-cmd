#!/usr/bin/python3

import subprocess
import re
import fnmatch
from pcvalidator import validation
from pcutil import get_existence, get_exist, get_not_exist


class Regex:
    """Define regular expresiions for determiming file type."""
    prefix_assemblies = re.compile(r'.*\/assembly.*\.adoc')
    prefix_modules = re.compile(r'.*\/con.*\.adoc|.*\/proc.*\.adoc|.*\/ref.*\.adoc')
    #no_prefix_files
    #no_prefix_assemblies
    #no_prefix_modules
    #undetermined_file_type


def get_current_branch(path=None):
    command = 'git rev-parse --abbrev-ref HEAD'.split()
    current_branch = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=path).stdout.read()
    return current_branch.strip().decode('utf-8')


# print(get_current_branch())


def get_target_branch(path=None):
    command = 'git rev-parse --abbrev-ref origin/HEAD'.split()
    target_branch = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=path).stdout.read()
    return target_branch.strip().decode('utf-8')


# print(get_target_branch())


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


files_found = get_exist(get_changed_files())
files_not_found = get_not_exist(get_changed_files())


def get_prefix_assemblies():
    prefix_assembly_files = []

    for file in files_found:
        if re.findall(Regex.prefix_assemblies, file):
            prefix_assembly_files.append(file)

    return prefix_assembly_files


def get_prefix_modules():
    prefix_module_files = []

    for file in files_found:
        if re.findall(Regex.prefix_modules, file):
            prefix_module_files.append(file)

    return prefix_module_files
