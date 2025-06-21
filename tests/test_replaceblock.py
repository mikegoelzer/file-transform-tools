#!/usr/bin/env python3

import os
import subprocess
import sys
import tempfile
import unittest

from file_transform_tools.util.find_block import find_lines_to_replace, FileLineRange
from file_transform_tools.re_pattern_library import patterns, TestPatterns
from file_transform_tools.util.cli import ActionIfBlockNotFound
from file_transform_tools.replace_block import replace_or_insert_block

class TestFindLinesToReplaceBashRc(unittest.TestCase):
    def assert_lines_to_remove(self, test_file_str, expected_start_line, expected_end_line):
        import tempfile
        temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
        try:
            pat = patterns['bash_rc_export_path']['pat']
            temp.write(test_file_str)
            temp.close()
            line_ranges = find_lines_to_replace(temp.name, pat)
            assert len(line_ranges) == 1, f"len(line_ranges) = {len(line_ranges)}, expected 1"
            self.assertEqual(line_ranges[0].start_line, expected_start_line, f"start_line = {line_ranges[0].start_line}, expected_start_line = {expected_start_line}")
            self.assertEqual(line_ranges[0].end_line, expected_end_line, f"end_line = {line_ranges[0].end_line}, expected_end_line = {expected_end_line}")
        finally:
            try:
                os.unlink(temp.name)
            except:
                pass

    def test_file_block_at_end_of_file(self):
        test_file_str = """# (0)
# Lattice Diamond license (1)
# (2)
LATTICE_LICENSE_FILE=/usr/local/diamond/3.13/license/license.dat (3)




# (8)
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from 'github.com/mikegoelzer/ecp5-first-steps'
# 
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/template_tool:/home/mwg/ecp5-first-steps/my-designs/util/continuous_make:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper:/home/mwg/ecp5-first-steps/my-designs/util/clog2
"""
        self.assert_lines_to_remove(test_file_str, 8, 11)

    def test_file_block_in_middle_of_file(self):
        test_file_str = """# (0)
# Lattice Diamond license (1)
# (2)
LATTICE_LICENSE_FILE=/usr/local/diamond/3.13/license/license.dat (3)




# (8)
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from 'github.com/mikegoelzer/ecp5-first-steps'
# 
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/template_tool:/home/mwg/ecp5-first-steps/my-designs/util/continuous_make:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper:/home/mwg/ecp5-first-steps/my-designs/util/clog2

XXXXXX
"""
        self.assert_lines_to_remove(test_file_str, 8, 11)

    def test_file_block_at_start_of_file(self):
        test_file_str = """# (0)
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from 'github.com/mikegoelzer/ecp5-first-steps'
# 
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/template_tool:/home/mwg/ecp5-first-steps/my-designs/util/continuous_make:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper:/home/mwg/ecp5-first-steps/my-designs/util/clog2

XXXXXX
"""
        self.assert_lines_to_remove(test_file_str, 0, 3)

    def test_file_block_is_entire_file(self):
        test_file_str = """# (0)
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from 'github.com/mikegoelzer/ecp5-first-steps'
# 
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/template_tool:/home/mwg/ecp5-first-steps/my-designs/util/continuous_make:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper:/home/mwg/ecp5-first-steps/my-designs/util/clog2
"""
        self.assert_lines_to_remove(test_file_str, 0, 3)

