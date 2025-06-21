import os
import datetime
import shutil

def backup_file(filename):
    """
    Creates a backup copy of the given file in /tmp with a timestamp and full path encoded in name.
    
    Args:
        filename: Path to the file to backup
        
    Returns:
        str: Full path to the created backup file
        
    Example:
        '/home/user/.bashrc' -> '/tmp/home-user-.bashrc-20250621_120100.000000.bak'
    """

    filename = os.path.abspath(os.path.expanduser(filename))

    # Get just the filename without path
    base_filename = os.path.basename(filename)
    
    # Get directory path and convert / to - for filename safety
    dir_path = os.path.dirname(filename).lstrip('/')
    dir_path = dir_path.replace('/', '-')
    
    # Generate timestamp string
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S.%f")
    
    # Create backup filename with directory path included
    backup_path = f"/tmp/{dir_path}-{base_filename}-{timestamp}.bak"
    
    # Copy the file
    shutil.copy2(filename, backup_path)
    
    return backup_path

