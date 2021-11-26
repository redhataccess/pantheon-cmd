import unittest
import os
import yaml

from PantheonCMD.validation.pcyamlchecks import *


# needs empty.yml, valid.yml
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


# needs syntax-error.yml, valid.yml
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
        file = yaml.safe_load("""
repository:
variants:
  - name: rhel83
    path: rhel-8/common-content/attributes.adoc
    canonical:
""")
        # load schema
        schema = eval(open(path_to_script + '/../PantheonCMD/validation/schema.py', 'r').read())

        with self.assertRaises(SystemExit) as cm:
            get_yaml_errors(schema, file)

        self.assertEqual(cm.exception.code, 2)

    def test_valid_yml(self):
        path_to_script = os.path.dirname(os.path.realpath(__file__))
        file_name = (path_to_script + "/fixtures/valid.yml")
        loaded_yaml = load_yml(file_name)
        # load schema
        schema = eval(open(path_to_script + '/../PantheonCMD/validation/schema.py', 'r').read())

        try:
            get_yaml_errors(schema, loaded_yaml)
        except ZeroDivisionError as exc:
            assert False, f"'valid.yml' raised an exception {exc}"


class TestGetResourcesPaths(unittest.TestCase):
    def test_fake_path(self):
        file = yaml.safe_load("""
resources:
  - fake-path/*.py
""")

        result = get_resources_paths(file)
        self.assertEqual(result, ['fake-path/*.py'], "Should return ['fake-path/*.py'] when path to resources does not exist.")

    def test_real_path(self):
        file = yaml.safe_load("""
resources:
  - validation/*.py
""")

        result = get_resources_paths(file)
        self.assertEqual(result, [], "Should return [] when path to resources exists.")


# TODO: might need to be rewritten to accept a list, not string (schema)
class TestGetAttributePaths(unittest.TestCase):
    def test_fake_path(self):
        file = yaml.safe_load("""
variants:
  - name: some-name
    path: fake-path/file.py
""")
        result = get_attribute_paths(file)
        self.assertEqual(result, ([], ['fake-path/file.py']))

    def test_real_path(self):
        file = yaml.safe_load("""
variants:
  - name: some-name
    path: validation/schema.py
""")
        result = get_attribute_paths(file)
        self.assertEqual(result, (['validation/schema.py'], []))

    # if rewritten to accept a list, a test case for a fake + valid path is needed


class TestGetAttributeFilePath(unittest.TestCase):
    def test_fake_path(self):
        file = yaml.safe_load("""
variants:
  - name: some-name
    path: fake-path/file.py
""")
        result = get_attribute_file_path(file)
        self.assertEqual(result, [], "Should return [] when path to attributes does not exist.")

    def test_real_path(self):
        file = yaml.safe_load("""
variants:
  - name: some-name
    path: validation/schema.py
""")
        result = get_attribute_file_path(file)
        self.assertEqual(result, ['validation/schema.py'], "Should return ['validation/schema.py'] when path to attributes exists.")


class TestGetNonexistentPaths(unittest.TestCase):
    def test_two_fake_paths(self):
        file = yaml.safe_load("""
variants:
  - name: some-name
    path: fake-path/file.py
resources:
  - fake-path/*.py
""")
        result = get_nonexistent_paths(file)
        self.assertEqual(result, ['fake-path/file.py', 'fake-path/*.py'])

    def test_two_real_paths(self):
        file = yaml.safe_load("""
variants:
  - name: some-name
    path: validation/schema.py
resources:
  - validation/*.py
""")
        result = get_nonexistent_paths(file)
        self.assertEqual(result, [])

    def test_real_attribute_path_and_fake_resources_path(self):
        file = yaml.safe_load("""
variants:
  - name: some-name
    path: validation/schema.py
resources:
  - fake-rec-path/*.py
""")

        result = get_nonexistent_paths(file)
        self.assertEqual(result, ['fake-rec-path/*.py'])

    def test_fake_attribute_path_and_real_resources_path(self):
        file = yaml.safe_load("""
variants:
  - name: some-name
    path: fake-att-path/file.adoc
resources:
  - validation/*.py
""")

        result = get_nonexistent_paths(file)
        self.assertEqual(result, ['fake-att-path/file.adoc'])

# get_attribute_file_validation_results function is just opening the file and runs toc + icon check. Those checks are tested in tests_pcchecks.py
# yaml_validation function doesn't need to be teted


# run all the tests in this file
if __name__ == '__main__':
    unittest.main()
