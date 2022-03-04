#!/usr/bin/python3
import os
import sys
from enki_checks import Regex, icons_check, toc_check, nbsp_check, checks, nesting_in_modules_check, add_res_section_module_check, add_res_section_assembly_check
import re
import subprocess
from enki_yaml_valiadtor import Report, printing_build_yml_error


def get_files_bash(file_path):
    """Expand filepaths."""
    command = "find  " + str(file_path) + " -type f -name \*adoc 2>/dev/null"
    process = subprocess.run(command, stdout=subprocess.PIPE, shell=True).stdout
    files = process.strip().decode('utf-8').split('\n')

    return files


def sort_prefix_files(files):
    """Get a list of assemblies, modulesa, and unidentifiyed files."""
    prefix_assembly = []
    prefix_modules = []
    undefined_content = []
    attribute_file = []

    for item in files:
        file_name = os.path.basename(item)
        file_path = os.path.basename(item)

        if file_path.startswith("_"):
            attribute_file.append(item)
        elif "/_" in file_path:
            attribute_file.append(item)

        if file_name.startswith('assembly'):
            prefix_assembly.append(item)
        elif file_name.startswith(("proc_", "con_", "ref_", "proc-", "con-", "ref-")):
            prefix_modules.append(item)
        elif file_name.startswith("_"):
            attribute_file.append(item)
        elif file_name.startswith(("snip_", "snip-")):
            continue
        elif file_name == 'master.adoc':
            continue
        else:
            undefined_content.append(item)

    return attribute_file, prefix_assembly, prefix_modules, undefined_content


def file_validation(files):
    """Validate all files."""
    attribute_file, prefix_assembly, prefix_modules, undefined_content = sort_prefix_files(files)

    all_files = prefix_assembly + prefix_modules + undefined_content

    undetermined_file_type = []
    confused_files = []

    report = Report()

    for path in all_files:
        with open(path, 'r') as file:
            original = file.read()
            stripped = Regex.MULTI_LINE_COMMENT.sub('', original)
            stripped = Regex.SINGLE_LINE_COMMENT.sub('', stripped)
            stripped = Regex.CODE_BLOCK_DASHES.sub('', stripped)
            stripped = Regex.CODE_BLOCK_TWO_DASHES.sub('', stripped)
            stripped = Regex.CODE_BLOCK_DOTS.sub('', stripped)
            stripped = Regex.INTERNAL_IFDEF.sub('', stripped)

            checks(report, stripped, original, path)
            icons_check(report, stripped, path)
            toc_check(report, stripped, path)

            if path in undefined_content:
                if re.findall(Regex.MODULE_TYPE, stripped):
                    nesting_in_modules_check(report, stripped, path)
                    add_res_section_module_check(report, stripped, path)

                elif re.findall(Regex.ASSEMBLY_TYPE, stripped):
                    add_res_section_assembly_check(report, stripped, path)

                else:
                    undetermined_file_type.append(path)

            if path in prefix_assembly:
                if re.findall(Regex.MODULE_TYPE, stripped):
                    confused_files.append(path)
                    nesting_in_modules_check(report, stripped, path)
                    add_res_section_module_check(report, stripped, path)
                else:
                    add_res_section_assembly_check(report, stripped, path)

            if path in prefix_modules:
                if re.findall(Regex.ASSEMBLY_TYPE, stripped):
                    confused_files.append(path)
                    add_res_section_assembly_check(report, stripped, path)
                else:
                    nesting_in_modules_check(report, stripped, path)
                    add_res_section_module_check(report, stripped, path)

    if confused_files:
        printing_build_yml_error("files that have mismatched name prefix and content type tag. Content type tag takes precedence. The files were checked according to the tag", confused_files)

    if undetermined_file_type:
        printing_build_yml_error('files that can not be classified as modules or assemblies', undetermined_file_type)

    return report


def multi_file_validation(file_path):
    files = get_files_bash(file_path)
    validation = file_validation(files)

    if validation.count != 0:
        validation.print_report()
        sys.exit(2)


def single_file_validation(files):
    validation = file_validation(files)

    if validation.count != 0:
        validation.print_report()
        sys.exit(2)
