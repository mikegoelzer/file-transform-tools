from enum import Enum
import re
import sys
from typing import Generator, List
import unittest
from file_transform_tools.util.cli import COLOR_BLUE_BKG, COLOR_RESET, COLOR_RED_BKG, COLOR_GREEN_BKG, COLOR_YELLOW_BKG

bash_rc_export_path_pattern = re.compile(
    r"""
    ^\#.*\n                                  # First comment line
    ^\#.*github\.com.mikegoelzer/ecp5-first-steps.*\n  # Second line must contain the URL
    ^\#.*\n                                  # Third comment line (could be any comment)
    (^export\s+PATH=.*$\n)*                      # export PATH=...
    (^\s*\n)?                                    # optional empty line
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
        'desc': 'for deleting or replacing lines in ~/.bashrc added by ~/ecp5-first-steps/my-designs/util/update_bashrc.sh'
    },
    "ifdef_slang": {
        'pat': ifdef_slang_pattern, 
        'desc': 'for modifying a block of lines that is wrapped in `ifdef SLANG ... `endif'
    },
}

class PatternMatcherModifiers(Enum):
    NO_TRAILING_NEWLINES = 1

class ModifiedPatternMatcher:
    """
    A wrapper around a re.Pattern that allows for modifiers to be applied to each match
    that is found.  For example, one modifier will backtrack and remove any trailing
    newlines.

    The result is a list of (start_pos, end_pos) tuples that represent the first character
    position of the match and the first character position after the match.

    An empty list means no matches were found.
    """
    def __init__(self, s:str, pattern:re.Pattern, modifier:PatternMatcherModifiers=None):
        self.s = s
        self.pattern = pattern
        self.modifier = modifier

    def _make_modified_matches_list(self) -> List[tuple[int, int]]:
        """
        Returns a list of (start_pos, end_pos) tuples, with the modifier, if any, applied.
        """
        start_end_pos_list = []
        for match in self.pattern.finditer(self.s):
            start_end_pos = (match.start(), match.end())
            modified_start_end_pos = self._apply_modifier(start_end_pos)
            start_end_pos_list.append(modified_start_end_pos)
        return start_end_pos_list
    
    def _apply_modifier(self, start_end_pos:tuple[int, int]) -> tuple[int, int]:
        """
        Applies the modifier, if any, to the start_end_pos tuple.
        """
        start_pos, end_pos = start_end_pos
        if self.modifier == PatternMatcherModifiers.NO_TRAILING_NEWLINES:
            while end_pos > start_pos and self.s[end_pos-1] == '\n':
                end_pos -= 1
        return (start_pos, end_pos)

    def finditer(self) -> Generator[tuple[int, int], None, None]:
        """
        Returns a list of (start_pos, end_pos) tuples, with the modifier, if any, applied.
        """
        for (start_pos, end_pos) in self._make_modified_matches_list():
            yield (start_pos,end_pos)

#
# This unit test class is located here for easier visual inspection,
# but it is run from the main test module in tests/test_replaceblock.py
#
class TestPatterns(unittest.TestCase):
    disable_color=True
    
    def test_bash_rc_export_path(self):
        did_match = False
        s = """
#
# Lattice Diamond license
#
LATTICE_LICENSE_FILE=/usr/local/diamond/3.13/license/license.dat

#
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from git@github.com:mikegoelzer/ecp5-first-steps.git
# 
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/template_tool:/home/mwg/ecp5-first-steps/my-designs/util/continuous_make:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper:/home/mwg/ecp5-first-steps/my-designs/util/clog2
"""
        # for match in bash_rc_export_path_pattern.finditer(s):
        #     print(f"match.start() = {match.start()}, match.end() = {match.end()}")
        #     print(f"{COLOR_BLUE_BKG}{s[match.start():match.end()]}{COLOR_RESET}")
        #     did_match = True

        modified_pattern_matcher = ModifiedPatternMatcher(s, bash_rc_export_path_pattern, PatternMatcherModifiers.NO_TRAILING_NEWLINES)
        for (start_pos,end_pos) in modified_pattern_matcher.finditer():
            print(f"match.start() = {start_pos}, match.end() = {end_pos}")
            if not self.disable_color:
                print(f"{COLOR_GREEN_BKG}{s[start_pos:end_pos]}{COLOR_RESET}")
            else:
                print(f"{s[start_pos:end_pos]}")
            did_match = True

        self.assertTrue(did_match)

    def test_bash_rc_export_path_with_new_lines(self):
        did_match = False
        s = """
#
# Added by brew
#
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

#
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from git@github.com:mikegoelzer/ecp5-first-steps.git
#
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/clog2
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/parse_sv_enums
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/cache_tool4
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/slang-parse-tools

export RISC_REPO_ROOT=/home/mwg/ecp5-first-steps
export RISC_COMMON_DIR=/home/mwg/ecp5-first-steps/my-designs/common
export RISCV_DIR=/home/mwg/ecp5-first-steps/my-designs/riscv-soc/riscv
export RISCV_SOC_DIR=/home/mwg/ecp5-first-steps/my-designs/riscv-soc
"""
        # for match in bash_rc_export_path_pattern.finditer(s):
        #     print(f"match.start() = {match.start()}, match.end() = {match.end()}")
        #     print(f"{COLOR_BLUE_BKG}{s[match.start():match.end()]}{COLOR_RESET}")
        #     did_match = True
        modified_pattern_matcher = ModifiedPatternMatcher(s, bash_rc_export_path_pattern, PatternMatcherModifiers.NO_TRAILING_NEWLINES)
        for (start_pos,end_pos) in modified_pattern_matcher.finditer():
            print(f"match.start() = {start_pos}, match.end() = {end_pos}")
            if not self.disable_color:
                print(f"{COLOR_GREEN_BKG}{s[start_pos:end_pos]}{COLOR_RESET}")
            else:
                print(f"{s[start_pos:end_pos]}")
            did_match = True
        self.assertTrue(did_match)

    def test_bash_rc_export_path_with_no_riscv_lines(self):
        did_match = False
        s = """
#
# Added by brew
#
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

#
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from git@github.com:mikegoelzer/ecp5-first-steps.git
#
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/clog2
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/parse_sv_enums
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/cache_tool4
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/slang-parse-tools




"""
        # for match in bash_rc_export_path_pattern.finditer(s):
        #     print(f"match.start() = {match.start()}, match.end() = {match.end()}")
        #     print(f"{COLOR_YELLOW_BKG}{s[match.start():match.end()]}{COLOR_RESET}")
        #     did_match = True
        modified_pattern_matcher = ModifiedPatternMatcher(s, bash_rc_export_path_pattern, PatternMatcherModifiers.NO_TRAILING_NEWLINES)
        for (start_pos,end_pos) in modified_pattern_matcher.finditer():
            print(f"match.start() = {start_pos}, match.end() = {end_pos}")
            if not self.disable_color:
                print(f"{COLOR_GREEN_BKG}{s[start_pos:end_pos]}{COLOR_RESET}")
            else:
                print(f"{s[start_pos:end_pos]}")
            did_match = True
        self.assertTrue(did_match)

    def test_bash_rc_export_path_with_new_lines_and_two_blocks(self):
        did_match = False
        s = """
#
# Added by brew
#
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

#
# Added by /home/mwg/ecp5-first-steps/my-designs/util/update_bashrc.sh from git@github.com:mikegoelzer/ecp5-first-steps.git
#
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/slang_tb_gtkwave_helper
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/clog2
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/parse_sv_enums
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/build_helpers/cache_tool4
export PATH=$PATH:/home/mwg/ecp5-first-steps/my-designs/util/slang-parse-tools

export RISC_REPO_ROOT=/home/mwg/ecp5-first-steps
export RISC_COMMON_DIR=/home/mwg/ecp5-first-steps/my-designs/common
export RISCV_DIR=/home/mwg/ecp5-first-steps/my-designs/riscv-soc/riscv
export RISCV_SOC_DIR=/home/mwg/ecp5-first-steps/my-designs/riscv-soc

#
# Added by brew
#
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
"""
        # for match in bash_rc_export_path_pattern.finditer(s):
        #     print(f"match.start() = {match.start()}, match.end() = {match.end()}")
        #     print(f"{COLOR_BLUE_BKG}{s[match.start():match.end()]}{COLOR_RESET}")
        #     did_match = True
        modified_pattern_matcher = ModifiedPatternMatcher(s, bash_rc_export_path_pattern, PatternMatcherModifiers.NO_TRAILING_NEWLINES)
        for (start_pos,end_pos) in modified_pattern_matcher.finditer():
            print(f"match.start() = {start_pos}, match.end() = {end_pos}")
            if not self.disable_color:
                print(f"{COLOR_GREEN_BKG}{s[start_pos:end_pos]}{COLOR_RESET}")
            else:
                print(f"{s[start_pos:end_pos]}")
            did_match = True
        self.assertTrue(did_match)

    def test_ifdef_slang(self):
        did_match = False
        s = """
// This is the beginning of the file.

`ifdef SLANG  // maybe some comment
    `include "my_slang_file.sv"  // some comment
    `include "my_slang_file2.sv" // some other comment
`endif // maybe some comment

// This is the rest of the file...
"""
        # for match in ifdef_slang_pattern.finditer(s):
        #     print(f"match.start() = {match.start()}, match.end() = {match.end()}")
        #     print(f"{COLOR_BLUE_BKG}{s[match.start():match.end()]}{COLOR_RESET}")
        #     did_match = True
        modified_pattern_matcher = ModifiedPatternMatcher(s, ifdef_slang_pattern, modifier=PatternMatcherModifiers.NO_TRAILING_NEWLINES)
        for (start_pos,end_pos) in modified_pattern_matcher.finditer():
            print(f"match.start() = {start_pos}, match.end() = {end_pos}")
            if not self.disable_color:
                print(f"{COLOR_GREEN_BKG}{s[start_pos:end_pos]}{COLOR_RESET}")
            else:
                print(f"{s[start_pos:end_pos]}")
            did_match = True
        self.assertTrue(did_match)

    def test_bash_rc_export_path_with_env_vars_run_twice(self):
        did_match = False
        s = """
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
        # for match in bash_rc_export_path_pattern.finditer(s):
        #     print(f"match.start() = {match.start()}, match.end() = {match.end()}")
        #     print(f"{COLOR_BLUE_BKG}{s[match.start():match.end()]}{COLOR_RESET}")
        #     did_match = True
        modified_pattern_matcher = ModifiedPatternMatcher(s, bash_rc_export_path_pattern, PatternMatcherModifiers.NO_TRAILING_NEWLINES)
        for (start_pos,end_pos) in modified_pattern_matcher.finditer():
            print(f"match.start() = {start_pos}, match.end() = {end_pos}")
            if not self.disable_color:
                print(f"{COLOR_GREEN_BKG}{s[start_pos:end_pos]}{COLOR_RESET}")
            else:
                print(f"{s[start_pos:end_pos]}")
            did_match = True
        self.assertTrue(did_match)

if __name__ == "__main__":
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    result = test_runner.run(test_suite)
    if result.wasSuccessful():
        print("✅ all tests passed!")
        sys.exit(0)
    else:
        print("❌ some tests failed")
        sys.exit(1)