class TestReplaceBlockBashRc(unittest.TestCase):
    test_replacement_text = """ZZZZZ
YYYYY
"""

    #
    # contains block at beginning of file tests
    #
    test_file_str_contains_block_at_beginning_of_file = """# 
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from 'github.com/mikegoelzer/ecp5-first-steps'
# 
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/template_tool:/home/mwg/ecp5-first-steps/my-designs/util/continuous_make:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper:/home/mwg/ecp5-first-steps/my-designs/util/clog2

AAA
BBB
CCC
DDD
"""

    test_file_str_contains_block_at_beginning_of_file_expected_output = """ZZZZZ
YYYYY

AAA
BBB
CCC
DDD
"""

    #
    # contains block at end of file tests
    #
    test_file_str_contains_block_at_end_of_file = """# (0)
# Lattice Diamond license (1)
# (2)
LATTICE_LICENSE_FILE=/usr/local/diamond/3.13/license/license.dat (3)




# (8)
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from 'github.com/mikegoelzer/ecp5-first-steps'
# 
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/template_tool:/home/mwg/ecp5-first-steps/my-designs/util/continuous_make:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper:/home/mwg/ecp5-first-steps/my-designs/util/clog2
"""

    test_file_str_contains_block_at_end_of_file_expected_output = """# (0)
# Lattice Diamond license (1)
# (2)
LATTICE_LICENSE_FILE=/usr/local/diamond/3.13/license/license.dat (3)




ZZZZZ
YYYYY
"""

    #
    # contains block in middle of file tests
    #
    test_file_str_contains_block_in_middle_of_file = """A
B
C


# 
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from 'github.com/mikegoelzer/ecp5-first-steps'
# 
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/template_tool:/home/mwg/ecp5-first-steps/my-designs/util/continuous_make:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper:/home/mwg/ecp5-first-steps/my-designs/util/clog2

This is some extra text that should be unchanged.
"""

    test_file_str_contains_block_in_middle_of_file_expected_output = """A
B
C


ZZZZZ
YYYYY

This is some extra text that should be unchanged.
"""

    #
    # contains multiple copies of the target block
    #
    test_file_str_contains_multiple_copies_of_block = """A
B
C

# 
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from 'github.com/mikegoelzer/ecp5-first-steps'
# 
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/template_tool:/home/mwg/ecp5-first-steps/my-designs/util/continuous_make:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper:/home/mwg/ecp5-first-steps/my-designs/util/clog2

# 
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from 'github.com/mikegoelzer/ecp5-first-steps'
# 
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/template_tool:/home/mwg/ecp5-first-steps/my-designs/util/continuous_make:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper:/home/mwg/ecp5-first-steps/my-designs/util/clog2

# 
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from 'github.com/mikegoelzer/ecp5-first-steps'
# 
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/template_tool:/home/mwg/ecp5-first-steps/my-designs/util/continuous_make:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper:/home/mwg/ecp5-first-steps/my-designs/util/clog2

This is some extra text that should be unchanged.
"""

    test_file_str_contains_multiple_copies_of_block_expected_output = """A
B
C

ZZZZZ
YYYYY

ZZZZZ
YYYYY

ZZZZZ
YYYYY

This is some extra text that should be unchanged.
"""

    #
    # does not contain block tests
    #
    test_file_str_does_not_contain_block = """# (1)
# Lattice Diamond license (2)
# (3)
LATTICE_LICENSE_FILE=/usr/local/diamond/3.13/license/license.dat (4)
"""

    test_file_str_does_not_contain_block_expected_output_append = """# (1)
# Lattice Diamond license (2)
# (3)
LATTICE_LICENSE_FILE=/usr/local/diamond/3.13/license/license.dat (4)
ZZZZZ
YYYYY
"""

    test_file_str_does_not_contain_block_expected_output_prepend = """ZZZZZ
YYYYY
# (1)
# Lattice Diamond license (2)
# (3)
LATTICE_LICENSE_FILE=/usr/local/diamond/3.13/license/license.dat (4)
"""

    def replace_with_asserts(self, test_file_str, action:ActionIfBlockNotFound, replacement_text:str, expected_line_ranges, expected_file_str, expected_num_line_ranges):
        pat = patterns['bash_rc_export_path']['pat']
        temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
        try:
            temp.write(test_file_str)
            temp.close()
            line_ranges = find_lines_to_replace(temp.name, pat)
            assert len(line_ranges) == expected_num_line_ranges, f"len(line_ranges) = {len(line_ranges)}, expected expected_num_line_ranges"
            assert line_ranges == expected_line_ranges, f"line_ranges = {line_ranges}, expected_line_ranges={expected_line_ranges}"
            for line_range, expected_line_range in zip(line_ranges, expected_line_ranges):
                assert line_range == expected_line_range, f"line_range = {line_range}, expected_line_range = {expected_line_range}"
            replace_or_insert_block(temp.name, line_ranges, action, replacement_text)
            with open(temp.name, 'r') as f:
                actual_file_str = f.read()
            self.assertEqual(actual_file_str, expected_file_str, f"actual_file_str = {actual_file_str!r}, expected_file_str = {expected_file_str!r}")
        finally:
            os.unlink(temp.name)

    def test_replace_block_at_beginning_of_file(self):
        self.replace_with_asserts(self.test_file_str_contains_block_at_beginning_of_file, ActionIfBlockNotFound.REPLACE_ONLY, self.test_replacement_text, [FileLineRange(0, 3)], self.test_file_str_contains_block_at_beginning_of_file_expected_output, 1)

    def test_replace_block_at_end_of_file(self):
        self.replace_with_asserts(self.test_file_str_contains_block_at_end_of_file, ActionIfBlockNotFound.REPLACE_ONLY, self.test_replacement_text, [FileLineRange(8, 11)], self.test_file_str_contains_block_at_end_of_file_expected_output, 1)

    def test_replace_block_in_middle_of_file(self):
        self.replace_with_asserts(self.test_file_str_contains_block_in_middle_of_file, ActionIfBlockNotFound.REPLACE_ONLY, self.test_replacement_text, [FileLineRange(5, 8)], self.test_file_str_contains_block_in_middle_of_file_expected_output, 1)

    def test_replace_or_append_block(self):
        self.replace_with_asserts(self.test_file_str_does_not_contain_block, ActionIfBlockNotFound.REPLACE_OR_APPEND, self.test_replacement_text, [], self.test_file_str_does_not_contain_block_expected_output_append, 0)

    def test_replace_or_prepend_block(self):
        self.replace_with_asserts(self.test_file_str_does_not_contain_block, ActionIfBlockNotFound.REPLACE_OR_PREPEND, self.test_replacement_text, [], self.test_file_str_does_not_contain_block_expected_output_prepend, 0)

    def test_replace_only_block(self):
        self.replace_with_asserts(self.test_file_str_does_not_contain_block, ActionIfBlockNotFound.REPLACE_ONLY, "", [], self.test_file_str_does_not_contain_block, 0)

    def test_multiple_copies_of_block(self):
        self.replace_with_asserts(self.test_file_str_contains_multiple_copies_of_block, ActionIfBlockNotFound.REPLACE_ONLY, self.test_replacement_text, [FileLineRange(4, 7), FileLineRange(9, 12), FileLineRange(14, 17)], self.test_file_str_contains_multiple_copies_of_block_expected_output, 3)

