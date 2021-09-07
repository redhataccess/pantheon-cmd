#!/usr/bin/python3

import os
import sys
from pcvalidator import validation

# import variables collected with bash script
changed_files = os.environ.get('changed_files').split()
all_assemblies = os.environ.get('all_assemblies').split()
all_modules = os.environ.get('all_modules').split()
undetermined_file_type = os.environ.get('undetermined_file_type').split()

# call validator from the main validation script
validate = validation(changed_files, all_modules, all_assemblies)

if validate.count != 0:
    print("\nThe following files did not pass validation:\n")
    validate.print_report()
    if undetermined_file_type:
        print("\nThe following files can not be identifiyed as modules or assemblies:\n")
        for file in undetermined_file_type:
            print('\t' + file)
    sys.exit(2)
else:
    print("All files passed validation.")
