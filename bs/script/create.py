import os

from bs.script import archive
from gplib.text.utils import up

def create_backup_zip(execution_data, script_data):
    up.print('Backing up as: ZIP')
    vfs_final = execution_data['VfsFinal']

    archive_base_folder_path = script_data['BackupFileName'][0] + execution_data['ResolvedDateSuffix']
    dest_path = execution_data['DestPath']
    dest_dir_path = script_data['BackupDestination']
    archiver = archive.Archiver(vfs_final, dest_path, dest_dir_path, archive_base_folder_path)
    return archiver.archive_vfs(script_data)

def create_backup(execution_data, script_data):
    up.print_header('Backup Start')

    backup_dest = script_data['BackupDestination']
    if not os.path.exists(backup_dest):
        up.print('Error: Backup destination does not exist.')
        up.print('Backup destination: ' + '"' + backup_dest + '"')
        return False
    elif not os.path.isdir(backup_dest):
        up.print('Error: Backup destination is not a directory.')
        return False

    backup_to_delete = execution_data['BackupToDelete']
    if backup_to_delete:
        backup_to_delete_temp = backup_to_delete + '.temp'
        os.replace(backup_to_delete, backup_to_delete_temp)

    archive_type = script_data['ArchiveType']
    if archive_type == 'zip':
        success = create_backup_zip(execution_data, script_data)
    else:
        up.print('ERROR: Unknown archive type: "' + archive_type + '"')
        success = False

    if backup_to_delete:
        if success:
            os.remove(backup_to_delete_temp)
        else:
            os.replace(backup_to_delete_temp, backup_to_delete)

    up.print_footer('Backup End')
    return success