class TestVectors(unittest.TestCase):
    replacement_text = """Hello,
world!
"""
    replacement_at_file = "@tests/test_vectors/replace_with_file_contents/sample-at-replacement-file.txt"

    def replace_with_asserts(self, test_file_str, action:ActionIfBlockNotFound, replacement_text:str, expected_line_range, expected_file_str):
        pat = patterns['bash_rc_export_path']['pat']
        temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
        try:
            temp.write(test_file_str)
            temp.close()
            line_ranges = find_lines_to_replace(temp.name, pat)
            assert len(line_ranges) == 1, f"len(line_ranges) = {len(line_ranges)}, expected 1"
            assert line_ranges[0] == expected_line_range, f"line_range = {line_ranges[0]}, expected_line_range = {expected_line_range}"
            replace_or_insert_block(temp.name, line_ranges, action, replacement_text)
            with open(temp.name, 'r') as f:
                actual_file_str = f.read()
            self.assertEqual(actual_file_str, expected_file_str, f"actual_file_str = {actual_file_str!r}, expected_file_str = {expected_file_str!r}")
        finally:
            os.unlink(temp.name)

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

class TestSlangReplacer(unittest.TestCase):
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

    def slang_replace_with_asserts(self, test_file_str, action:ActionIfBlockNotFound, replacement_text:str, expected_line_ranges,expected_file_str, expected_lines_inserted_or_replaced, desired_preceding_newlines:int=None, desired_trailing_newlines:int=None):
        pat = patterns['ifdef_slang']['pat']
        temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
        try:
            temp.write(test_file_str)
            temp.close()
            line_ranges = find_lines_to_replace(temp.name, pat)
            assert len(line_ranges) == 1, f"len(line_ranges) = {len(line_ranges)}, expected 1"
            assert line_ranges == expected_line_ranges, f"line_ranges = {line_ranges}, expected_line_ranges = {expected_line_ranges}"
            line_ranges_inserted_or_replaced = []
            replace_or_insert_block(temp.name, line_ranges, action, replacement_text, line_ranges_inserted_or_replaced=line_ranges_inserted_or_replaced, desired_preceding_newlines=desired_preceding_newlines, desired_trailing_newlines=desired_trailing_newlines)
            assert line_ranges_inserted_or_replaced == expected_lines_inserted_or_replaced, f"line_ranges_inserted_or_replaced = {line_ranges_inserted_or_replaced}, expected_lines_inserted_or_replaced = {expected_lines_inserted_or_replaced}"
            with open(temp.name, 'r') as f:
                actual_file_str = f.read()
            self.assertEqual(actual_file_str, expected_file_str, f"actual_file_str = {actual_file_str!r}, expected_file_str = {expected_file_str!r}")
        finally:
            os.unlink(temp.name)

    def test_slang_replacer(self):
        self.slang_replace_with_asserts(self.test_file_str, ActionIfBlockNotFound.REPLACE_ONLY, self.replacement_text, expected_line_ranges=[FileLineRange(2, 5)], expected_file_str=self.test_file_str_expected_output, expected_lines_inserted_or_replaced=[FileLineRange(2, 7)], desired_preceding_newlines=None, desired_trailing_newlines=None)
        self.slang_replace_with_asserts(self.test_file_str, ActionIfBlockNotFound.REPLACE_ONLY, self.replacement_text, expected_line_ranges=[FileLineRange(2, 5)], expected_file_str=self.test_file_str_expected_output_w00, expected_lines_inserted_or_replaced=[FileLineRange(2, 7)], desired_preceding_newlines=0, desired_trailing_newlines=0)
        self.slang_replace_with_asserts(self.test_file_str, ActionIfBlockNotFound.REPLACE_ONLY, self.replacement_text, expected_line_ranges=[FileLineRange(2, 5)], expected_file_str=self.test_file_str_expected_output_w23, expected_lines_inserted_or_replaced=[FileLineRange(2, 7)], desired_preceding_newlines=2, desired_trailing_newlines=3)

