#!/usr/bin/python3

import argparse
from pathlib import Path
import os
from enki_yaml_valiadtor import yaml_validation
from enki_files_valiadtor import multi_file_validation, single_file_validation

parser = argparse.ArgumentParser()
parser.add_argument("path", type=Path)

p = parser.parse_args()


user_input = p.path

if user_input.is_file():
    file_name = os.path.basename(user_input)
    file_path = os.path.dirname(user_input)
    if file_name == 'build.yml':
        file_name = os.path.basename(user_input)
        yaml_validation(user_input, file_path)
    else:
        str = str(user_input)
        list = str.split()
        single_file_validation(list)

elif user_input.is_dir():
    multi_file_validation(user_input)
else:
    print("ERROR: Provided path doesn't exist.")
