#!/usr/bin/python3

from pcchecks import Regex, checks, nesting_in_modules_check, nesting_in_assemblies_check, add_res_section_module_check, add_res_section_assembly_check
import sys


class Report():
    """Create and print report. thank u J."""

    def __init__(self):
        """Create placeholder for problem description."""
        self.report = {}
        self.count = 0

    def create_report(self, category, file_path):
        """Generate report."""
        self.count += 1
        if not category in self.report:
            self.report[category] = []
        self.report[category].append(file_path)

    def print_report(self):

        """Print report."""
        separator = "\n\t"

        for category, files in self.report.items():
            print("\nFAIL: {} found in the following files:".format(category))
            print('\t' + separator.join(files))


def validation(files_found, modules_found, assemblies_found):
    """Validate files."""
    report = Report()

    for path in files_found:
        with open(path, "r") as file:
            original = file.read()
            stripped = Regex.MULTI_LINE_COMMENT.sub('', original)
            stripped = Regex.SINGLE_LINE_COMMENT.sub('', stripped)
            # FIXME: figure out a better way to exclude pseudo vanilla xrefs
            #stripped = Regex.PSEUDO_VANILLA_XREF.sub('', stripped)
            stripped = Regex.CODE_BLOCK.sub('', stripped)
            checks(report, stripped, original, path)

    for path in modules_found:
        with open(path, "r") as file:
            original = file.read()
            stripped = Regex.MULTI_LINE_COMMENT.sub('', original)
            stripped = Regex.SINGLE_LINE_COMMENT.sub('', stripped)
            # FIXME: figure out a better way to exclude pseudo vanilla xrefs
            #stripped = Regex.PSEUDO_VANILLA_XREF.sub('', stripped)
            stripped = Regex.CODE_BLOCK.sub('', stripped)
            nesting_in_modules_check(report, stripped, path)
            add_res_section_module_check(report, stripped, path)

    for path in assemblies_found:
        with open(path, "r") as file:
            original = file.read()
            stripped = Regex.MULTI_LINE_COMMENT.sub('', original)
            stripped = Regex.SINGLE_LINE_COMMENT.sub('', stripped)
            # FIXME: figure out a better way to exclude pseudo vanilla xrefs
            #stripped = Regex.PSEUDO_VANILLA_XREF.sub('', stripped)
            stripped = Regex.CODE_BLOCK.sub('', stripped)
            nesting_in_assemblies_check(report, stripped, path)
            add_res_section_assembly_check(report, stripped, path)

    return report