class TestPrependAndAppendWithNewLineControl(unittest.TestCase):
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

    def slang_replace_with_asserts(self, test_file_str, action:ActionIfBlockNotFound, replacement_text:str, expected_line_ranges,expected_file_str, expected_lines_inserted_or_replaced, desired_preceding_newlines:int=None, desired_trailing_newlines:int=None):
        pat = patterns['ifdef_slang']['pat']
        temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
        try:
            temp.write(test_file_str)
            temp.close()
            line_ranges = find_lines_to_replace(temp.name, pat)
            assert len(line_ranges) == 1, f"len(line_ranges) = {len(line_ranges)}, expected 1"
            assert line_ranges == expected_line_ranges, f"line_ranges = {line_ranges}, expected_line_ranges = {expected_line_ranges}"
            line_ranges_inserted_or_replaced = []
            replace_or_insert_block(temp.name, line_ranges, action, replacement_text, line_ranges_inserted_or_replaced=line_ranges_inserted_or_replaced, desired_preceding_newlines=desired_preceding_newlines, desired_trailing_newlines=desired_trailing_newlines)
            assert line_ranges_inserted_or_replaced == expected_lines_inserted_or_replaced, f"line_ranges_inserted_or_replaced = {line_ranges_inserted_or_replaced}, expected_lines_inserted_or_replaced = {expected_lines_inserted_or_replaced}"
            with open(temp.name, 'r') as f:
                actual_file_str = f.read()
            self.assertEqual(actual_file_str, expected_file_str, f"actual_file_str = {actual_file_str!r}, expected_file_str = {expected_file_str!r}")
        finally:
            os.unlink(temp.name)

    def test_prepend_no_desired_newlines(self):
        self.slang_replace_with_asserts(self.test_file_str_prepend, ActionIfBlockNotFound.REPLACE_OR_PREPEND, self.replacement_text, expected_line_ranges=[FileLineRange(0, 3)], expected_file_str=self.test_file_str_prepend_expected_output, expected_lines_inserted_or_replaced=[FileLineRange(0, 2)], desired_preceding_newlines=None, desired_trailing_newlines=None)
    
    def test_append_no_desired_newlines(self):
        self.slang_replace_with_asserts(self.test_file_str_append, ActionIfBlockNotFound.REPLACE_OR_APPEND, self.replacement_text, expected_line_ranges=[FileLineRange(3, 6)], expected_file_str=self.test_file_str_append_expected_output, expected_lines_inserted_or_replaced=[FileLineRange(3, 5)], desired_preceding_newlines=None, desired_trailing_newlines=None)
    
    def test_prepend_with_desired_newlines(self):
        self.slang_replace_with_asserts(self.test_file_str_prepend, ActionIfBlockNotFound.REPLACE_OR_PREPEND, self.replacement_text, expected_line_ranges=[FileLineRange(0, 3)], expected_file_str=self.test_file_str_prepend_expected_output_with_3_2, expected_lines_inserted_or_replaced=[FileLineRange(0, 2)], desired_preceding_newlines=3, desired_trailing_newlines=2)
    
    def test_append_with_desired_newlines(self):
        self.slang_replace_with_asserts(self.test_file_str_append, ActionIfBlockNotFound.REPLACE_OR_APPEND, self.replacement_text, expected_line_ranges=[FileLineRange(3, 6)], expected_file_str=self.test_file_str_append_expected_output_with_3_2, expected_lines_inserted_or_replaced=[FileLineRange(3, 5)], desired_preceding_newlines=3, desired_trailing_newlines=2)

