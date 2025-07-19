import argparse
import os
import sys
from enum import Enum

COLOR_GREEN = '\033[92m'
COLOR_MAGENTA = '\033[95m'
COLOR_RESET = '\033[0m'
COLOR_BOLD = '\033[1m'
COLOR_ORANGE = '\033[93m'
COLOR_UNDERLINE = '\033[4m'
COLOR_ITALIC = '\033[3m'
COLOR_BLUE_BKG = '\033[44m'
COLOR_GREEN_BKG = '\033[42m'
COLOR_YELLOW_BKG = '\033[43m'
COLOR_RED_BKG = '\033[41m'
COLOR_CYAN_BKG = '\033[46m'
COLOR_WHITE_BKG = '\033[47m'

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
    for i, pattern_name in enumerate(patterns):
        patterns_list += f"  {('('+str(i+1)+')').ljust(4)} {pattern_name.ljust(longest_pattern_name+4)} {patterns[pattern_name]['desc']}\n"

    parser = argparse.ArgumentParser(description=f"{COLOR_GREEN}Replace, update, insert or delete a multi-line block in one or more files{COLOR_RESET}", 
                                     formatter_class=argparse.RawDescriptionHelpFormatter, 
                                     epilog=f"""

  {COLOR_MAGENTA}NOTES{COLOR_RESET}
  1. -o/--outfile and --dry-run/--dry-run-preserve-temp-file are mutually exclusive concepts
  2. Dry run options require the `delta` tool to be installed and in the PATH.  See readme.md for instructions.
  3. The optional arguments to -A and -P are {COLOR_UNDERLINE}only{COLOR_RESET} applied if no replacement is made.
  4. The optional argument to -A is a {COLOR_ITALIC}prefix{COLOR_RESET} to the insertion, while for -P it is a {COLOR_ITALIC}suffix{COLOR_RESET} to the insertion.

  {COLOR_MAGENTA}AVAILABLE PATTERNS{COLOR_RESET} 
  (see `re_pattern_library.py` for more info)

  {patterns_list}

  {COLOR_MAGENTA}EXAMPLES{COLOR_RESET}
  Replace the matching block in ~/.bashrc with a string (dry run, no overwrite):
    replace_block -r "export PATH=/usr/local/bin:$PATH" -pat bash_rc_export_path ~/.bashrc

  Replace the matching block with the contents of 'replacement.txt' (dry run, no overwrite):
    replace_block -r- -pat bash_rc_export_path --dry-run tests/test_vectors/replace_block_debug_input.txt < replacement.txt

  Try to replace the matching block with 'X=1', but if that's not found, append 'X=1' with a preceding newline (note that two are needed):
    replace-block -y -b -r "X=1" -pat bash_rc_export_path {COLOR_BOLD}{COLOR_ORANGE}-A $'\\n'{COLOR_RESET} --dry-run readme.md
  $'\\n' is a shell convention that inserts an actual newline instead of a backslash,n.
""")
    parser.add_argument("filename", type=str, nargs='+', help="One or more input files to replace/delete/insert into (required)")
    parser.add_argument("--pattern-name", '-pat', type=str, help="The name of the pattern to match against (-h to list all patterns)")
    parser.add_argument("--replacement", '-r', type=str, help="Text to replace the block with; if no text is provided, the matching block is deleted; '-' for stdin, '@somefile' to read from a file")
    parser.add_argument("--backup", '-b', action="store_true", help="Create a backup of the original file(s) in /tmp before overwriting")

    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--outfile", '-o', type=str, help="Write output to this file instead of overwriting filename")
    output_group.add_argument("--dry-run", '-dry', action="store_true", help="Write updated file to a temp file and show diff")
    output_group.add_argument("--preserve-temp-file-dry-run", '-pdry', action="store_true", help="Implies --dry-run, but save the temp file as '[filename].new' in current directory")
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--append", '-A', type=str, nargs='?', const="", help="If matching block not found, just append the replacement text to file. Argument string is an optional prefix for the replacement text if it is appended (default ''). If you provide anything here, it will probably be $'\\n' as shown in the examples.")
    group.add_argument("--prepend", '-P', type=str, nargs='?', const="", help="If matching block not found, just prepend the replacement text to file. Argument string is an optional suffix for the replacement text if it is prepended (default ''). If you provide anything here, it will probably be $'\\n' as shown in the examples.")

    parser.add_argument("--blank-line-control", '-w', type=int, nargs=2, metavar=('preceding', 'trailing'), help="Required number of preceding and trailing newlines that should exist after the insertion, deletion or replacement of the block")

    parser.add_argument('-y', action="store_true", help="Don't prompt about overwriting files")
    parser.add_argument("--verbose", '-v', action="store_true", help="Print verbose output")

    args = parser.parse_args()

    if args.append is None and args.prepend is None:
        if not args.pattern_name:
            print("Error: -pat/--pattern-name is required; see -h for help")
            sys.exit(1)
        if args.pattern_name not in patterns:
            print(f"Error: pattern '{args.pattern_name}' not found in pattern library")
            sys.exit(1)

    if not args.filename or len(args.filename) == 0:
        print("Error: at least one filename is required")
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

    if args.append is not None:
        args.action = ActionIfBlockNotFound.REPLACE_OR_APPEND
    elif args.prepend is not None:
        args.action = ActionIfBlockNotFound.REPLACE_OR_PREPEND
    else:
        args.action = ActionIfBlockNotFound.REPLACE_ONLY

    if args.preserve_temp_file_dry_run:
        args.dry_run = True

    if not args.outfile and not args.dry_run and not args.y:
        # prompt the user to make sure overwrite is ok
        response = input(f"No -o/--outfile specified. Are you sure you want to overwrite '{args.filename}'? [y/N] ")
        if response.lower() != 'y':
            print("OK, aborting with nothing changed")
            sys.exit(1)

    return args
