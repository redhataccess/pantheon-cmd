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


# run all the tests in this file
if __name__ == '__main__':
    unittest.main()
