#!/usr/bin/python3

from validation.pcchecks import Regex, checks, nesting_in_modules_check, nesting_in_assemblies_check, add_res_section_module_check, add_res_section_assembly_check, icons_check, toc_check
import sys
from validation.pcmsg import print_message, print_report_message, Report
from pcutil import get_not_exist, get_exist, PantheonRepo, is_pantheon_repo


def validation(files_found, modules_found, assemblies_found):
    """Validate files."""
    report = Report()

    for path in files_found:
        with open(path, "r") as file:
            original = file.read()
            stripped = Regex.MULTI_LINE_COMMENT.sub('', original)
            stripped = Regex.SINGLE_LINE_COMMENT.sub('', stripped)
            stripped = Regex.CODE_BLOCK_DASHES.sub('', stripped)
            stripped = Regex.CODE_BLOCK_DOTS.sub('', stripped)
            stripped = Regex.INTERNAL_IFDEF.sub('', stripped)
            checks(report, stripped, original, path)
            icons_check(report, stripped, path)
            toc_check(report, stripped, path)

    for path in modules_found:
        with open(path, "r") as file:
            original = file.read()
            stripped = Regex.MULTI_LINE_COMMENT.sub('', original)
            stripped = Regex.SINGLE_LINE_COMMENT.sub('', stripped)
            stripped = Regex.CODE_BLOCK_DASHES.sub('', stripped)
            stripped = Regex.CODE_BLOCK_DOTS.sub('', stripped)
            stripped = Regex.INTERNAL_IFDEF.sub('', stripped)
            nesting_in_modules_check(report, stripped, path)
            add_res_section_module_check(report, stripped, path)

    for path in assemblies_found:
        with open(path, "r") as file:
            original = file.read()
            stripped = Regex.MULTI_LINE_COMMENT.sub('', original)
            stripped = Regex.SINGLE_LINE_COMMENT.sub('', stripped)
            stripped = Regex.CODE_BLOCK_DASHES.sub('', stripped)
            stripped = Regex.CODE_BLOCK_DOTS.sub('', stripped)
            stripped = Regex.INTERNAL_IFDEF.sub('', stripped)
            nesting_in_assemblies_check(report, stripped, path)
            add_res_section_assembly_check(report, stripped, path)

    return report


def validate_build_files():
    repo_location = is_pantheon_repo()
    pantheon_repo = PantheonRepo(repo_location)

    exists = get_not_exist(pantheon_repo.get_content())

    if exists:
        print_message(exists, 'pantheon2.yml', 'contains the following files that do not exist in your repositor')

    files_found = get_exist(pantheon_repo.get_content())
    modules_found = pantheon_repo.get_existing_content("modules")
    assemblies_found = pantheon_repo.get_existing_content("assemblies")

    validate = validation(files_found, modules_found, assemblies_found)

    print_report_message(validate, 'pantheon2.yml')
