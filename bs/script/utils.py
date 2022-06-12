from datetime import datetime

from gplib.fs import utils as fs_utils

def is_file_backup(filename:str, backup_basename:str, backup_date_string:str, backup_extension:str):
    if not filename.startswith(backup_basename):
        return False
    fn = filename[len(backup_basename):]
    if backup_extension:
        if not fn.endswith(backup_extension):
            return False
        fn = fn[:-1 * len(backup_extension)]
    
    if len(fn) < len(backup_date_string):
        return False
    
    if not fs_utils.DateString.matches(backup_date_string, fn):
        return False

    return True
