#!/usr/bin/python3

import argparse
import os
import pcbuild
import pcutil
import shutil
import sys

from pcutil import PantheonRepo, get_not_exist, get_exist, is_pantheon_repo
from pcvalidator import validation
from pcyamlcheck import yaml_validator, get_missing_keys, get_empty_values, get_yaml_syntax_errors
from subprocess import call
from pcprvalidator import get_changed_files, get_all_modules, get_all_assemblies, get_undetermined_files, get_no_prefix_files


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

    # 'Preview' command
    parser_a = subparsers.add_parser('preview', help='Build a preview of content.')
    parser_a.add_argument('--files', help='The files to target.')
    parser_a.add_argument('--lang', help='The language to build. For example, ja-JP.')

    # 'Clean' command
    parser_b = subparsers.add_parser('clean', help='Clean the build directory.')

    # 'Duplicates' command
    parser_c = subparsers.add_parser('duplicates', help='Enumerate duplicate entries in your pantheon2.yml file.')

    # 'Validate' command
    parser_d = subparsers.add_parser('validate', help='Validate entries in your pantheon2.yml file.')
    parser_d.add_argument('--mr', action='store_true', help='Validate files commited on a merge request.')

    # 'Generate' command
    parser_e = subparsers.add_parser('generate', help='Generate pantheon2.yml file from a template.')

    return parser.parse_args()


# MAIN ROUTINE
if __name__ == "__main__":

    # Print the header
    print_header()

    # Parse arguments
    args = parse_args()

    repo_location = is_pantheon_repo()

    # Action - generate a pantheon2.yml file
    if args.command == 'generate':
        path_to_script = os.path.dirname(os.path.realpath(__file__))
        call("sh " + path_to_script + "/pv2yml-generator.sh", shell=True)
        sys.exit(0)


    # Action - validate yaml syntax, validate yaml keys and values
    # find nonexistent files
    # validate modules and assemblies
    elif args.command == 'validate':

        if args.mr:

            changed_files = get_changed_files()
            files_found = get_exist(changed_files)
            no_prefix_files = get_no_prefix_files(files_found)
            modules_found = get_all_modules(files_found, no_prefix_files)
            assemblies_found = get_all_assemblies(files_found, no_prefix_files)
            undetermined_file_type = get_undetermined_files(no_prefix_files)

            if undetermined_file_type:
                print("\nYour Merge Request contains the following files that can not be classified as modules or assemblies:\n")

                for file in undetermined_file_type:

                    print('\t' + file)

                print("\nTotal: ", str(len(undetermined_file_type)))

            validate = validation(files_found, modules_found, assemblies_found)

            if validate.count != 0:
                print("\nYour Merge Request contains the following files that did not pass validation:\n")
                validate.print_report()
                sys.exit(2)
            else:
                print("All files passed validation.")
                sys.exit(0)
        else:

            pantheon_repo = PantheonRepo(repo_location)

            if os.path.exists('pantheon2.yml'):

                # function searches for syntax errors and prints the results
                syntax_errors = get_yaml_syntax_errors(pantheon_repo)
                missing_keys = get_missing_keys(pantheon_repo)
                empty_values = get_empty_values(pantheon_repo)

                if missing_keys:

                    print("\nYour pantheon2.yml is missing the following keys:\n")

                    for key in missing_keys:

                        print('\t' + key)

                    print("\nTotal: ", str(len(missing_keys)))
                    print('\nPlease fix your pantheon2.yml to validte the files; exiting...')
                    sys.exit(2)

                if empty_values:

                    print("\nYour pantheon2.yml has the following keys with no value:\n")

                    for value in empty_values:

                        print('\t' + value)

                    print("\nTotal: ", str(len(empty_values)))
                    print('\nPlease fix your pantheon2.yml to validte the files; exiting...')
                    sys.exit(2)

                files_found = get_exist(pantheon_repo.get_content())
                modules_found = pantheon_repo.get_existing_content("modules")
                assemblies_found = pantheon_repo.get_existing_content("assemblies")

                yaml_validation = yaml_validator(pantheon_repo)

                if yaml_validation.count != 0:
                    print("\nYour pantheon2.yml has the following errors:\n")
                    yaml_validation.print_report()
                    sys.exit(2)

                exists = get_not_exist(pantheon_repo.get_content())

                if exists:

                    print("\nYour pantheon2.yml contains the following files that do not exist in your repository:\n")

                    for exist in exists:

                        print('\t' + exist)

                    print("\nTotal: ", str(len(exists)))

                files_found = get_exist(pantheon_repo.get_content())
                modules_found = pantheon_repo.get_existing_content("modules")
                assemblies_found = pantheon_repo.get_existing_content("assemblies")

                validate = validation(files_found, modules_found, assemblies_found)

                if validate.count != 0:
                    print("\nYour pantheon2.yml contains the following files that did not pass validation:\n")
                    validate.print_report()
                    sys.exit(2)
                else:
                    print("All files passed validation.")

            else:

                print("ERROR: You must run this command from the same directory as the pantheon2.yml file.\n")
                sys.exit(1)

    # Exit if not a Pantheon V2 repository
    if repo_location:
        # Construct a PantheonRepo instance
        pantheon_repo = PantheonRepo(repo_location)
    else:
        print("Not a Pantheon V2 repository; exiting...")
        sys.exit(1)

    # Else parse actions
    # Action - preview
    if args.command == 'preview':
        # Did a user specify a set of files? If so, only build those.
        if args.files:
            # Handle different interpretations of directories
            if os.path.isdir(args.files):
                if args.files.endswith('/'):
                    args.files += '*.adoc'
                else:
                    args.files += '/*.adoc'

            # Get set of files
            content_subset = pcutil.get_content_subset(args.files)

            # Ensure at least one valid file exists in the set
            if not content_subset:
                print("Couldn't find any valid files; exiting...\n")
                sys.exit(1)
            else:
                pcbuild.prepare_build_directory()
                pcbuild.copy_resources(pantheon_repo.get_existing_content("resources"))
                pcbuild.build_content(content_subset, args.lang, pantheon_repo.repo_location, pantheon_repo.yaml_file_location)
        # Otherwise, attempt to build all files in the pantheon2.yml file.
        else:
            if os.path.exists('pantheon2.yml'):
                content_types = ['assemblies','modules']
                continue_run = True

                pcbuild.prepare_build_directory()
                pcbuild.copy_resources(pantheon_repo.get_existing_content("resources"))

                for content_type in content_types:
                    if continue_run:
                        print("Building %s...\n" % content_type)
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
