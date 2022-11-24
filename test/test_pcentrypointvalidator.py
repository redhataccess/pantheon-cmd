
import unittest
import os
import glob

from PantheonCMD.pcentrypointvalidator import *


class TestGetNonexistentEntryPoint(unittest.TestCase):
    def setUp(self):
        self.current_path = os.path.dirname(__file__)
        self.fixtures_path = os.path.join(self.current_path, "fixtures")

    def test_fake_path(self):
        file_name ="/some/fake/path.adoc"

        with self.assertRaises(SystemExit) as cm:
            get_nonexisting_entry_points(file_name)

        self.assertEqual(cm.exception.code, 2)

    def test_real_path(self):
        files = glob.glob(self.fixtures_path + '/*.adoc')

        try:
            get_nonexisting_entry_points(files)
        except ExceptionType:
            self.fail("get_nonexisting_entry_points() raised ExceptionType unexpectedly!")


class TestRemoveAttributeFiles(unittest.TestCase):
    def test_underscore_filename(self):
        files = ['some-file.adoc', '_attribute.adoc']

        result = remove_attribute_files(files)
        self.assertEqual(result, ['some-file.adoc'])

    def test_undescore_directory(self):
        files = ['some-file.adoc', '_dir/attribute.adoc']

        result = remove_attribute_files(files)
        self.assertEqual(result, ['some-file.adoc'])

    def test_undescore_files_and_dir(self):
        files = ['some-file.adoc', '_dir/attribute.adoc', '_attribute.adoc']

        result = remove_attribute_files(files)
        self.assertEqual(result, ['some-file.adoc'])

    def test_no_undescore(self):
        files = ['some-file.adoc']

        result = remove_attribute_files(files)
        self.assertEqual(result, ['some-file.adoc'])

    def test_all_undescore(self):
        files = ['_dir/attribute.adoc', '_attribute.adoc']

        result = remove_attribute_files(files)
        self.assertEqual(result, [])

    def test_empty_list(self):
        files = []

        result = remove_attribute_files(files)
        self.assertEqual(result, [])


class TestSubAttributesInPath(unittest.TestCase):
    def setUp(self):
        self.current_path = os.path.dirname(__file__)

    def attribute_in_path(self):
        file_name = os.path.join(self.fixtures_path, "{attribute}/valid.yml")
        


# run all the tests in this file
if __name__ == '__main__':
    unittest.main()
