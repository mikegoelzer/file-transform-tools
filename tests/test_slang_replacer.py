import os
import sys
import tempfile
import unittest

from file_transform_tools.util.find_block import find_lines_to_replace, FileLineRange
from file_transform_tools.util.cli import ActionIfBlockNotFound
from file_transform_tools.replace_block import replace_or_insert_block

# tests in other files
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from file_transform_tools.re_pattern_library import patterns, TestPatterns
from test_helpers import TestHelpersMixin, NewLineControlReplaceWithAssertMixin

class TestSlangReplacer(unittest.TestCase, TestHelpersMixin, NewLineControlReplaceWithAssertMixin):
    pat = patterns['ifdef_slang']['pat']

    test_file_str = """// This is the beginning of the file.

`ifdef SLANG  // maybe some comment
    `include "my_slang_file.sv"  // some comment
    `include "my_slang_file2.sv" // some other comment
`endif // maybe some comment

// This is the rest of the file...
"""

    replacement_text = """`ifdef SLANG
    `include "different_slang_file.sv"
    `include "different_slang_file2.sv"
    `include "different_slang_file3.sv"
    `include "different_slang_file4.sv"
`endif
"""

    test_file_str_expected_output = """// This is the beginning of the file.

`ifdef SLANG
    `include "different_slang_file.sv"
    `include "different_slang_file2.sv"
    `include "different_slang_file3.sv"
    `include "different_slang_file4.sv"
`endif

// This is the rest of the file...
"""

    test_file_str_expected_output_w00 = """// This is the beginning of the file.
`ifdef SLANG
    `include "different_slang_file.sv"
    `include "different_slang_file2.sv"
    `include "different_slang_file3.sv"
    `include "different_slang_file4.sv"
`endif
// This is the rest of the file...
"""

    test_file_str_expected_output_w23 = """// This is the beginning of the file.


`ifdef SLANG
    `include "different_slang_file.sv"
    `include "different_slang_file2.sv"
    `include "different_slang_file3.sv"
    `include "different_slang_file4.sv"
`endif



// This is the rest of the file...
"""

    # def slang_replace_with_asserts(self, test_file_str, action:ActionIfBlockNotFound, replacement_text:str, expected_line_ranges,expected_file_str, expected_lines_inserted_or_replaced, desired_preceding_newlines:int=None, desired_trailing_newlines:int=None):
    #     temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
    #     try:
    #         temp.write(test_file_str)
    #         temp.close()
    #         line_ranges = find_lines_to_replace(temp.name, self.pat)
    #         assert len(line_ranges) == 1, f"len(line_ranges) = {len(line_ranges)}, expected 1"
    #         assert line_ranges == expected_line_ranges, f"line_ranges = {line_ranges}, expected_line_ranges = {expected_line_ranges}"
    #         line_ranges_inserted_or_replaced = []
    #         replace_or_insert_block(temp.name, line_ranges, action, replacement_text, line_ranges_inserted_or_replaced=line_ranges_inserted_or_replaced, desired_preceding_newlines=desired_preceding_newlines, desired_trailing_newlines=desired_trailing_newlines)
    #         assert line_ranges_inserted_or_replaced == expected_lines_inserted_or_replaced, f"line_ranges_inserted_or_replaced = {line_ranges_inserted_or_replaced}, expected_lines_inserted_or_replaced = {expected_lines_inserted_or_replaced}"
    #         self.assert_file_contents_equal(temp.name, expected_file_str)
    #     finally:
    #         os.unlink(temp.name)

    def test_slang_replacer(self):
        self.newline_control_replace_with_asserts(self.test_file_str, ActionIfBlockNotFound.REPLACE_ONLY, self.replacement_text, expected_line_ranges=[FileLineRange(2, 5)], expected_file_str=self.test_file_str_expected_output, expected_lines_inserted_or_replaced=[FileLineRange(2, 7)], desired_preceding_newlines=None, desired_trailing_newlines=None)
        self.newline_control_replace_with_asserts(self.test_file_str, ActionIfBlockNotFound.REPLACE_ONLY, self.replacement_text, expected_line_ranges=[FileLineRange(2, 5)], expected_file_str=self.test_file_str_expected_output_w00, expected_lines_inserted_or_replaced=[FileLineRange(2, 7)], desired_preceding_newlines=0, desired_trailing_newlines=0)
        self.newline_control_replace_with_asserts(self.test_file_str, ActionIfBlockNotFound.REPLACE_ONLY, self.replacement_text, expected_line_ranges=[FileLineRange(2, 5)], expected_file_str=self.test_file_str_expected_output_w23, expected_lines_inserted_or_replaced=[FileLineRange(2, 7)], desired_preceding_newlines=2, desired_trailing_newlines=3)

