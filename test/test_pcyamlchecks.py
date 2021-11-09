import unittest
import os

from PantheonCMD.pcyamlchecks import *


class TestGetYamlSize(unittest.TestCase):
    def setUp(self):
        self.current_path = os.path.dirname(__file__)
        self.fixtures_path = os.path.join(self.current_path, "fixtures")

    def test_empty_yml_file(self):
        file_name = os.path.join(self.fixtures_path, "empty.yml")

        with self.assertRaises(SystemExit) as cm:
            get_yaml_size(file_name)

        self.assertEqual(cm.exception.code, 2)

    def test_valid_yml_file(self):
        file_name = os.path.join(self.fixtures_path, "valid.yml")

        try:
            get_yaml_size(file_name)
        except ZeroDivisionError as exc:
            assert False, f"'valid.yml' raised an exception {exc}"


class TestLoadYml(unittest.TestCase):
    def setUp(self):
        self.current_path = os.path.dirname(__file__)
        self.fixtures_path = os.path.join(self.current_path, "fixtures")

    def test_corrupt_yml_syntax(self):
        file_name = os.path.join(self.fixtures_path, "syntax-error.yml")

        with self.assertRaises(SystemExit) as cm:
            load_yml(file_name)

        self.assertEqual(cm.exception.code, 2)

    def test_valid_yml_syntax(self):
        file_name = os.path.join(self.fixtures_path, "valid.yml")

        try:
            load_yml(file_name)
        except ZeroDivisionError as exc:
            assert False, f"'valid.yml' raised an exception {exc}"


class TestGetYamlErrors(unittest.TestCase):
    def setUp(self):
        self.current_path = os.path.dirname(__file__)
        self.fixtures_path = os.path.join(self.current_path, "fixtures")

    def test_yml_missing_keys(self):
        path_to_script = os.path.dirname(os.path.realpath(__file__))
        file_name = (path_to_script + "/fixtures/missing-keys.yml")
        loaded_yaml = load_yml(file_name)
        # load schema
        schema = eval(open(path_to_script + '/../PantheonCMD/schema.py', 'r').read())

        with self.assertRaises(SystemExit) as cm:
            get_yaml_errors(schema, loaded_yaml)

        self.assertEqual(cm.exception.code, 2)

    def test_valid_yml(self):
        path_to_script = os.path.dirname(os.path.realpath(__file__))
        file_name = (path_to_script + "/fixtures/valid.yml")
        loaded_yaml = load_yml(file_name)
        # load schema
        schema = eval(open(path_to_script + '/../PantheonCMD/schema.py', 'r').read())

        try:
            get_yaml_errors(schema, loaded_yaml)
        except ZeroDivisionError as exc:
            assert False, f"'valid.yml' raised an exception {exc}"



# run all the tests in this file
if __name__ == '__main__':
    unittest.main()
