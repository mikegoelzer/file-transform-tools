import re
import sys
import unittest

# Match: 3 lines of comment, middle one fixed, then export PATH
bash_rc_export_path_pattern = re.compile(
    r"""
    ^\#.*\n                                  # First comment line
    ^\#.*github\.com.mikegoelzer/ecp5-first-steps.*\n  # Second line must contain the URL
    ^\#.*\n                                  # Third comment line (could be any comment)
    ^export\s+PATH=.*\n                      # export PATH=...
    (?:^export\s+RISC[^=]+=.*$\n)*            # zero or more export RISC*=... lines
    """, 
    re.MULTILINE | re.VERBOSE
)

ifdef_slang_pattern = re.compile(
    r"""
    ^\s*\`ifdef\s+SLANG.*\n                  # `ifdef SLANG
    ^(.*\n)*                                 # zero or more lines
    ^\s*\`endif.*$                           # `endif
    """, 
    re.MULTILINE | re.VERBOSE
)

patterns = {
    "bash_rc_export_path": {
        'pat': bash_rc_export_path_pattern, 
        'desc': 'for deleting lines at end of ~/.bashrc added by ~/ecp5-first-steps/my-designs/util/update_bashrc.sh'
    },
    "ifdef_slang": {
        'pat': ifdef_slang_pattern, 
        'desc': 'for modifying a block of lines that is wrapped in `ifdef SLANG ... `endif'
    },
}

#
# This unit test class is located here for easier visual inspection,
# but it is run from the main test module in tests/test_replaceblock.py
#
class TestPatterns(unittest.TestCase):
    def test_bash_rc_export_path(self):
        did_match = False
        for match in bash_rc_export_path_pattern.finditer("""
#
# Lattice Diamond license
#
LATTICE_LICENSE_FILE=/usr/local/diamond/3.13/license/license.dat

#
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from git@github.com:mikegoelzer/ecp5-first-steps.git
# 
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/template_tool:/home/mwg/ecp5-first-steps/my-designs/util/continuous_make:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper:/home/mwg/ecp5-first-steps/my-designs/util/clog2
"""):
            did_match = True
        self.assertTrue(did_match)

    def test_ifdef_slang(self):
        did_match = False
        for match in ifdef_slang_pattern.finditer("""
// This is the beginning of the file.

`ifdef SLANG  // maybe some comment
    `include "my_slang_file.sv"  // some comment
    `include "my_slang_file2.sv" // some other comment
`endif // maybe some comment

// This is the rest of the file...
"""):
            print(f"match.start() = {match.start()}, match.end() = {match.end()}")
            did_match = True
        self.assertTrue(did_match)

    def test_bash_rc_export_path_with_env_vars_run_twice(self):
        did_match = False
        file_str = """
#
# Lattice Diamond license
#
LATTICE_LICENSE_FILE=/usr/local/diamond/3.13/license/license.dat

#
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from git@github.com:mikegoelzer/ecp5-first-steps.git
# 
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/template_tool:/home/mwg/ecp5-first-steps/my-designs/util/continuous_make:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper:/home/mwg/ecp5-first-steps/my-designs/util/clog2
export FOO=bar
export BAR="baz"
export BAZ='qux'
"""
        for match in bash_rc_export_path_pattern.finditer(file_str):
            print(f"match.start() = {match.start()}, match.end() = {match.end()}")
            did_match = True
        self.assertTrue(did_match)

if __name__ == "__main__":
    result = unittest.main(exit=False)
    if result.result.wasSuccessful():
        print("✅ all tests passed!")
        sys.exit(0)
    else:
        print("❌ some tests failed")
        sys.exit(1)
