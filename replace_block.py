#!/usr/bin/env python3

import os
import subprocess
import sys
import tempfile
from util.cli import parse_args, ActionIfBlockNotFound
from re_pattern_library import patterns
from util.find_block import find_lines_to_replace, FileLineRange

def replace_or_insert_block(filename, line_range:FileLineRange, action:ActionIfBlockNotFound, replacement_text:str="", outfile=None, verbose=False):
    # catch the case where there's nothing to replace and we were told to replace only
    if line_range.is_empty() and action == ActionIfBlockNotFound.REPLACE_ONLY:
        if verbose:
            print(f"block not found => doing nothing")
        return
    
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

    # generate the new file contents
    if line_range.is_empty():
        if action == ActionIfBlockNotFound.REPLACE_ONLY:
            # do nothing
            pass
        elif action == ActionIfBlockNotFound.REPLACE_OR_APPEND:
            # append the replacement text to the end of the file
            new_file_lines = file_lines + replacement_lines
        elif action == ActionIfBlockNotFound.REPLACE_OR_PREPEND:
            # prepend the replacement text to the beginning of the file
            new_file_lines = replacement_lines + file_lines
    else:
        new_file_lines = file_lines[0:line_range.start_line-1] + replacement_lines + file_lines[line_range.end_line:]

    # write the new file contents to the output file
    if verbose:
        print(f"new_file_lines = {new_file_lines}")
    if outfile:
        if verbose:
            print(f"After deleting lines {line_range.start_line} to {line_range.end_line} the contents will be placed in '{outfile}'")
        with open(outfile, 'w') as f:
            f.writelines(new_file_lines)
    else:
        with open(filename, 'w') as f:
            f.writelines(new_file_lines)

def do_dry_run_with_diff(filename, line_range:FileLineRange, action:ActionIfBlockNotFound, replacement_text:str="", verbose=False, keep_temp_file=False)->int:
    try:
        temp_out_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        replace_or_insert_block(filename, line_range, action=action, replacement_text=replacement_text, outfile=temp_out_file.name, verbose=verbose)
        temp_out_file.close()

        # show the diff
        subprocess.run(['delta', filename, temp_out_file.name], stdout=sys.stdout, stderr=sys.stderr)
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        if not keep_temp_file:
            os.unlink(temp_out_file.name)
        else:
            temp_file_new_name = f"{os.path.basename(filename)}.new"
            os.rename(temp_out_file.name, temp_file_new_name)
            print(f"Keeping temp file {temp_file_new_name}")
    return 0

def main():
    args = parse_args(patterns)

    pattern = patterns[args.pattern_name]['pat']

    line_range = find_lines_to_replace(args.filename, pattern=pattern, verbose=args.verbose)
    if line_range.is_empty() and args.action == ActionIfBlockNotFound.REPLACE_ONLY:
        print("error: block not found but nothing to do without --append/-A or --prepend/-P")
        return 1

    if args.replacement_text == '-':
        replacement_text = sys.stdin.read()
    else:
        replacement_text = args.replacement_text

    if args.dry_run:
        return do_dry_run_with_diff(args.filename, line_range, action=args.action, replacement_text=replacement_text, verbose=args.verbose, keep_temp_file=args.dry_run_preserve_temp_file)
    else:
        replace_or_insert_block(args.filename, line_range, action=args.action, replacement_text=replacement_text, outfile=args.outfile, verbose=args.verbose)
    return 0

if __name__ == "__main__":
    sys.exit(main())