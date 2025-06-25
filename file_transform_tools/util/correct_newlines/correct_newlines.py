from file_transform_tools.util.find_block import FileLineRange
from file_transform_tools.util.correct_newlines.slim_replacement import get_num_leading_and_trailing_blank_lines_within_replacement_block

def correct_newlines(file_lines:list[str], line_ranges_inserted_or_replaced:list[FileLineRange], desired_preceding_newlines:int, desired_trailing_newlines:int)->list[str]:
    """
    Takes file_lines and for each line range that was inserted or replaced, adjusts the number of newlines before or after it to requested values.
    Returns modified file_lines.
    """

    #
    # Functions
    #
    def get_last_non_blank_line_idx_before_range_start(file_lines:list[str], modified_line_range:FileLineRange)->int|None:
        """
        Returns the last non-blank line before the modified range's start line.
        If the modified range starts right at the beginning of the file, we return None.
        Otherwise, return 0-indexed line offset of last non-blank.
        """
        # find the last non-blank line before modified_line_range.start
        last_leading_non_blank = None
        if modified_line_range.start_line > 0:
            for idx, line in enumerate(file_lines[:modified_line_range.start_line]):
                if line.strip() != '':
                    last_leading_non_blank = idx
        return last_leading_non_blank

    def get_first_trailing_non_blank_line_idx_after_range_end(file_lines:list[str], modified_line_range:FileLineRange)->int|None:
        """
        find the first non-blank line after modified_line_range.end.
        If there are none, because we are either already at the end of the file or it's just all blank lines until 
        the end of the file, then we return None.
        """
        first_trailing_non_blank = None
        if modified_line_range.end_line < len(file_lines):
            for idx, line in enumerate(file_lines[modified_line_range.end_line+1:]):
                if line.strip() != '':
                    first_trailing_non_blank = idx + modified_line_range.end_line+1
                    break
        return first_trailing_non_blank

    def get_leading_and_trailing_blank_ranges(file_lines:list[str], modified_line_range:FileLineRange)->tuple[FileLineRange|None,FileLineRange|None]:
        """
        Returns a tuple of two FileLineRange representing the leading blank lines range and the trailing blank lines range.
        Either element can be None -- if there are no leading blank lines, or if there are no trailing blank lines.
        """
        def get_leading_blank_range()->FileLineRange|None:
            """
            Gets the line range of the leading blank lines.  Returns None if there are no leading blank lines.
            """
            last_leading_non_blank = get_last_non_blank_line_idx_before_range_start(file_lines=file_lines, modified_line_range=modified_line_range)
            if last_leading_non_blank is not None:
                if last_leading_non_blank+1 < modified_line_range.start_line:
                    first_leading_blank_line = last_leading_non_blank+1
                else:
                    first_leading_blank_line = None
            else:
                first_leading_blank_line = None
            
            if modified_line_range.start_line==0 and modified_range_internal_leading_blanks==0:
                last_leading_blank_line = None
            else:
                last_leading_blank_line = modified_line_range.start_line-1+modified_range_internal_leading_blanks
        
            if first_leading_blank_line is None or last_leading_blank_line is None:
                return None
            else:
                return FileLineRange(first_leading_blank_line, last_leading_blank_line)

        def get_trailing_blank_range()->FileLineRange|None:
            """
            Gets the line range of the trailing blank lines.  Returns None if there are no trailing blank lines.
            """
            first_trailing_non_blank = get_first_trailing_non_blank_line_idx_after_range_end(file_lines=file_lines, modified_line_range=modified_line_range)
            if first_trailing_non_blank is not None:
                if first_trailing_non_blank >= modified_line_range.end_line:
                    last_trailing_blank_line = first_trailing_non_blank-1
                else:
                    last_trailing_blank_line = None
            else:
                last_trailing_blank_line = None

            if modified_line_range.end_line == len(modified_line_range):
                # already at the end of the file, so there cannot be any trailing blanks
                first_trailing_blank_line = None
            else:
                first_trailing_blank_line = modified_line_range.end_line+1-modified_range_internal_trailing_blanks
            
            if first_trailing_blank_line is None or last_trailing_blank_line is None:
                return None
            else:
                return FileLineRange(first_trailing_blank_line, last_trailing_blank_line)
        
        # get internal blank line counts within the replacement
        modified_range_internal_leading_blanks, modified_range_internal_trailing_blanks = get_num_leading_and_trailing_blank_lines_within_replacement_block(file_lines=file_lines, modified_line_range=modified_line_range)
        
        return get_leading_blank_range(), get_trailing_blank_range()
    
    #
    # Classes
    #

    class ReplaceLineRangeWith:
        def __init__(self, line_range:FileLineRange, replacement:list[str]):
            self.line_range = line_range
            self.replacement = replacement

    class InsertBeforeLine:
        def __init__(self, line:int, replacement:list[str]):
            self.line = line
            self.replacement = replacement

    class InsertAfterLine:
        def __init__(self, line:int, replacement:list[str]):
            self.line = line
            self.replacement = replacement

    #
    # Function body: correct_newlines
    #

    # Generate a list of all replacements to make to the file
    replacements:list[ReplaceLineRangeWith|InsertBeforeLine|InsertAfterLine] = []
    for modified_line_range in line_ranges_inserted_or_replaced:
        # these are the two blocks we want to replace
        leading_blank_lines_range, trailing_blank_lines_range = get_leading_and_trailing_blank_ranges(file_lines=file_lines, modified_line_range=modified_line_range)

        # hack:  to correct for an off-by-one error when the insertion is at the EOF
        if modified_line_range.end_line == len(file_lines) and desired_preceding_newlines is not None:
            desired_preceding_newlines += 1 # TODO: hack!

        # this is what we want to replace them with
        leading_blank_lines_replacement = []
        trailing_blank_lines_replacement = []
        if desired_preceding_newlines is not None:
            for i in range(0,desired_preceding_newlines):
                leading_blank_lines_replacement.append('\n')
        if desired_trailing_newlines is not None:
            for i in range(0,desired_trailing_newlines):
                trailing_blank_lines_replacement.append('\n')

        if leading_blank_lines_range is not None:
            replacements.append(ReplaceLineRangeWith(line_range=leading_blank_lines_range, replacement=leading_blank_lines_replacement))
        else:
            replacements.append(InsertBeforeLine(line=max(0,modified_line_range.start_line-1), replacement=leading_blank_lines_replacement))
        if trailing_blank_lines_range is not None:
            replacements.append(ReplaceLineRangeWith(line_range=trailing_blank_lines_range, replacement=trailing_blank_lines_replacement))
        else:
            replacements.append(InsertAfterLine(line=max(0,modified_line_range.end_line-1), replacement=trailing_blank_lines_replacement))

    # iterate over lines making all replacements
    new_file_lines = []
    skip = False
    skip_once = False
    for line_index, line in enumerate(file_lines):
        for replacement in replacements:
            if isinstance(replacement, ReplaceLineRangeWith):
                if line_index == replacement.line_range.start_line:
                    new_file_lines.extend(replacement.replacement)
                    skip = True
                    break
                elif line_index == replacement.line_range.end_line+1:
                    skip = False
                    break
            elif isinstance(replacement, InsertBeforeLine):
                if line_index == replacement.line:
                    new_file_lines.extend(replacement.replacement)
                    skip = False
            elif isinstance(replacement, InsertAfterLine):
                if line_index == replacement.line:
                    new_file_lines.append(line)
                    new_file_lines.extend(replacement.replacement)
                    skip_once = True
        if not skip and not skip_once:
            new_file_lines.append(line)
        if skip_once:
            skip = False
            skip_once = False
    
    return new_file_lines
