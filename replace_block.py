#!/usr/bin/env python3

import re
import os
import argparse
import subprocess
import sys
import tempfile
from re_pattern_library import patterns

COLOR_BLUE = '\033[94m'
COLOR_RESET = '\033[0m'

def find_lines_to_replace(filename, pattern_name:str, verbose=False)->tuple[int, int]:
    start_line = 0
    end_line = 0
    with open(filename, 'r') as f:
        lines = f.readlines()

    # Join lines with newline so we can match across them
    text = ''.join(lines)

    pattern = patterns[pattern_name]['pat']

    for match in pattern.finditer(text):
        start_char = match.start()
        end_char = match.end()

        # Compute line numbers
        start_line = text.count('\n', 0, start_char) + 1
        end_line = text.count('\n', 0, end_char) + 1

        # does block occur at the end of the file?
        if end_line == len(lines):
            if verbose:
                print("Block occurs at the end of the file")
            block_occurs_at_end_of_file = True
        else:
            if verbose:
                print("Block does not occur at the end of the file")
            block_occurs_at_end_of_file = False

        # if there are any blank lines are the start, mark all but one of them for deletion
        # Except if the block occurs at the end of the file, then mark all for deletion
        blank_lines = match.group(1)
        num_blank_lines = len(blank_lines)
        if verbose:
            print(f"num blank lines = {num_blank_lines}")
        if not block_occurs_at_end_of_file:
            if num_blank_lines > 1:
                start_line += num_blank_lines - 1
            elif num_blank_lines == 1:
                    start_line += 1
        else:
            start_line += 0

        if verbose:
            print(f"Match from line {start_line} to {end_line}")
            print(repr(text[match.start():match.end()]))
    
    return start_line, end_line

def parse_args():
    parser = argparse.ArgumentParser(description="Replace or delete a multi-line block from a file")
    parser.add_argument("filename", type=str, nargs='?', help="The file to replace/delete the block from")
    parser.add_argument("--pattern-name", '-p', type=str, help="The name of the pattern to match against (-l to list all patterns)")
    parser.add_argument("--list-patterns", '-l', action="store_true", help="List all patterns available for use")
    parser.add_argument("--verbose", '-v', action="store_true", help="Print verbose output")
    parser.add_argument("--outfile", '-o', type=str, help="Write output to this file instead of overwriting filename")
    parser.add_argument("--dry-run", '-d', action="store_true", help="Write updated file to a temp file and show diff")
    parser.add_argument("--dry-run-preserve-temp-file", '-D', action="store_true", help="Same as --dry-run, but keep the temp file in 'filename.new' in current directory")
    parser.add_argument("--replacement-text", '-r', type=str, help="Text to replace the block with; '-' for stdin")
    args = parser.parse_args()

    if args.list_patterns:
        print("Available patterns:")
        for pattern_name in patterns:
            print(f"  {pattern_name.ljust(40)} {patterns[pattern_name]['desc']}")
        sys.exit(0)
    else:
        if not args.pattern_name:
            print("Error: -p/--pattern-name is required; use -l to list all patterns")
            sys.exit(1)
        if args.pattern_name not in patterns:
            print(f"Error: pattern '{args.pattern_name}' not found")
            sys.exit(1)
        if not args.filename:
            print("Error: -f/--filename is required; use -l to list all patterns")
            sys.exit(1)

    args.filename = os.path.abspath(os.path.expanduser(args.filename))

    if args.dry_run_preserve_temp_file:
        args.dry_run = True

    if not args.outfile and not args.dry_run:
        # prompt the user to make sure overwrite is ok
        response = input(f"No -o/--outfile specified. Are you sure you want to overwrite '{args.filename}'? [y/N] ")
        if response.lower() != 'y':
            print("OK, aborting with nothing changed")
            sys.exit(1)

    return args

def replace_block(filename, delete_from_line, delete_to_line, replacement_text:str="", outfile=None, verbose=False):
    with open(filename, 'r') as f:
        lines = f.readlines()
    if replacement_text and replacement_text != '-':
        replacement_lines = replacement_text.split('\n')
        replacement_lines = [line + '\n' for line in replacement_lines]
    else:
        replacement_lines = []
    if verbose:
        print(f"replacement_lines = {replacement_lines}")
    lines = lines[0:delete_from_line-1] + replacement_lines + lines[delete_to_line:]
    if verbose:
        print(f"lines = {lines}")
    if outfile:
        if verbose:
            print(f"After deleting lines {delete_from_line} to {delete_to_line} you will have contents in '{outfile}'")
        with open(outfile, 'w') as f:
            f.writelines(lines)
    else:
        with open(filename, 'w') as f:
            f.writelines(lines)
    return 

def do_dry_run_with_diff(filename, start_line, end_line, replacement_text:str="", verbose=False, keep_temp_file=False)->int:
    try:
        temp_out_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        replace_block(filename, start_line, end_line, replacement_text=replacement_text, outfile=temp_out_file.name, verbose=verbose)
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
    args = parse_args()
    start_line, end_line = find_lines_to_replace(args.filename, pattern_name=args.pattern_name, verbose=args.verbose)
    
    if start_line == 0 and end_line == 0:
        print("block not found; nothing to do")
        return 0

    if args.replacement_text == '-':
        replacement_text = sys.stdin.read()
    else:
        replacement_text = args.replacement_text

    if args.dry_run:
        do_dry_run_with_diff(args.filename, start_line, end_line, replacement_text=replacement_text, verbose=args.verbose, keep_temp_file=args.dry_run_preserve_temp_file)
    else:
        replace_block(args.filename, start_line, end_line, replacement_text=replacement_text, outfile=args.outfile, verbose=args.verbose)
    return 0

if __name__ == "__main__":
    sys.exit(main())