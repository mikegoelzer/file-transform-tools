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
    parser = argparse.ArgumentParser(description="Replace or delete a multi-line block from a file")
    parser.add_argument("filename", type=str, nargs='?', help="The file to replace/delete the block from (required)")
    parser.add_argument("--pattern-name", '-p', type=str, help="The name of the pattern to match against (-l to list all patterns)")
    parser.add_argument("--list-patterns", '-l', action="store_true", help="List all patterns available for use")
    parser.add_argument("--verbose", '-v', action="store_true", help="Print verbose output")
    parser.add_argument("--outfile", '-o', type=str, help="Write output to this file instead of overwriting filename")
    parser.add_argument("--dry-run", '-d', action="store_true", help="Write updated file to a temp file and show diff")
    parser.add_argument("--dry-run-preserve-temp-file", '-dp', action="store_true", help="Same as --dry-run, but keep the temp file in '[filename].new' in current directory")
    parser.add_argument("--replacement-text", '-r', type=str, help="Text to replace the block with; '-' for stdin; if not text is provided, just deletes the block")
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--append", '-A', action="store_true", help="If matching block not found, just append the replacement text to file")
    group.add_argument("--prepend", '-P', action="store_true", help="If matching block not found, just prepend the replacement text to file")
    
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
            print(f"Error: pattern '{args.pattern_name}' not found in pattern library")
            sys.exit(1)
        if not args.filename:
            print("Error: filename is required")
            sys.exit(1)

    args.filename = os.path.abspath(os.path.expanduser(args.filename))

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
