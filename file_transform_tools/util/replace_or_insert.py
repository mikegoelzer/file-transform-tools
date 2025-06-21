import os
import subprocess
import sys
import tempfile
from typing import Optional
from file_transform_tools.util.find_block import FileLineRange
from file_transform_tools.util.cli import ActionIfBlockNotFound
from file_transform_tools.util.which import which_delta
from file_transform_tools.util.backup import backup_file, CreateBackupInstructions

def replace_or_insert_block(filename, line_ranges:list[FileLineRange], action:ActionIfBlockNotFound, replacement_text:str="", outfile=None, verbose=False, create_backup=False, create_backup_instructions:CreateBackupInstructions=None, line_ranges_inserted_or_replaced:Optional[list[FileLineRange]]=None, desired_preceding_newlines:int=None, desired_trailing_newlines:int=None):
    
    def correct_newlines(file_lines:list[str], line_ranges_inserted_or_replaced:list[FileLineRange], desired_preceding_newlines:int, desired_trailing_newlines:int)->list[str]:
        """
        Takes file_lines and for each line range that was inserted or replaced, adjusts the number of newlines before or after it to requested values.
        Returns modified file_lines.
        """

        #
        # Functions
        #
        def get_num_leading_and_trailing_blank_lines_within_replacement_block(modified_line_range:FileLineRange)->tuple[int,int]:
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
            for idx, line in enumerate(file_lines[modified_line_range.start_line:modified_line_range.end_line+1]):
                if line.strip() != '':
                    if first_non_blank_within_modified_block is None:
                        first_non_blank_within_modified_block = idx + modified_line_range.start_line
                    last_non_blank_within_modified_block = idx + modified_line_range.start_line
            
            
            assert (first_non_blank_within_modified_block is None and last_non_blank_within_modified_block is None) or (first_non_blank_within_modified_block is not None and last_non_blank_within_modified_block is not None), "sanity check: either they are both None or neither is None"

            if first_non_blank_within_modified_block is None:
                # entire insertion is blank lines, so add that number of blank lines to our count of leading blanks later on
                add_to_leading_blank_lines = len(modified_line_range)
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
                add_to_trailing_blank_lines = modified_line_range.end_line-last_non_blank_within_modified_block

            assert add_to_leading_blank_lines is not None and add_to_leading_blank_lines>=0, "this function should never return a none or negative"
            assert add_to_trailing_blank_lines is not None and add_to_trailing_blank_lines>=0, "this function should never return a none or negative"
            return add_to_leading_blank_lines, add_to_trailing_blank_lines

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
            modified_range_internal_leading_blanks, modified_range_internal_trailing_blanks = get_num_leading_and_trailing_blank_lines_within_replacement_block(modified_line_range=modified_line_range)
            
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

    #
    # Function body: replace_next_occurrence
    #

    def replace_next_occurrence(file_lines:list[str], replacement_lines:list[str], line_range:FileLineRange, line_ranges_inserted_or_replaced:list[FileLineRange])->list[str]:
        new_file_lines = file_lines[0:line_range.start_line] + replacement_lines + file_lines[line_range.end_line+1:]
        if line_ranges_inserted_or_replaced is not None:
            num_lines_being_replaced = len(line_range)
            num_lines_inserted_or_replaced = len(replacement_lines)
            increase_in_file_length = num_lines_inserted_or_replaced - num_lines_being_replaced # negative means decrease
            # we keep track of which line ranges in the final file were inserted/replaced by us for the final newline modification
            line_ranges_inserted_or_replaced.append(FileLineRange(line_range.start_line, line_range.end_line+increase_in_file_length))
        return new_file_lines
    
    #
    # Function body: replace_or_insert_block
    #

    # for debugging purposes, we will use an empty array passed in for line_ranges_inserted_or_replaced.
    # but if the param is omitted, we just init an empty list here
    if line_ranges_inserted_or_replaced is None:
        line_ranges_inserted_or_replaced = []
    
    # get input file into an array of lines
    with open(filename, 'r') as f:
        file_lines = f.readlines()
    
    # get replacement text into an array of lines
    if replacement_text and replacement_text != '-':
        replacement_lines = replacement_text.split('\n')
        replacement_lines = [line + '\n' for line in replacement_lines]

        # if replacement lines contains a single extra line at the end, remove it
        if len(replacement_lines) > 0 and replacement_lines[-1] == '\n':
            replacement_lines = replacement_lines[:-1]
    else:
        replacement_lines = []
    if verbose:
        print(f"replacement_lines = {replacement_lines}")

    # catch the case where there's nothing to replace and we were told to replace only
    if len(line_ranges) == 0:
        if action == ActionIfBlockNotFound.REPLACE_ONLY:
            if verbose:
                print(f"block not found => doing nothing")
            return
        elif action == ActionIfBlockNotFound.REPLACE_OR_APPEND:
            # append the replacement text to the end of the file
            new_file_lines = file_lines + replacement_lines
            # keep track of lines in final file that were inserted or replaced by us
            line_ranges_inserted_or_replaced = [FileLineRange(len(file_lines)+1, len(file_lines) + len(replacement_lines))]
        elif action == ActionIfBlockNotFound.REPLACE_OR_PREPEND:
            # prepend the replacement text to the beginning of the file
            new_file_lines = replacement_lines + file_lines
            # same idea as above
            line_ranges_inserted_or_replaced = [FileLineRange(1, len(replacement_lines)-1)]
    else:
        # if we have any line ranges, they should be non empty
        for line_range in line_ranges:
            assert not line_range.is_empty(), "if there are elements in line_ranges, they should never be empty"

        # because we have one or more non-empty line ranges, we treat any REPLACE_* action as equivalent to REPLACE_ONLY
        # if we were going to append or prepend, we would have done it in the if part of this if...else
        if action == ActionIfBlockNotFound.REPLACE_ONLY or action == ActionIfBlockNotFound.REPLACE_OR_APPEND or action == ActionIfBlockNotFound.REPLACE_OR_PREPEND:
            # loop over matches and replace each one
            new_file_lines = file_lines
            original_num_file_lines = len(file_lines)
            for line_range_index, line_range in enumerate(line_ranges):
                new_file_lines = replace_next_occurrence(new_file_lines, replacement_lines, line_range, line_ranges_inserted_or_replaced)

                # if we've shortened (or lengthened) the file, we need to adjust all the line ranges after this one
                new_num_file_lines = len(new_file_lines)
                if new_num_file_lines != original_num_file_lines:
                    new_line_ranges = line_ranges
                    for idx, line_range in enumerate(line_ranges[line_range_index+1:]):
                        new_line_ranges[line_range_index+1+idx] = FileLineRange(line_range.start_line + new_num_file_lines - original_num_file_lines, line_range.end_line + new_num_file_lines - original_num_file_lines)
                    line_ranges = new_line_ranges
                    original_num_file_lines = new_num_file_lines

    if verbose:
        print(f"new_file_lines = {new_file_lines}")
        print(f"line_ranges_inserted_or_replaced = {line_ranges_inserted_or_replaced}")

    # do final newline correction
    if (desired_preceding_newlines is not None) or (desired_trailing_newlines is not None):
        assert line_ranges_inserted_or_replaced is not None, "code mistake:you must pass an empty list for line_ranges_inserted_or_replaced if you want to use desired_preceding_newlines or desired_trailing_newlines"
        new_file_lines = correct_newlines(new_file_lines, line_ranges_inserted_or_replaced, desired_preceding_newlines, desired_trailing_newlines)

    # write the new file contents to the output file,  creating a backup of the input file if requested
    if outfile:
        if verbose:
            print(f"The output contents will be placed in '{outfile}'")
        with open(outfile, 'w') as f:
            f.writelines(new_file_lines)
    else:
        # overwrite original file
        if create_backup:
            backup_path = backup_file(filename)
        with open(filename, 'w') as f:
            f.writelines(new_file_lines)
        if create_backup and create_backup_instructions is not None:
            create_backup_instructions.append(filename, backup_path)

def do_dry_run_with_diff(filename, line_ranges:list[FileLineRange], action:ActionIfBlockNotFound, replacement_text:str="", verbose=False, keep_temp_file=False, desired_preceding_newlines:int=None, desired_trailing_newlines:int=None)->int:
    try:
        temp_out_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        replace_or_insert_block(filename, line_ranges, action=action, replacement_text=replacement_text, outfile=temp_out_file.name, verbose=verbose, desired_preceding_newlines=desired_preceding_newlines, desired_trailing_newlines=desired_trailing_newlines)
        temp_out_file.close()

        # show the diff if they have delta installed
        if not which_delta(print_message=True):
            return 1
        else:
            subprocess.run(['delta', filename, temp_out_file.name], stdout=sys.stdout, stderr=sys.stderr)
    except Exception as e:
        print(f"error (at line {sys.exc_info()[2].tb_lineno}): {e}")
        return 1
    finally:
        if not keep_temp_file:
            os.unlink(temp_out_file.name)
        else:
            temp_file_new_name = f"{os.path.basename(filename)}.new"
            os.rename(temp_out_file.name, temp_file_new_name)
            print(f"Keeping temp file {temp_file_new_name}")
    return 0
