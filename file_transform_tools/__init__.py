"""
file_transform_tools - Tools for transforming files using regex patterns

This package provides utilities for finding and replacing blocks of text in files
using regular expressions.

Main components:
- replace_block: Main function for replacing text blocks
- patterns: Pre-defined regex patterns
- FileLineRange: Class representing a range of lines in a file
"""

from file_transform_tools.replace_block import replace_or_insert_block
from file_transform_tools.re_pattern_library import patterns
from file_transform_tools.util.find_block import FileLineRange
from file_transform_tools.util.cli import ActionIfBlockNotFound

__version__ = "0.1.0"

__all__ = [
    'replace_or_insert_block',
    'patterns',
    'FileLineRange',
    'ActionIfBlockNotFound',
]
