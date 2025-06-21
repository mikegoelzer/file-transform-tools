#!/usr/bin/env python3

import sys
from util.cli import parse_args, ActionIfBlockNotFound
from re_pattern_library import patterns
from util.find_block import find_lines_to_replace, FileLineRange
from util.replace_or_insert import replace_or_insert_block, do_dry_run_with_diff

def main():
    args = parse_args(patterns)

    # read replacement text
    if args.replacement == '-':
        replacement_text = sys.stdin.read()
    else:
        replacement_text = args.replacement

    error_count = 0
    for filename in args.filename:
        # find lines matching the pattern
        if args.pattern_name:
            pattern = patterns[args.pattern_name]['pat']
            line_range = find_lines_to_replace(filename, pattern=pattern, verbose=args.verbose)
            if line_range.is_empty() and args.action == ActionIfBlockNotFound.REPLACE_ONLY:
                print("error: block not found but nothing to do without --append/-A or --prepend/-P")
                error_count += 1
        else:
            line_range = FileLineRange(0, 0)

        # do the replacement(s)
        try:
            if args.dry_run:
                ret = do_dry_run_with_diff(filename, line_range=line_range, action=args.action, replacement_text=replacement_text, verbose=args.verbose, keep_temp_file=args.dry_run_preserve_temp_file)
                error_count += ret
            else:
                replace_or_insert_block(filename, line_range, action=args.action, replacement_text=replacement_text, outfile=args.outfile, verbose=args.verbose)
        except Exception as e:
            print(f"error: {e}")
            error_count += 1
    
    if error_count > 0:
        return 1
    else:
        return 0

if __name__ == "__main__":
    sys.exit(main())