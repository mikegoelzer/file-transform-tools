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

class CreateBackupInstructions():
    def __init__(self, color_enabled=True):
        self.color_enabled = color_enabled
        self.backup_files_map:dict[str, str] = {}

    def is_empty(self)->bool:
        return len(self.backup_files_map) == 0
    
    def append(self, filename:str, backup_filename:str):
        filename = os.path.abspath(filename)
        backup_filename = os.path.abspath(backup_filename)
        self.backup_files_map[filename] = backup_filename
    
    def get_instructions_str(self)->str:
        if self.color_enabled:
            COLOR_YELLOW = '\033[93m'
            COLOR_RESET = '\033[0m'
            COLOR_BOLD = '\033[1m'
        else:
            COLOR_YELLOW = ''
            COLOR_RESET = ''
            COLOR_BOLD = ''
        s = "To view the changes:\n" 
        for filename, backup_filename in self.backup_files_map.items():
            s += f"  {COLOR_YELLOW}delta {backup_filename} {filename}{COLOR_RESET}\n\n"
        s += "To revert the overwritten file(s):\n" 
        for filename, backup_filename in self.backup_files_map.items():
            s += f"  {COLOR_YELLOW}mv {backup_filename} {filename}{COLOR_RESET}  # restores {COLOR_BOLD}{os.path.basename(filename)}{COLOR_RESET}\n"
        return s
