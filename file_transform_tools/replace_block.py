#!/usr/bin/env python3

import sys
from file_transform_tools.util.cli import parse_args, ActionIfBlockNotFound
from file_transform_tools.re_pattern_library import patterns
from file_transform_tools.util.find_block import find_lines_to_replace, FileLineRange
from file_transform_tools.util.replace_or_insert import replace_or_insert_block, do_dry_run_with_diff
from file_transform_tools.util.backup import CreateBackupInstructions

def main():
    args = parse_args(patterns)

    # read replacement text
    if args.replacement == '-':
        replacement_text = sys.stdin.read()
    else:
        replacement_text = args.replacement

    error_count = 0
    try:
        # track the backup instructions so we can print them at the end
        if args.backup:
            create_backup_instructions = CreateBackupInstructions()
        else:
            create_backup_instructions = None

        for filename in args.filename:
            # find lines matching the pattern
            if args.pattern_name:
                pattern = patterns[args.pattern_name]['pat']
                line_ranges = find_lines_to_replace(filename, pattern=pattern, verbose=args.verbose)
                if len(line_ranges) == 0:
                    # we were asked to replace only, but there's nothing to replace
                    if args.action == ActionIfBlockNotFound.REPLACE_ONLY:
                        print("error: block not found but nothing to do without --append/-A or --prepend/-P")
                        error_count += 1
                    # we were asked to replace or append, there's nothing to replace, so we are appending.  modify the
                    # replacement str with -A's argument if any
                    elif args.action == ActionIfBlockNotFound.REPLACE_OR_APPEND:
                        replacement_text = args.append + replacement_text
                    # ditto for prepend
                    elif args.action == ActionIfBlockNotFound.REPLACE_OR_PREPEND:
                        replacement_text = replacement_text + args.prepend
            else:
                line_ranges = []

            # blank line control from -w option
            blank_line_control = args.blank_line_control
            if blank_line_control is not None:
                desired_preceding_newlines = blank_line_control[0]
                desired_trailing_newlines = blank_line_control[1]
            else:
                desired_preceding_newlines = None
                desired_trailing_newlines = None

            # do the replacement(s)
            try:
                if args.dry_run:
                    ret = do_dry_run_with_diff(filename, line_ranges=line_ranges, action=args.action, replacement_text=replacement_text, verbose=args.verbose, keep_temp_file=args.preserve_temp_file_dry_run, desired_preceding_newlines=desired_preceding_newlines, desired_trailing_newlines=desired_trailing_newlines)
                    error_count += ret
                else:
                    replace_or_insert_block(filename, line_ranges, action=args.action, replacement_text=replacement_text, outfile=args.outfile, verbose=args.verbose, create_backup=args.backup, create_backup_instructions=create_backup_instructions, desired_preceding_newlines=desired_preceding_newlines, desired_trailing_newlines=desired_trailing_newlines)
            except Exception as e:
                import traceback
                print("".join(traceback.format_exception(type(e), e, e.__traceback__)))
                error_count += 1
    finally:
        if create_backup_instructions is not None and not create_backup_instructions.is_empty():
            print(create_backup_instructions.get_instructions_str())

    if error_count > 0:
        return 1
    else:
        return 0

if __name__ == "__main__":
    sys.exit(main())