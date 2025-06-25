from file_transform_tools.util.find_block import FileLineRange
import unittest

def slim_replacement_block(file_lines:list[str], modified_line_range:FileLineRange)->list[FileLineRange]:
    """
    The replacement block itself may contain leading and/or trailing blank lines.  We need to slim down each element of modified_line_range
    to remove those leading and trailing blank lines from the range.

    Returns a new list of FileLineRange objects.
    """
    return modified_line_range

class TestSlimReplacementBlock(unittest.TestCase):
    file_lines_no_blanks = [
        "A",
        "B",
        "C",
        "D",
    ]
    file_lines_with_leading_blanks = [
        "",
        "A",
        "B",
        "C",
        "D",
    ]
    file_lines_with_trailing_blanks = [
        "A",
        "B",
        "C",
        "D",
        "",
    ]
    file_lines_with_leading_and_trailing_blanks = [
        "",
        "A",
        "B",
        "C",
        "D",
        "",
    ]
    modified_line_range_no_blanks = FileLineRange(start_line=0, num_lines=4)
    modified_line_range_with_leading_blanks = FileLineRange(start_line=1, num_lines=4)
    modified_line_range_with_trailing_blanks = FileLineRange(start_line=0, num_lines=4)
    modified_line_range_with_leading_and_trailing_blanks = FileLineRange(start_line=1, num_lines=4)

    def test_slim_replacement_block_no_blanks(self):
        self.assertEqual(slim_replacement_block(file_lines=self.file_lines_no_blanks, modified_line_range=self.modified_line_range_no_blanks), [self.modified_line_range_no_blanks])

    def test_slim_replacement_block_with_leading_blanks(self):
        self.assertEqual(slim_replacement_block(file_lines=self.file_lines_with_leading_blanks, modified_line_range=self.modified_line_range_with_leading_blanks), [FileLineRange(start_line=0, num_lines=4)])

    def test_slim_replacement_block_with_trailing_blanks(self):
        self.assertEqual(slim_replacement_block(file_lines=self.file_lines_with_trailing_blanks, modified_line_range=self.modified_line_range_with_trailing_blanks), [FileLineRange(start_line=0, num_lines=4)])

    def test_slim_replacement_block_with_leading_and_trailing_blanks(self):
        self.assertEqual(slim_replacement_block(file_lines=self.file_lines_with_leading_and_trailing_blanks, modified_line_range=self.modified_line_range_with_leading_and_trailing_blanks), [FileLineRange(start_line=0, num_lines=4)])

def get_num_leading_and_trailing_blank_lines_within_replacement_block(file_lines:list[str], modified_line_range:FileLineRange)->tuple[int,int]:
    """
    There may be leading or trailing blank lines inside the replacement block itself, so we need to keep track of that.
    Also, the block may be blank and entirely non-existant.

    The function returns the number of leading and trailing blank lines inside the block.  If the block is empty, obviously
    it returns zero for both.

    Does not return Nones.
    """

    if modified_line_range.is_empty():
        return 0,0

    # find the first and last non-blank lines in the modified block (if any)
    first_non_blank_within_modified_block = None
    last_non_blank_within_modified_block = None
    for idx, line in enumerate(file_lines[modified_line_range.start_line:modified_line_range.start_line+modified_line_range.num_lines]):
        if line.strip() != '':
            if first_non_blank_within_modified_block is None:
                first_non_blank_within_modified_block = idx + modified_line_range.start_line
            last_non_blank_within_modified_block = idx + modified_line_range.start_line
    
    
    assert (first_non_blank_within_modified_block is None and last_non_blank_within_modified_block is None) or (first_non_blank_within_modified_block is not None and last_non_blank_within_modified_block is not None), "sanity check: either they are both None or neither is None"

    if first_non_blank_within_modified_block is None:
        # entire insertion is blank lines, so add that number of blank lines to our count of leading blanks later on
        add_to_leading_blank_lines = modified_line_range.num_lines
    else:
        if first_non_blank_within_modified_block > 0:
            # zero or more leading blank lines inside replacement block, so that's how many we will add to our count of leading blank lines
            add_to_leading_blank_lines = first_non_blank_within_modified_block-modified_line_range.start_line
        else:
            # the first non-blank line is the first line of the modified block, so we don't need to add any leading blank lines
            add_to_leading_blank_lines = 0

    if last_non_blank_within_modified_block is None:
        # entire insertion is blank lines, but we accounted for it already with add_to_leading_blank_lines,
        # so we don't have to add any blanks at the end
        add_to_trailing_blank_lines = 0
    else:
        # zero or more trailing blank lines inside replacement block, so that's how many we will add to our count of trailing blank lines
        add_to_trailing_blank_lines = modified_line_range.num_lines-last_non_blank_within_modified_block

    assert add_to_leading_blank_lines is not None and add_to_leading_blank_lines>=0, "this function should never return a none or negative"
    assert add_to_trailing_blank_lines is not None and add_to_trailing_blank_lines>=0, "this function should never return a none or negative"
    return add_to_leading_blank_lines, add_to_trailing_blank_lines
