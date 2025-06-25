from file_transform_tools.util.find_block import find_lines_to_replace, FileLineRange
from file_transform_tools.re_pattern_library import patterns
import os
import tempfile
import unittest

class TestFindLinesToReplaceBashRc(unittest.TestCase):
    def assert_lines_to_remove(self, test_file_str:str, expected_start_line:int, expected_end_line:int):
        temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
        try:
            pat = patterns['bash_rc_export_path']['pat']
            temp.write(test_file_str)
            temp.close()
            line_ranges = find_lines_to_replace(temp.name, pat)
            assert len(line_ranges) == 1, f"len(line_ranges) = {len(line_ranges)}, expected 1"
            self.assertEqual(line_ranges[0].start_line, expected_start_line, f"start_line = {line_ranges[0].start_line}, expected_start_line = {expected_start_line}")
            self.assertEqual(line_ranges[0].num_lines, expected_end_line-expected_start_line+1, f"num_lines = {line_ranges[0].num_lines}, expected_num_lines = {expected_end_line-expected_start_line+1}")
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
