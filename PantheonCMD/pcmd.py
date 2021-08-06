#!/usr/bin/python3

import argparse
import os
import pcbuild
import pcutil
import shutil
import sys

from pcutil import PantheonRepo, get_not_exist, get_exist, is_pantheon_repo
from pcvalidator import validation
from pcyamlcheck import yaml_validator
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

    parser_g = subparsers.add_parser('validate-yaml', help='Validate the syntax of your pantheon2.yml file.')

    return parser.parse_args()


# MAIN ROUTINE
if __name__ == "__main__":

    # Print the header
    print_header()

    # Parse arguments
    args = parse_args()

    repo_location = is_pantheon_repo()

    # Exit if not a Pantheon V2 repository
    if repo_location:
        # Construct a PantheonRepo instance
        pantheon_repo = PantheonRepo(repo_location)
    else:
        print("Not a Pantheon V2 repository; exiting...")
        sys.exit(1)

    # Else parse actions
    # Action - compile
    if args.command == 'compile':

        if args.files:

            pcbuild.build_content(pcutil.get_content_subset(args.files), args.lang, pantheon_repo.repo_location, pantheon_repo.yaml_file_location)

        else:

            if os.path.exists('pantheon2.yml'):

                content_types = ['assemblies','modules']
                continue_run = True

                for content_type in content_types:

                    if continue_run:

                        print("Building %s...\n" % content_type)
                        print(pantheon_repo.get_existing_content(content_type))

                        continue_run = pcbuild.build_content(pantheon_repo.get_existing_content(content_type), args.lang, pantheon_repo.repo_location, pantheon_repo.yaml_file_location)

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
            modules_found = pantheon_repo.get_existing_content("modules")
            assemblies_found = pantheon_repo.get_existing_content("assemblies")

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

    # Action - validate modules and assemblies
    elif args.command == 'validate-yaml':

        if os.path.exists('pantheon2.yml'):

            missing_keys = pantheon_repo.get_missing_yaml_keys()

            if missing_keys:

                print("Your pantheon2.yml is missing the following keys:\n")

                for key in missing_keys:

                    print(key)

                print("\nTotal: ", str(len(missing_keys)))

            else:

                print("All keys are set.")

                yaml_validation = yaml_validator(pantheon_repo)

                if yaml_validation.count != 0:
                    print("Your pantheon2.yml has the following errors:\n")
                    yaml_validation.print_report()

                else:

                    print("Your pantheon2.yml file passed validation.")

        else:
            print("ERROR: You must run this command from the same directory as the pantheon2.yml file.\n")
