import shutil

def which_delta(print_message:bool=True) -> bool:
    """
    Check if 'delta' binary is available in PATH and print helpful message if not.
    Returns True if 'delta' is found, False otherwise.
    """
    if shutil.which('delta') is None:
        print("Error: 'delta' command not found in PATH")
        print("Please install delta:")
        print("  (macOS) brew install git-delta")
        print("  (Ubuntu/Debian) see readme.md for instructions to download and install the .deb package")
        return False
    return True
