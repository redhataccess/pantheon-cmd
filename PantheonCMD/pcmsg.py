#!/usr/bin/python3

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
            print("\nERROR: {} found in the following files:".format(category))
            print('\t' + separator.join(files))


def print_message(variable, specification, msg):
    print(f'\nYour {specification} {msg}:\n')
    for var in variable:
        print('\t', var)
    print("\nTotal: ", str(len(variable)))


def print_report_message(variable, specification):
    if variable.count != 0:
        print(f"\nYour {specification} contains the following files that did not pass validation:\n")
        variable.print_report()
        sys.exit(2)
    else:
        print("All files passed validation.")
        sys.exit(0)
