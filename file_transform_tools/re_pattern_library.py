import re

# Match: 3 lines of comment, middle one fixed, then export PATH
bash_rc_export_path_pattern = re.compile(
    r"""
    ^\#.*\n                                  # First comment line
    ^\#.*github\.com/mikegoelzer/ecp5-first-steps.*\n  # Second line must contain the URL
    ^\#.*\n                                  # Third comment line (could be any comment)
    ^export\s+PATH=.*$                       # export PATH=...
    """, 
    re.MULTILINE | re.VERBOSE
)

patterns = {
    "bash_rc_export_path": {
        'pat': bash_rc_export_path_pattern, 
        'desc': 'for deleting lines at end of ~/.bashrc added by ~/ecp5-first-steps/my-designs/util/update_bashrc.sh'
    },
}