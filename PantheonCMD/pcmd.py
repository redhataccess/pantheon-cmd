#!/usr/libexec/platform-python

import argparse
import os
import pcbuild
import pcutil
import shutil
import sys


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

    return parser.parse_args()


# MAIN ROUTINE
if __name__ == "__main__":

    # Print the header
    print_header()

    # Parse arguments
    args = parse_args()

    # Exit if not a Pantheon 2 repository
    if not pcutil.get_yaml_file():

        print("No pantheon2.yml file detected; exiting...")

        sys.exit(2)

    # Else parse actions
    # Action - compile
    elif args.command == 'compile':

        try:

            if args.files:

                pcbuild.build_subset(args.files,args.lang)

            else:

                if os.path.exists('pantheon2.yml'):

                    pcbuild.build_all(args.lang)

                else:

                    print("ERROR: You must run this command from the same directory as the pantheon2.yml file.\n")

                    sys.exit(2)

        except (KeyboardInterrupt, OSError) as e:

            print("Operation cancelled; exiting...")

            sys.exit(0)

    # Action - clean
    elif args.command == 'clean':

        if os.path.exists('build'):

            shutil.rmtree('build')

            print("Successfully removed build directory!")
