#!/usr/bin/env python3

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util.find_block import find_lines_to_replace, FileLineRange
from re_pattern_library import patterns
from util.cli import ActionIfBlockNotFound
from replace_block import replace_or_insert_block

class TestFindLinesToReplaceBashRc(unittest.TestCase):
    def assert_lines_to_remove(self, test_file_str, expected_start_line, expected_end_line):
        import tempfile
        temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
        try:
            pat = patterns['bash_rc_export_path']['pat']
            temp.write(test_file_str)
            temp.close()
            line_range = find_lines_to_replace(temp.name, pat)
            self.assertEqual(line_range.start_line, expected_start_line, f"start_line = {line_range.start_line}, expected_start_line = {expected_start_line}")
            self.assertEqual(line_range.end_line, expected_end_line, f"end_line = {line_range.end_line}, expected_end_line = {expected_end_line}")
        finally:
            try:
                os.unlink(temp.name)
            except:
                pass

    def test_file_block_at_end_of_file(self):
        test_file_str = """# (1)
# Lattice Diamond license (2)
# (3)
LATTICE_LICENSE_FILE=/usr/local/diamond/3.13/license/license.dat (4)




# (9)
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from 'github.com/mikegoelzer/ecp5-first-steps'
# 
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/template_tool:/home/mwg/ecp5-first-steps/my-designs/util/continuous_make:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper:/home/mwg/ecp5-first-steps/my-designs/util/clog2
"""
        self.assert_lines_to_remove(test_file_str, 9, 12)

    def test_file_block_in_middle_of_file(self):
        test_file_str = """# (1)
# Lattice Diamond license (2)
# (3)
LATTICE_LICENSE_FILE=/usr/local/diamond/3.13/license/license.dat (4)




# (9)
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from 'github.com/mikegoelzer/ecp5-first-steps'
# 
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/template_tool:/home/mwg/ecp5-first-steps/my-designs/util/continuous_make:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper:/home/mwg/ecp5-first-steps/my-designs/util/clog2

XXXXXX
"""
        self.assert_lines_to_remove(test_file_str, 9, 12)

    def test_file_block_at_start_of_file(self):
        test_file_str = """# (1)
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from 'github.com/mikegoelzer/ecp5-first-steps'
# 
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/template_tool:/home/mwg/ecp5-first-steps/my-designs/util/continuous_make:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper:/home/mwg/ecp5-first-steps/my-designs/util/clog2

XXXXXX
"""
        self.assert_lines_to_remove(test_file_str, 1, 4)

    def test_file_block_is_entire_file(self):
        test_file_str = """# (1)
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from 'github.com/mikegoelzer/ecp5-first-steps'
# 
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/template_tool:/home/mwg/ecp5-first-steps/my-designs/util/continuous_make:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper:/home/mwg/ecp5-first-steps/my-designs/util/clog2
"""
        self.assert_lines_to_remove(test_file_str, 1, 4)

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
    test_file_str_contains_block_at_end_of_file = """# (1)
# Lattice Diamond license (2)
# (3)
LATTICE_LICENSE_FILE=/usr/local/diamond/3.13/license/license.dat (4)




# (9)
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from 'github.com/mikegoelzer/ecp5-first-steps'
# 
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/template_tool:/home/mwg/ecp5-first-steps/my-designs/util/continuous_make:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper:/home/mwg/ecp5-first-steps/my-designs/util/clog2
"""

    test_file_str_contains_block_at_end_of_file_expected_output = """# (1)
# Lattice Diamond license (2)
# (3)
LATTICE_LICENSE_FILE=/usr/local/diamond/3.13/license/license.dat (4)




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

    def replace_with_asserts(self, test_file_str, action:ActionIfBlockNotFound, replacement_text:str, expected_line_range, expected_file_str):
        pat = patterns['bash_rc_export_path']['pat']
        temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
        try:
            temp.write(test_file_str)
            temp.close()
            line_range = find_lines_to_replace(temp.name, pat)
            assert line_range == expected_line_range, f"line_range = {line_range}, expected_line_range = {expected_line_range}"
            replace_or_insert_block(temp.name, line_range, action, replacement_text)
            with open(temp.name, 'r') as f:
                actual_file_str = f.read()
            self.assertEqual(actual_file_str, expected_file_str, f"actual_file_str = {actual_file_str!r}, expected_file_str = {expected_file_str!r}")
        finally:
            os.unlink(temp.name)

    def test_replace_block_at_beginning_of_file(self):
        self.replace_with_asserts(self.test_file_str_contains_block_at_beginning_of_file, ActionIfBlockNotFound.REPLACE_ONLY, self.test_replacement_text, FileLineRange(1, 4), self.test_file_str_contains_block_at_beginning_of_file_expected_output)

    def test_replace_block_at_end_of_file(self):
        self.replace_with_asserts(self.test_file_str_contains_block_at_end_of_file, ActionIfBlockNotFound.REPLACE_ONLY, self.test_replacement_text, FileLineRange(9, 12), self.test_file_str_contains_block_at_end_of_file_expected_output)

    def test_replace_block_in_middle_of_file(self):
        self.replace_with_asserts(self.test_file_str_contains_block_in_middle_of_file, ActionIfBlockNotFound.REPLACE_ONLY, self.test_replacement_text, FileLineRange(6, 9), self.test_file_str_contains_block_in_middle_of_file_expected_output)

    def test_replace_or_append_block(self):
        self.replace_with_asserts(self.test_file_str_does_not_contain_block, ActionIfBlockNotFound.REPLACE_OR_APPEND, self.test_replacement_text, FileLineRange(0, 0), self.test_file_str_does_not_contain_block_expected_output_append)

    def test_replace_or_prepend_block(self):
        self.replace_with_asserts(self.test_file_str_does_not_contain_block, ActionIfBlockNotFound.REPLACE_OR_PREPEND, self.test_replacement_text, FileLineRange(0, 0), self.test_file_str_does_not_contain_block_expected_output_prepend)

    def test_replace_only_block(self):
        self.replace_with_asserts(self.test_file_str_does_not_contain_block, ActionIfBlockNotFound.REPLACE_ONLY, "", FileLineRange(0, 0), self.test_file_str_does_not_contain_block)

class TestVectors(unittest.TestCase):
    replacement_text = """Hello,
