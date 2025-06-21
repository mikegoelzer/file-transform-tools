import argparse
import os
import sys
from enum import Enum

class ActionIfBlockNotFound(Enum):
    """
    What to do if the block is not found
    """
    REPLACE_ONLY = "replace_only"
    REPLACE_OR_APPEND = "replace_or_append"
    REPLACE_OR_PREPEND = "replace_or_prepend"

def parse_args(patterns:dict[str, dict[str, str]])->argparse.Namespace:
    longest_pattern_name = max(len(pattern_name) for pattern_name in patterns)
    patterns_list = ""
    for pattern_name in patterns:
        patterns_list += f"  {pattern_name.ljust(longest_pattern_name+2)} {patterns[pattern_name]['desc']}\n"

    parser = argparse.ArgumentParser(description="Replace or delete a multi-line block from a file", 
                                     formatter_class=argparse.RawDescriptionHelpFormatter, 
                                     epilog=f"""

    -o/--outfile and --dry-run/--dry-run-preserve-temp-file are mutually exclusive concepts.

    Available patterns (see `re_pattern_library.py` for details):

    {patterns_list}

    Examples:

    Replace the block in ~/.bashrc with a string from the command line (dry run, no overwrite):
        replace_block -r "export PATH=/usr/local/bin:$PATH" -pat bash_rc_export_path ~/.bashrc

    Replace the block with the contents of 'replacement.txt' (dry run, no overwrite):
        replace_block -r- -pat bash_rc_export_path --dry-run tests/test_vectors/replace_block_debug_input.txt < replacement.txt
    """)
    parser.add_argument("filename", type=str, nargs='+', help="One or more input files to replace/delete/insert into (required)")
    parser.add_argument("--pattern-name", '-pat', type=str, help="The name of the pattern to match against (-h to list all patterns)")
    parser.add_argument("--replacement", '-r', type=str, help="Text to replace the block with; if no text is provided, the matching block is deleted; '-' for stdin, '@somefile' to read from a file")
    
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--outfile", '-o', type=str, help="Write output to this file instead of overwriting filename")
    output_group.add_argument("--dry-run", '-dry', action="store_true", help="Write updated file to a temp file and show diff")
    output_group.add_argument("--dry-run-preserve-temp-file", '-dryp', action="store_true", help="Implies --dry-run, but save the temp file as '[filename].new' in current directory")
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--append", '-A', action="store_true", help="If matching block not found, just append the replacement text to file")
    group.add_argument("--prepend", '-P', action="store_true", help="If matching block not found, just prepend the replacement text to file")

    parser.add_argument("--verbose", '-v', action="store_true", help="Print verbose output")

    args = parser.parse_args()

    if not args.append and not args.prepend:
        if not args.pattern_name:
            print("Error: -pat/--pattern-name is required; see -h for help")
            sys.exit(1)
        if args.pattern_name not in patterns:
            print(f"Error: pattern '{args.pattern_name}' not found in pattern library")
            sys.exit(1)
    if not args.filename:
        print("Error: filename is required")
        sys.exit(1)

    if len(args.filename) == 1:
        args.filename = [os.path.abspath(os.path.expanduser(args.filename[0]))]
    else:
        if args.outfile is not None:
            print("error: -o/--outfile is not supported with multiple files; use dry run if you don't want to overwrite")
            sys.exit(1)
        files = []
        for filename in args.filename:
            if not os.path.exists(filename):
                print(f"error: file '{filename}' not found")
                sys.exit(1)
            files.append(os.path.abspath(os.path.expanduser(filename)))
        args.filename = files

    if args.replacement and args.replacement.startswith('@'):
        if not os.path.exists(args.replacement[1:]):
            print(f"error: replacement file '{args.replacement[1:]}' not found")
            sys.exit(1)
        else:
            args.replacement = open(args.replacement[1:], 'r').read()

    if args.append:
        args.action = ActionIfBlockNotFound.REPLACE_OR_APPEND
    elif args.prepend:
        args.action = ActionIfBlockNotFound.REPLACE_OR_PREPEND
    else:
        args.action = ActionIfBlockNotFound.REPLACE_ONLY

    if args.dry_run_preserve_temp_file:
        args.dry_run = True

    if not args.outfile and not args.dry_run:
        # prompt the user to make sure overwrite is ok
        response = input(f"No -o/--outfile specified. Are you sure you want to overwrite '{args.filename}'? [y/N] ")
        if response.lower() != 'y':
            print("OK, aborting with nothing changed")
            sys.exit(1)

    return args