class TestPrependAndAppendWithNewLineControl(unittest.TestCase, NewLineControlReplaceWithAssertMixin):
    pat = patterns['ifdef_slang']['pat']

    test_file_str_prepend = """`ifdef SLANG  // maybe some comment
    `include "my_slang_file.sv"  // some comment
    `include "my_slang_file2.sv" // some other comment
`endif // maybe some comment
X
Y
Z
"""

    test_file_str_append = """A
B
C
`ifdef SLANG  // maybe some comment
    `include "my_slang_file.sv"  // some comment
    `include "my_slang_file2.sv" // some other comment
`endif // maybe some comment
"""

    replacement_text = """insert1
insert2
insert3
"""

    test_file_str_append_expected_output = """A
B
C
insert1
insert2
insert3
"""

    test_file_str_prepend_expected_output = """insert1
insert2
insert3
X
Y
Z
"""

    test_file_str_append_expected_output_with_3_2 = """A
B
C



insert1
insert2
insert3


"""

    test_file_str_prepend_expected_output_with_3_2 = """
    
    
insert1
insert2
insert3


X
Y
Z
"""

    # def newline_control_replace_with_asserts(self, test_file_str, action:ActionIfBlockNotFound, replacement_text:str, expected_line_ranges,expected_file_str, expected_lines_inserted_or_replaced, desired_preceding_newlines:int=None, desired_trailing_newlines:int=None):
    #     temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
    #     try:
    #         temp.write(test_file_str)
    #         temp.close()
    #         line_ranges = find_lines_to_replace(temp.name, self.pat)
    #         assert len(line_ranges) == 1, f"len(line_ranges) = {len(line_ranges)}, expected 1"
    #         assert line_ranges == expected_line_ranges, f"line_ranges = {line_ranges}, expected_line_ranges = {expected_line_ranges}"
    #         line_ranges_inserted_or_replaced = []
    #         replace_or_insert_block(temp.name, line_ranges, action, replacement_text, line_ranges_inserted_or_replaced=line_ranges_inserted_or_replaced, desired_preceding_newlines=desired_preceding_newlines, desired_trailing_newlines=desired_trailing_newlines)
    #         assert line_ranges_inserted_or_replaced == expected_lines_inserted_or_replaced, f"line_ranges_inserted_or_replaced = {line_ranges_inserted_or_replaced}, expected_lines_inserted_or_replaced = {expected_lines_inserted_or_replaced}"
    #         self.assert_file_contents_equal(temp.name, expected_file_str)
    #     finally:
    #         os.unlink(temp.name)

    def test_prepend_no_desired_newlines(self):
        self.newline_control_replace_with_asserts(self.test_file_str_prepend, ActionIfBlockNotFound.REPLACE_OR_PREPEND, self.replacement_text, expected_line_ranges=[FileLineRange(0, 3)], expected_file_str=self.test_file_str_prepend_expected_output, expected_lines_inserted_or_replaced=[FileLineRange(0, 2)], desired_preceding_newlines=None, desired_trailing_newlines=None)
    
    def test_append_no_desired_newlines(self):
        self.newline_control_replace_with_asserts(self.test_file_str_append, ActionIfBlockNotFound.REPLACE_OR_APPEND, self.replacement_text, expected_line_ranges=[FileLineRange(3, 6)], expected_file_str=self.test_file_str_append_expected_output, expected_lines_inserted_or_replaced=[FileLineRange(3, 5)], desired_preceding_newlines=None, desired_trailing_newlines=None)
    
    def test_prepend_with_desired_newlines(self):
        self.newline_control_replace_with_asserts(self.test_file_str_prepend, ActionIfBlockNotFound.REPLACE_OR_PREPEND, self.replacement_text, expected_line_ranges=[FileLineRange(0, 3)], expected_file_str=self.test_file_str_prepend_expected_output_with_3_2, expected_lines_inserted_or_replaced=[FileLineRange(0, 2)], desired_preceding_newlines=3, desired_trailing_newlines=2)
    
    def test_append_with_desired_newlines(self):
        self.newline_control_replace_with_asserts(self.test_file_str_append, ActionIfBlockNotFound.REPLACE_OR_APPEND, self.replacement_text, expected_line_ranges=[FileLineRange(3, 6)], expected_file_str=self.test_file_str_append_expected_output_with_3_2, expected_lines_inserted_or_replaced=[FileLineRange(3, 5)], desired_preceding_newlines=3, desired_trailing_newlines=2)
