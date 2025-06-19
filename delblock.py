#!/usr/bin/env python3

import re
import os
import argparse
import subprocess
import sys
import tempfile

COLOR_BLUE = '\033[94m'
COLOR_RESET = '\033[0m'

def find_lines_to_remove(filename, verbose=False)->tuple[int, int]:
    start_line = 0
    end_line = 0
    with open(filename, 'r') as f:
        lines = f.readlines()

    # Join lines with newline so we can match across them
    text = ''.join(lines)

    # Match: 3 lines of comment, middle one fixed, then export PATH
    pattern = re.compile(
        r"""
        ^((\s*\n)*)                              # Optional blank lines at the start
        ^\#.*\n                                  # First comment line
        ^\#.*github\.com/mikegoelzer/ecp5-first-steps.*\n  # Second line must contain the URL
        ^\#.*\n                                  # Third comment line (could be any comment)
        ^export\s+PATH=.*$                       # export PATH=...
        """, 
        re.MULTILINE | re.VERBOSE
    )

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
    parser = argparse.ArgumentParser(description="Delete a block of lines from a file")
    parser.add_argument("filename", type=str, help="The file to delete the block from")
    parser.add_argument("--verbose", '-v', action="store_true", help="Print verbose output")
    parser.add_argument("--outfile", '-o', type=str, help="Write output to this file instead of overwriting filename")
    parser.add_argument("--dry-run", '-d', action="store_true", help="Write updated file to a temp file and show diff")
    args = parser.parse_args()
    args.filename = os.path.abspath(os.path.expanduser(args.filename))

    if not args.outfile and not args.dry_run:
        # prompt the user to make sure overwrite is ok
        response = input(f"No -o/--outfile specified. Are you sure you want to overwrite '{args.filename}'? [y/N] ")
        if response.lower() != 'y':
            print("OK, aborting with nothing changed")
            sys.exit(1)

    return args

def delete_block(filename, delete_from_line, delete_to_line, outfile=None, verbose=False):
    with open(filename, 'r') as f:
        lines = f.readlines()
    lines = lines[0:delete_from_line-1] + lines[delete_to_line:]
    if outfile:
        if verbose:
            print(f"After deleting lines {delete_from_line} to {delete_to_line} you will have contents in '{outfile}'")
        with open(outfile, 'w') as f:
            f.writelines(lines)
    else:
        with open(filename, 'w') as f:
            f.writelines(lines)
    return 

def do_dry_run_with_diff(filename, start_line, end_line, verbose=False)->int:
    try:
        temp_out_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        delete_block(filename, start_line, end_line, outfile=temp_out_file.name, verbose=verbose)
        temp_out_file.close()

        # show the diff
        subprocess.run(['delta', filename, temp_out_file.name], stdout=sys.stdout, stderr=sys.stderr)
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        os.unlink(temp_out_file.name)
    return 0

def main():
    args = parse_args()
    start_line, end_line = find_lines_to_remove(args.filename, verbose=args.verbose)
    
    if start_line == 0 and end_line == 0:
        print("block not found; nothing to do")
        return 0

    if args.dry_run:
        do_dry_run_with_diff(args.filename, start_line, end_line, verbose=args.verbose)
    else:
        delete_block(args.filename, start_line, end_line, outfile=args.outfile, verbose=args.verbose)
    return 0

if __name__ == "__main__":
    sys.exit(main())