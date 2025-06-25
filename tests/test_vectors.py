import os
import sys
import unittest
from file_transform_tools.util.find_block import FileLineRange
from file_transform_tools.re_pattern_library import patterns
from file_transform_tools.util.cli import ActionIfBlockNotFound

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from test_helpers import TestHelpersMixin, ReplaceWithAssertMixin

class TestVectors(unittest.TestCase, TestHelpersMixin, ReplaceWithAssertMixin):
    pat = patterns['bash_rc_export_path']['pat']

    replacement_text = """Hello,
world!
"""
    replacement_at_file = "@tests/test_vectors/replace_with_file_contents/sample-at-replacement-file.txt"

    # def replace_with_asserts(self, test_file_str, action:ActionIfBlockNotFound, replacement_text:str, expected_line_range, expected_file_str):
    #     pat = patterns['bash_rc_export_path']['pat']
    #     temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
    #     try:
    #         temp.write(test_file_str)
    #         temp.close()
    #         line_ranges = find_lines_to_replace(temp.name, pat)
    #         assert len(line_ranges) == 1, f"len(line_ranges) = {len(line_ranges)}, expected 1"
    #         assert line_ranges[0] == expected_line_range, f"line_range = {line_ranges[0]}, expected_line_range = {expected_line_range}"
    #         replace_or_insert_block(temp.name, line_ranges, action, replacement_text)
    #         self.assert_file_contents_equal(temp.name, expected_file_str)
    #     finally:
    #         os.unlink(temp.name)

    def test_replace_block_with_string(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        for filename in os.listdir(f"{script_dir}/test_vectors/replace_with_string/input"):
            input_filename = f"{script_dir}/test_vectors/replace_with_string/input/{filename}"
            expected_filename = f"{script_dir}/test_vectors/replace_with_string/expected/{filename}"
            with open(input_filename, 'r') as f:
                test_file_str = f.read()
            with open(expected_filename, 'r') as f:
                expected_file_str = f.read()
            self.replace_with_asserts(test_file_str, ActionIfBlockNotFound.REPLACE_ONLY, self.replacement_text, FileLineRange(131, 134), expected_file_str)

    def test_replace_block_with_at_file(self):
        with open(self.replacement_at_file[1:], 'r') as f:
            replacement_text_from_file = f.read()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        for filename in os.listdir(f"{script_dir}/test_vectors/replace_with_file_contents/input"):
            input_filename = f"{script_dir}/test_vectors/replace_with_file_contents/input/{filename}"
            expected_filename = f"{script_dir}/test_vectors/replace_with_file_contents/expected/{filename}"
            with open(input_filename, 'r') as f:
                test_file_str = f.read()
            with open(expected_filename, 'r') as f:
                expected_file_str = f.read()
        
            self.replace_with_asserts(test_file_str, ActionIfBlockNotFound.REPLACE_ONLY, replacement_text_from_file, FileLineRange(14, 17), expected_file_str)
