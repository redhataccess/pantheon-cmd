#!/usr/bin/python3
import os
import sys
import yaml
from cerberus import Validator, errors
from cerberus.errors import BasicErrorHandler
from pcutil import is_pantheon_repo
import glob

pantheon_repo = is_pantheon_repo()
yaml_file = pantheon_repo + 'pantheon2.yml'


class CustomErrorHandler(BasicErrorHandler):
    """Custom error messages."""
    messages = errors.BasicErrorHandler.messages.copy()
    messages[errors.REQUIRED_FIELD.code] = "key is missing"
    messages[errors.UNKNOWN_FIELD.code] = "unsupported key"
    messages[errors.NOT_NULLABLE.code] = "value can't be empty"


# test if pv2.yml is empty
if os.path.getsize(yaml_file) == 0:
    print("\nYour pantheon2.yml file is empty; exiting...")
    sys.exit(2)


def load_doc():
    """Load pv2.yml and test for syntax errors."""
    with open(yaml_file, 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError:
            print("There's a syntax error in your pantheon2.yml file. Please fix it and try again.\nTo detect an error try running yaml lint on your pantheo2.yml file.")
            sys.exit(2)


scriptdir = os.path.dirname(os.path.realpath(__file__))
schema = eval(open(scriptdir + '/schema.py', 'r').read())

v = Validator(schema, error_handler=CustomErrorHandler())
doc = load_doc()

v.validate(doc, schema)

if v.errors:
    for key in v.errors.keys():
        print("Error in '{}': \n\t{}".format(key, ', '.join(str(item) for item in v.errors[key])))
else:

    path_does_not_exist = []
    path_exists = []

    for item in doc['resources']:
        path_to_images_dir = os.path.split(item)[0]
        if not glob.glob(path_to_images_dir):
            path_does_not_exist.append(item)

    for variant in doc['variants']:
        if not os.path.exists(variant['path']):
            path_does_not_exist.append(variant['path'])
        else:
            path_exists.append(variant['path'])

    if path_does_not_exist:
        print('\nFAIL: Your pantheon2.yml file contains the following file or directory that doesn not exist in your repository:\n')
        for path in path_does_not_exist:
            print('\t', path)
