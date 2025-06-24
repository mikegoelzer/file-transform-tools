import os
import subprocess
import sys
import tempfile
from typing import Optional
from file_transform_tools.util.find_block import FileLineRange
from file_transform_tools.util.cli import ActionIfBlockNotFound
from file_transform_tools.util.which import which_delta
from file_transform_tools.util.backup import backup_file, CreateBackupInstructions
from file_transform_tools.util.correct_newlines.correct_newlines import correct_newlines

def replace_or_insert_block(filename, line_ranges:list[FileLineRange], action:ActionIfBlockNotFound, replacement_text:str="", outfile=None, verbose=False, create_backup=False, create_backup_instructions:CreateBackupInstructions=None, line_ranges_inserted_or_replaced:Optional[list[FileLineRange]]=None, desired_preceding_newlines:int=None, desired_trailing_newlines:int=None):
    
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