world!
"""

    def replace_with_asserts(self, test_file_str, action:ActionIfBlockNotFound, replacement_text:str, expected_line_range, expected_file_str):
        pat = patterns['bash_rc_export_path']['pat']
        temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
        try:
            temp.write(test_file_str)
            temp.close()
            line_range = find_lines_to_replace(temp.name, pat)
            assert line_range == expected_line_range, f"line_range = {line_range}, expected_line_range = {expected_line_range}"
            replace_or_insert_block(temp.name, line_range, action, replacement_text)
            with open(temp.name, 'r') as f:
                actual_file_str = f.read()
            self.assertEqual(actual_file_str, expected_file_str, f"actual_file_str = {actual_file_str!r}, expected_file_str = {expected_file_str!r}")
        finally:
            os.unlink(temp.name)

    def test_replace_block_debug_input(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(f"{script_dir}/test_vectors/replace_block_debug_input.txt", 'r') as f:
            test_file_str = f.read()
        with open(f"{script_dir}/test_vectors/replace_block_debug_input.txt_expected", 'r') as f:
            expected_file_str = f.read()
        self.replace_with_asserts(test_file_str, ActionIfBlockNotFound.REPLACE_ONLY, self.replacement_text, FileLineRange(132, 135), expected_file_str)

def main():
    result = unittest.main(exit=False)
    if result.result.wasSuccessful():
        print("\n✅ all tests passed")
        return 0
    else:
        print("\n❌ some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
