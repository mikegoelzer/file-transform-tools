import inspect
import os
import tempfile
from file_transform_tools.util.delta import show_delta_diff_strs
from file_transform_tools.util.find_block import find_lines_to_replace
from file_transform_tools.util.cli import ActionIfBlockNotFound
from file_transform_tools.replace_block import replace_or_insert_block

COLOR_RED = "\033[91m"
COLOR_RESET = "\033[0m"
COLOR_MAGENTA = "\033[95m"

def who_called_me(level:int=1)->str:
    frame = inspect.currentframe()
    caller_frame = frame.f_back
    for _ in range(level):
        caller_frame = caller_frame.f_back
    return caller_frame.f_code.co_name

class TestHelpersMixin:
    def assert_file_contents_equal(self, temp_file_actual_name:str, expected_file_str:str):
        with open(temp_file_actual_name, 'r') as f:
            actual_file_str = f.read()
        if (actual_file_str != expected_file_str):
            print(f"{COLOR_RED}{who_called_me(level=2)}{COLOR_RESET}")
            print(f"    {COLOR_MAGENTA}FULL ACTUAL FILE{COLOR_RESET}")
            for i, line in enumerate(actual_file_str.splitlines()):
                print(f"    {i}: {line!r}")
            print()
            print(f"    {COLOR_MAGENTA}FULL EXPECTED FILE{COLOR_RESET}")
            for i, line in enumerate(expected_file_str.splitlines()):
                print(f"    {i}: {line!r}")
            print()
            show_delta_diff_strs(str1=expected_file_str, str2=actual_file_str, name1="expected", name2="actual")
        self.assertEqual(actual_file_str, expected_file_str, f"actual_file_str = {actual_file_str!r}, expected_file_str = {expected_file_str}")

class ReplaceWithAssertMixin:
    def replace_with_asserts(self, test_file_str, action:ActionIfBlockNotFound, replacement_text:str, expected_line_ranges, expected_file_str, expected_num_line_ranges):
        try:
            temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
            temp.write(test_file_str)
            temp.close()
            line_ranges = find_lines_to_replace(temp.name, self.pat)
            assert len(line_ranges) == expected_num_line_ranges, f"len(line_ranges) = {len(line_ranges)}, expected expected_num_line_ranges"
            assert line_ranges == expected_line_ranges, f"line_ranges = {line_ranges}, expected_line_ranges={expected_line_ranges}"
            for line_range, expected_line_range in zip(line_ranges, expected_line_ranges):
                assert line_range == expected_line_range, f"line_range = {line_range}, expected_line_range = {expected_line_range}"
            replace_or_insert_block(temp.name, line_ranges, action, replacement_text)
            self.assert_file_contents_equal(temp_file_actual_name=temp.name, expected_file_str=expected_file_str)
        finally:
            try:
                os.unlink(temp.name)
            except:
                pass

class NewLineControlReplaceWithAssertMixin:
    def newline_control_replace_with_asserts(self, test_file_str, action:ActionIfBlockNotFound, replacement_text:str, expected_line_ranges,expected_file_str, expected_lines_inserted_or_replaced, desired_preceding_newlines:int=None, desired_trailing_newlines:int=None):
        try:
            temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
            temp.write(test_file_str)
            temp.close()
            line_ranges = find_lines_to_replace(temp.name, self.pat)
            assert len(line_ranges) == 1, f"len(line_ranges) = {len(line_ranges)}, expected 1"
            assert line_ranges == expected_line_ranges, f"line_ranges = {line_ranges}, expected_line_ranges = {expected_line_ranges}"
            line_ranges_inserted_or_replaced = []
            replace_or_insert_block(temp.name, line_ranges, action, replacement_text, line_ranges_inserted_or_replaced=line_ranges_inserted_or_replaced, desired_preceding_newlines=desired_preceding_newlines, desired_trailing_newlines=desired_trailing_newlines)
            assert line_ranges_inserted_or_replaced == expected_lines_inserted_or_replaced, f"line_ranges_inserted_or_replaced = {line_ranges_inserted_or_replaced}, expected_lines_inserted_or_replaced = {expected_lines_inserted_or_replaced}"
            self.assert_file_contents_equal(temp.name, expected_file_str)
        finally:
            try:
                os.unlink(temp.name)
            except:
                pass
