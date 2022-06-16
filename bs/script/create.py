import os

from bs.script import archive
from bs.script.data import PreExecutionData
from gplib.text.utils import up

def create_archive(pe_data:PreExecutionData, script_data, compression_format):
    up.print('Backing up as: {}'.format(compression_format))

    archive_base_folder_path = script_data['BackupFileName'][0] + pe_data.resolved_date_postfix
    dest_dir_path = script_data['BackupDestination']
    archiver = archive.Archiver(pe_data.vfs_final, pe_data.dest_path, dest_dir_path, archive_base_folder_path, compression_format=compression_format)
    return archiver.archive_vfs(script_data)

def create_backup(pe_data:PreExecutionData, script_data):
    up.print_header('Backup Start')

    backup_dest = script_data['BackupDestination']
    if not os.path.exists(backup_dest):
        up.print('Error: Backup destination does not exist.')
        up.print('Backup destination: ' + '"' + backup_dest + '"')
        return False
    elif not os.path.isdir(backup_dest):
        up.print('Error: Backup destination is not a directory.')
        return False

    if pe_data.backup_to_delete:
        backup_to_delete_temp = pe_data.backup_to_delete + '.temp'
        os.replace(pe_data.backup_to_delete, backup_to_delete_temp)

    archive_type = script_data['ArchiveType']
    if archive_type in ['zip', '7z']:
        success = create_archive(pe_data, script_data, compression_format=archive_type)
    else:
        up.print('ERROR: Unknown archive type: "' + archive_type + '"')
        success = False

    if pe_data.backup_to_delete:
        if success:
            os.remove(backup_to_delete_temp)
        else:
            os.replace(backup_to_delete_temp, pe_data.backup_to_delete)

    up.print_footer('Backup End')
    return success
