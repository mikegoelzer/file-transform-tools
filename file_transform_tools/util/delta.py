import shutil
import subprocess
import sys
import tempfile
import os
import traceback

def show_delta_diff(filename1:str, filename2:str):
    subprocess.run(['delta', filename1, filename2], stdout=sys.stdout, stderr=sys.stderr)

def str_to_temp_file(str:str, name:str=None)->str:
    # Create temporary files
    temp = tempfile.NamedTemporaryFile(mode='w', delete=False, prefix=name)
    
    try:
        # Write strings to temp files
        temp.write(str)
        
        # Close files to ensure all data is written
        temp.close() 
    except Exception as e:
        print(f"Error: {e} in str_to_temp_file: {traceback.format_exc()}")
        try:
            os.unlink(temp.name)
        except Exception as e:
            pass
        return None
    return temp.name

def show_delta_diff_strs(str1:str, str2:str, name1:str=None, name2:str=None):
    try:
        # create temp files
        temp1_filename = str_to_temp_file(str1, name=name1)
        temp2_filename = str_to_temp_file(str2, name=name2)
        if temp1_filename is None or temp2_filename is None:
            raise Exception("error: str_to_temp_file failed")

        # show delta diff
        show_delta_diff(temp1_filename, temp2_filename)
        
    finally:
        # Clean up temp files
        try:
            os.unlink(temp1_filename)
            os.unlink(temp2_filename)
        except Exception as e:
            pass

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