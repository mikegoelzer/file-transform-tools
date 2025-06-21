from typing import NamedTuple
import re

class FileLineRange(NamedTuple):
    """
    Represent a range of lines in a file and whether they are at the end of the file.
    """
    start_line:int
    end_line:int

    def __str__(self):
        return f"{self.start_line}-{self.end_line}"

    def __repr__(self):
        return f"FileLineRange(start_line={self.start_line}, end_line={self.end_line})"
    
    def is_empty(self)->bool:
        return self.start_line == 0 and self.end_line == 0
    
def find_lines_to_replace(filename, pattern:re.Pattern, verbose=False)->FileLineRange:
    start_line = 0
    end_line = 0

    with open(filename, 'r') as f:
        lines = f.readlines()

    # Join lines with newline so we can match across them
    text = ''.join(lines)

    for match in pattern.finditer(text):
        start_char = match.start()
        end_char = match.end()

        # Compute line numbers
        start_line = text.count('\n', 0, start_char) + 1
        end_line = text.count('\n', 0, end_char) + 1

        if verbose:
            print(f"Match from line {start_line} to {end_line}")
            print(repr(text[match.start():match.end()]))
    
    return FileLineRange(start_line, end_line)