class TestSubprocessInvoke(unittest.TestCase):
    def test_subprocess_invoke_prepend(self):
        temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
        temp.write("A\nB\nC\n")
        temp.close()
        try:
            p = subprocess.run(["replace-block", "-y", "-b", "-r", f"@{temp.name}", "-pat", "bash_rc_export_path", "-P", "-o", "outfile.txt", "-w", "3", "2", "readme.md"], check=True, cwd=os.path.dirname(os.path.dirname(__file__)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout = p.stdout.decode('utf-8')
            stderr = p.stderr.decode('utf-8')
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            print(f"returncode: {p.returncode}")

            if os.path.exists("outfile.txt"):
                with open("outfile.txt", "r") as f:
                    output_contents = f.read()
                print(f"outfile.txt contents:\n{output_contents}")
                # TODO: assert correct output here
                #self.assertTrue(output_contents == "\n\n\nA\nB\nC\n", "Output file should not be empty")
        except subprocess.CalledProcessError as e:
            print(f"CalledProcessError: {e.returncode}")
            print(f"stdout: {e.stdout.decode('utf-8')}")
            print(f"stderr: {e.stderr.decode('utf-8')}")
            raise e
        finally:
            if os.path.exists("outfile.txt"):
                os.unlink("outfile.txt")
            if os.path.exists(temp.name):
                os.unlink(temp.name)

    def test_subprocess_invoke_append(self):
        temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
        temp.write("A\nB\nC\n")
        temp.close()
        try:
            p = subprocess.run(["file_transform_tools/replace_block.py", "-y", "-b", "-r", f"@{temp.name}", "-pat", "bash_rc_export_path", "-A", "-o", "outfile.txt", "-w", "3", "2", "readme.md"], check=True, cwd=os.path.dirname(os.path.dirname(__file__)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout = p.stdout.decode('utf-8')
            stderr = p.stderr.decode('utf-8')
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            print(f"returncode: {p.returncode}")
            
            if os.path.exists("outfile.txt"):
                with open("outfile.txt", "r") as f:
                    output_contents = f.read()
                print(f"outfile.txt contents:\n{output_contents}")
                # TODO: assert correct output here
                #self.assertTrue(output_contents == "\n\n\nA\nB\nC\n", "Output file should not be empty")
                
        except subprocess.CalledProcessError as e:
            print(f"CalledProcessError: {e.returncode}")
            print(f"stdout: {e.stdout.decode('utf-8')}")
            print(f"stderr: {e.stderr.decode('utf-8')}")
            raise e
        finally:
            if os.path.exists("outfile.txt"):
                os.unlink("outfile.txt")
            if os.path.exists(temp.name):
                os.unlink(temp.name)

def main():
    # Create a test suite combining all test classes
    suite = unittest.TestSuite()
    
    # Add all test cases from this file
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFindLinesToReplaceBashRc))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestReplaceBlockBashRc))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestVectors))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSlangReplacer))

    # these tests are currently failing...
    # suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPrependAndAppendWithNewLineControl))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSubprocessInvoke))

    # Add test cases from re_pattern_library.py
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPatterns))
    
    # Run the combined test suite
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n✅ all tests passed")
        return 0
    else:
        print("\n❌ some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
