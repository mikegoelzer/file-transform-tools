import unittest
from file_transform_tools.util.find_block import FileLineRange
from file_transform_tools.util.cli import ActionIfBlockNotFound
from file_transform_tools.re_pattern_library import patterns
from test_helpers import TestHelpersMixin, ReplaceWithAssertMixin

class TestReplaceBlockBashRc(unittest.TestCase, TestHelpersMixin, ReplaceWithAssertMixin):
    maxDiff = None

    pat = patterns['bash_rc_export_path']['pat']

    test_replacement_text = """ZZZZZ
YYYYY
"""

    def test_replace_block_at_beginning_of_file(self):
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

        self.replace_with_asserts(test_file_str_contains_block_at_beginning_of_file, ActionIfBlockNotFound.REPLACE_ONLY, self.test_replacement_text, [FileLineRange(start_line=0, num_lines=4)], test_file_str_contains_block_at_beginning_of_file_expected_output, 1)

    def test_replace_block_at_end_of_file(self):
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
        self.replace_with_asserts(test_file_str_contains_block_at_end_of_file, ActionIfBlockNotFound.REPLACE_ONLY, self.test_replacement_text, [FileLineRange(start_line=8, num_lines=4)], test_file_str_contains_block_at_end_of_file_expected_output, 1)

    def test_replace_block_in_middle_of_file(self):
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
        self.replace_with_asserts(test_file_str_contains_block_in_middle_of_file, ActionIfBlockNotFound.REPLACE_ONLY, self.test_replacement_text, [FileLineRange(start_line=5, num_lines=4)], test_file_str_contains_block_in_middle_of_file_expected_output, 1)

    #
    # does not contain block tests
    #
    test_file_str_does_not_contain_block = """# (1)
# Lattice Diamond license (2)
# (3)
LATTICE_LICENSE_FILE=/usr/local/diamond/3.13/license/license.dat (4)
"""

    def test_replace_or_append_block(self):
        test_file_str_does_not_contain_block_expected_output_append = """# (1)
# Lattice Diamond license (2)
# (3)
LATTICE_LICENSE_FILE=/usr/local/diamond/3.13/license/license.dat (4)
ZZZZZ
YYYYY
"""
        self.replace_with_asserts(self.test_file_str_does_not_contain_block, ActionIfBlockNotFound.REPLACE_OR_APPEND, self.test_replacement_text, [], test_file_str_does_not_contain_block_expected_output_append, 0)

    def test_replace_or_prepend_block(self):
        test_file_str_does_not_contain_block_expected_output_prepend = """ZZZZZ
YYYYY
# (1)
# Lattice Diamond license (2)
# (3)
LATTICE_LICENSE_FILE=/usr/local/diamond/3.13/license/license.dat (4)
"""
        self.replace_with_asserts(self.test_file_str_does_not_contain_block, ActionIfBlockNotFound.REPLACE_OR_PREPEND, self.test_replacement_text, [], test_file_str_does_not_contain_block_expected_output_prepend, 0)

    def test_replace_only_block(self):
        self.replace_with_asserts(self.test_file_str_does_not_contain_block, ActionIfBlockNotFound.REPLACE_ONLY, "", [], self.test_file_str_does_not_contain_block, 0)

    def test_multiple_copies_of_block(self):
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

        self.replace_with_asserts(test_file_str_contains_multiple_copies_of_block, ActionIfBlockNotFound.REPLACE_ONLY, self.test_replacement_text, [FileLineRange(start_line=4, num_lines=4), FileLineRange(start_line=9, num_lines=4), FileLineRange(start_line=14, num_lines=4)], test_file_str_contains_multiple_copies_of_block_expected_output, 3)
