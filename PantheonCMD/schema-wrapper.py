#!/usr/bin/python3

from pprint import pprint
import yaml
from cerberus import Validator
import sys
import os
from pcutil import is_pantheon_repo

pantheon_repo = is_pantheon_repo()
yaml_file = pantheon_repo + 'pantheon2.yml'

if os.path.getsize(yaml_file) == 0:
    print("\nYour pantheon2.yml file is empty; exiting...")
    sys.exit(2)


def load_doc():
    with open(yaml_file, 'r') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError:
            print("There's a syntax error in your pantheon2.yml file. Please fix it and try again.\nTo detect an error try running yaml lint on your pantheo2.yml file.")
            sys.exit(2)


scriptdir = os.path.dirname(os.path.realpath(__file__))
schema = eval(open(scriptdir + '/schema.py', 'r').read())

v = Validator(schema)
doc = load_doc()

pprint(v.validate(doc, schema))
pprint(v.errors)
