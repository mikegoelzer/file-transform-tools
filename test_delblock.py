#!/usr/bin/env python3

import os
import sys
import unittest
from delblock import find_lines_to_remove

class TestDelBlock(unittest.TestCase):
    def assert_lines_to_remove(self, test_file_str, expected_start_line, expected_end_line):
        import tempfile
        temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
        try:
            temp.write(test_file_str)
            temp.close()
            start_line, end_line = find_lines_to_remove(temp.name)
            self.assertEqual(start_line, expected_start_line, f"start_line = {start_line}, expected_start_line = {expected_start_line}")
            self.assertEqual(end_line, expected_end_line, f"end_line = {end_line}, expected_end_line = {expected_end_line}")
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
        self.assert_lines_to_remove(test_file_str, 5, 12)

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
        self.assert_lines_to_remove(test_file_str, 8, 12)

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
