#!/usr/bin/python3

import argparse
import os
import pcbuild
import pcutil
import shutil
import sys

from pcutil import PantheonRepo, get_not_exist, get_exist, is_pantheon_repo
from validation.pcvalidator import validate_build_files
from validation.pcyamlchecks import yaml_validation
from subprocess import call
from validation.pcprvalidator import validate_merge_request_files
from validation.pcentrypointvalidator import validate_entry_point_files
from validation.pcmsg import print_message, print_report_message


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
    parser_a.add_argument('--format', choices=['html','pdf'], help='The format of the files to output.')
    parser_a.add_argument('--lang', help='The language to build. For example, ja-JP.')

    # 'Clean' command
    parser_b = subparsers.add_parser('clean', help='Clean the build directory.')

    # 'Duplicates' command
    parser_c = subparsers.add_parser('duplicates', help='Enumerate duplicate entries in your pantheon2.yml file.')

    # 'Validate' command
    parser_d = subparsers.add_parser('validate', help='Validate entries in your pantheon2.yml file.')
    parser_d.add_argument('--mr', action='store_true', help='Validate files commited on a merge request.')
    parser_d.add_argument('--e', nargs=1, help='Validate files from an entry point.')

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

        # user provides paths to files that are relative to current pwd

        if args.e:
            entry_point_list = args.e
            validate_entry_point_files(entry_point_list)

        elif args.mr:

            validate_merge_request_files()

        else:

            if os.path.exists('pantheon2.yml'):

                # call yaml file validation + attribute file validation
                yaml_validation('pantheon2.yml')

                validate_build_files()

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

        if args.format == 'pdf':
                output_format = 'pdf'
        else:
                output_format = 'html'

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
                pcbuild.build_content(content_subset, args.lang, output_format, pantheon_repo.repo_location, pantheon_repo.yaml_file_location)
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
                        continue_run = pcbuild.build_content(pantheon_repo.get_existing_content(content_type), args.lang, output_format, pantheon_repo.repo_location, pantheon_repo.yaml_file_location)
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
            print_message(duplicates, 'pantheon2.yml', 'contains the following duplicate entries')

        else:

            print("No duplicates found.")
