#!/usr/bin/python3

import argparse
import os
import pcbuild
import shutil
import signal
import sys
from pcutil import PantheonRepo, get_not_exist, get_exist
from pcvalidator import validation
from subprocess import call


def print_header():
    """Prints the default program header."""
    print('==================================================')
    print('Pantheon CMD                                      ')
    print('==================================================')
    print('')


def parse_args():
    """Constructs the main argument parser and sub-parsers for actions and arguments."""
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
    parser_d = subparsers.add_parser('exists',help='Enumerate entries in your pantheon2.yml file that do not exist in path.')

    # 'Validate' command
    parser_e = subparsers.add_parser('validate', help='Validate entries in your pantheon2.yml file.')

    # 'Generate' command
    parser_f = subparsers.add_parser('generate', help='Generate pantheon2.yml file from a template.')

    return parser.parse_args()


def keyboardInterruptHandler(signal, frame):
    """Defines a keyboard interrupt process."""
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

    # Construct a PantheonRepo instance
    pantheon_repo = PantheonRepo()

    # Exit if not a Pantheon V2 repository
    if not pantheon_repo.is_pantheon_repo():

        print("Not a Pantheon V2 repository; exiting...")

        sys.exit(1)

    # Else parse actions
    # Action - compile
    elif args.command == 'compile':

        if args.files:

            pcbuild.build_content(pcutil.get_content_subset(args.files), args.lang, pantheon_repo.repo_location, pantheon_repo.yaml_file_location)

        else:

            if os.path.exists('pantheon2.yml'):

                pcbuild.build_content(pantheon_repo.get_content(), args.lang, pantheon_repo.repo_location, pantheon_repo.yaml_file_location)

            else:

                print("ERROR: You must run this command from the same directory as the pantheon2.yml file.\n")

                sys.exit(1)

    # Action - clean
    elif args.command == 'clean':

        if os.path.exists('build'):
            shutil.rmtree('build')
            print("Successfully removed build directory!")
        else:
            print("No build directory found; exiting...")

    # Action - find duplicate entries
    elif args.command == 'duplicates':

        duplicates = pantheon_repo.get_duplicates()

        if duplicates:

            print("Your pantheon2.yml contains the following duplicate entries:\n")

            for duplicate in duplicates:
                print(duplicate)

            print("\nTotal: ", str(len(duplicates)))

        else:

            print("No duplicates found.")

    # Action - find nonexistent files
    elif args.command == 'exists':

        if os.path.exists('pantheon2.yml'):

            exists = get_not_exist(pantheon_repo.get_content())

            if exists:

                print("Your pantheon2.yml contains the following files that do not exist in your repository:\n")

                for exist in exists:

                    print(exist)

                print("\nTotal: ", str(len(exists)))

            else:

                print("All files exist.")
        else:
            print("ERROR: You must run this command from the same directory as the pantheon2.yml file.\n")

    # Action - validate modules and assemblies
    elif args.command == 'validate':

        if os.path.exists('pantheon2.yml'):

            files_found = get_exist(pantheon_repo.get_content())
            modules_found = pantheon_repo.get_existing_modules()
            assemblies_found = pantheon_repo.get_existing_assemblies()

            validate = validation(files_found, modules_found, assemblies_found)

            if validate.count != 0:
                print("Your pantheon2.yml contains the following files that did not pass validation:\n")
                validate.print_report()
            else:
                print("All files passed validation.")
        else:
            print("ERROR: You must run this command from the same directory as the pantheon2.yml file.\n")

    # Action - generate a pantheon2.yml file
    elif args.command == 'generate':
        path_to_script = os.path.dirname(os.path.realpath(__file__))
        call("sh " + path_to_script + "/pv2yml-generator.sh", shell=True)
