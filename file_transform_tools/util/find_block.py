import re
from file_transform_tools.util.file_line_range import FileLineRange
from file_transform_tools.re_pattern_library import ModifiedPatternMatcher, PatternMatcherModifiers

def find_lines_to_replace(filename, pattern:re.Pattern, verbose=False)->list[FileLineRange]:
    start_line = 0
    end_line = 0

    with open(filename, 'r') as f:
        lines = f.readlines()

    # Join lines with newline so we can match across them
    text = ''.join(lines)

    file_line_ranges = []
    modified_pattern_matcher = ModifiedPatternMatcher(text, pattern, PatternMatcherModifiers.NO_TRAILING_NEWLINES)
    for (start_pos,end_pos) in modified_pattern_matcher.finditer():
        start_char = start_pos
        end_char = end_pos

        # Compute line numbers
        start_line = text.count('\n', 0, start_char+1)
        end_line = text.count('\n', 0, end_char)

        if verbose:
            print(f"Match from line {start_line} to {end_line}")
            print(repr(text[start_pos:end_pos]))
    
        file_line_ranges.append(FileLineRange(start_line, end_line))
    
    return file_line_ranges
