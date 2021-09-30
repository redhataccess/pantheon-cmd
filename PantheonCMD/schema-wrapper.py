#!/usr/bin/python3
import os
import sys
import yaml
from cerberus import Validator, errors
from cerberus.errors import BasicErrorHandler
from pcutil import is_pantheon_repo

pantheon_repo = is_pantheon_repo()
yaml_file = pantheon_repo + 'pantheon2.yml'


class CustomErrorHandler(BasicErrorHandler):
    """Custom error messages."""
    messages = errors.BasicErrorHandler.messages.copy()
    messages[errors.REQUIRED_FIELD.code] = "key is missing"
    messages[errors.UNKNOWN_FIELD.code] = "unknown key"
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

for key in v.errors.keys():
    print("Error in '{}': \n\t{}".format(key, ', '.join(str(item) for item in v.errors[key])))
