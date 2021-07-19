#!/usr/libexec/platform-python

import argparse
import os
import pcbuild
import pcutil
import shutil
import signal
import sys
from pcvalidator import validation, Report


# Prints the default header
def print_header():

    print('==================================================')
    print('Pantheon CMD                                      ')
    print('==================================================')
    print('')


# Construct argument parser and parse arguments
def parse_args():

    # Main parser
    parser = argparse.ArgumentParser(prog='pcmd')
    parser = argparse.ArgumentParser(description='Preview and validate modular content from the command line.')

    # Main subparsers
    subparsers = parser.add_subparsers(dest='command')

    # 'Compile' command
    parser_a = subparsers.add_parser('compile', help='Build a preview of content.')
    parser_a.add_argument('--files', help='The files to target.')
    parser_a.add_argument('--lang', help='The language to build. For example, ja-JP.')

    # 'Clean' command
    parser_b = subparsers.add_parser('clean', help='Clean the build directory.')

    # 'Duplicates' command
    parser_c = subparsers.add_parser('duplicates', help='Enumerate duplicate entries in your pantheon2.yml file.')

    # 'Exists' command
    parser_d = subparsers.add_parser('exists', help='Enumerate entries in your pantheon2.yml file that do not exist in path.')

    # 'Validate' command
    parser_e = subparsers.add_parser('validate', help='Validate entries in your pantheon2.yml file.')

    return parser.parse_args()


# Define keyboard interrupt cleanup process
def keyboardInterruptHandler(signal, frame):

    print("Operation cancelled; exiting...")

    exit(0)


# MAIN ROUTINE
if __name__ == "__main__":

    # Print the header
    print_header()

    # Parse arguments
    args = parse_args()

    # Add custom keyboard interrupt handler
    signal.signal(signal.SIGINT, keyboardInterruptHandler)

    # Get the location of the pantheon2.yml file, if any
    yaml_file_location = pcutil.get_yaml_file()

    # Exit if not a Pantheon V2 repository
    if not yaml_file_location:

        print("No pantheon2.yml file detected; exiting...")

        sys.exit(1)

    # Else parse actions
    # Action - compile
    elif args.command == 'compile':

        if args.files:

            pcbuild.build_content(pcutil.get_content_subset(args.files), yaml_file_location, args.lang)

        else:

            if os.path.exists('pantheon2.yml'):

                pcbuild.build_content(pcutil.get_content(yaml_file_location), yaml_file_location, args.lang)

            else:

                print("ERROR: You must run this command from the same directory as the pantheon2.yml file.\n")

                sys.exit(1)

    # Action - clean
    elif args.command == 'clean':

        if os.path.exists('build'):

            shutil.rmtree('build')

            print("Successfully removed build directory!")

    # Action - find duplicate entries
    elif args.command == 'duplicates':

        duplicates = pcutil.get_duplicates(yaml_file_location)

        if duplicates:

            print("Your pantheon2.yml contains the following duplicate entries:\n")

            for duplicate in duplicates:

                print(duplicate)

            print("\nTotal: ", str(len(duplicates)))

        else:

            print("No duplicates found.")

    # Action - find nonexistent files
    elif args.command == 'exists':

        exists = pcutil.get_not_exist(pcutil.get_content(pcutil.get_yaml_file()))

        if os.path.exists('pantheon2.yml'):

            if exists:

                print("Your pantheon2.yml contains the following files that do not exist in your repository:\n")

                for exist in exists:

                    print(exist)

                print("\nTotal: ", str(len(exists)))

            else:

                print("All files exist.")
        else:
            print("ERROR: You must run this command from the same directory as the pantheon2.yml file.\n")

    # Action - find nonexistent files
    elif args.command == 'validate':

        validate = validation(pcutil.get_exist(pcutil.get_content(pcutil.get_yaml_file())))

        if os.path.exists('pantheon2.yml'):
            if validate.count != 0:
                print("Your pantheon2.yml contains the following files that did not pass validation:\n")
                validate.print_report()
            else:
                print("All files passed validation.")
        else:
            print("ERROR: You must run this command from the same directory as the pantheon2.yml file.\n")
