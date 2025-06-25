#!/usr/bin/env python3

import os
import sys
import unittest

# tests in other files
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from file_transform_tools.util.correct_newlines.slim_replacement import TestSlimReplacementBlock
from file_transform_tools.re_pattern_library import patterns, TestPatterns
from test_find_block import TestFindLinesToReplaceBashRc
from test_replace_block import TestReplaceBlockBashRc
from test_helpers import TestHelpersMixin
from test_vectors import TestVectors
from test_slang_replacer import TestSlangReplacer, TestPrependAndAppendWithNewLineControl
from test_subprocess_invoke_replace_block import TestSubprocessInvokeReplaceBlock

class VerifyDeltaPresent(unittest.TestCase):
    def test_delta_present(self):
        import file_transform_tools.util.delta
        if not file_transform_tools.util.delta.which_delta(print_message=False):
            self.fail("delta not found in PATH")

# control which tests are skipped during debugging
skip_tests = [
    #VerifyDeltaPresent,
    #TestFindLinesToReplaceBashRc,
    #TestReplaceBlockBashRc,
    TestVectors,
    TestSlangReplacer,
    TestPrependAndAppendWithNewLineControl,
    TestSubprocessInvokeReplaceBlock,
    TestSlimReplacementBlock,
    TestPatterns,
]

def main():
    # Create a test suite combining all test classes
    suite = unittest.TestSuite()
    
    # Add all test cases from this file
    # if VerifyDeltaPresent not in skip_tests:
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(VerifyDeltaPresent))
    if TestFindLinesToReplaceBashRc not in skip_tests:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFindLinesToReplaceBashRc))
    if TestReplaceBlockBashRc not in skip_tests:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestReplaceBlockBashRc))
    if TestVectors not in skip_tests:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestVectors))
    if TestSlangReplacer not in skip_tests:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSlangReplacer))

    if TestPrependAndAppendWithNewLineControl not in skip_tests:
        # these tests are currently failing...
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPrependAndAppendWithNewLineControl))
    if TestSubprocessInvokeReplaceBlock not in skip_tests:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSubprocessInvokeReplaceBlock))

    # Add test cases from re_pattern_library.py
    if TestPatterns not in skip_tests:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPatterns))
    
    # Add tests from util/correct_newlines/slim_replacement.py
    if TestSlimReplacementBlock not in skip_tests:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSlimReplacementBlock))
    
    # Run the combined test suite
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    
    if result.wasSuccessful():
        if len(skip_tests) == 0:
            print("\n✅ all tests passed")
            return 0
        else:
            print(f"\n⚠️ all tests passed, but {len(skip_tests)} tests were skipped")
            return 0
    else:
        print("\n❌ some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
