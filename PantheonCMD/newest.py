#!/usr/bin/python3

import sys
from pcyamlchecks import get_yaml_size, get_yaml_syntax_errors, checks


class Report():
    """Create and print report."""

    def __init__(self):
        self.report = {}
        self.count = 0

    def create_report(self, message, items):
        """Generate report."""
        self.count += 1
        if not message in self.report:
            self.report[message] = []
        self.report[message].append(items)

    def print_report(self):
        """Print report."""
        separator = "\n\t"

        for message, items in self.report.items():
            print("\nFAIL: Your pantheon2.yml {}:".format(message))
            for item in items:
                print('\t' + separator.join(item))


def yaml_validation(yaml_file):
    report = Report()

    checks(yaml_file, report)

    return report


#pcmd.py emulator

if get_yaml_size('pantheon2.yml') is True:
    print("\nYour pantheon2.yml file is empty; exiting...")
    sys.exit(2)


if get_yaml_syntax_errors('pantheon2.yml') is True:
    print("There's a syntax error in your pantheon2.yml file. Please fix it and try again.\nTo detect an error try running yaml lint on your pantheo2.yml file.")
    sys.exit(2)


validate = yaml_validation('pantheon2.yml')

if validate.count != 0:
    validate.print_report()
    sys.exit(2)
else:
    print("\nYour pantheon2.yml file passed validation.")
    sys.exit(0)
