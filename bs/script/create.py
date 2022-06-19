import os

from bs.script import archive
from bs.script.data import PreExecutionData
from gplib.text.utils import up

def create_archive(pre_data:PreExecutionData, script_data, archive_format):
    up.print('Backing up as: {}'.format(archive_format))

    archive_base_folder_path = script_data['BackupFileName'][0] + pre_data.resolved_date_postfix
    dest_dir_path = script_data['BackupDestination']
    archiver = archive.Archiver(pre_data.vfs_final, pre_data.dest_path, dest_dir_path, archive_base_folder_path, archive_format=archive_format)
    return archiver.archive_vfs(script_data, script_data['ArchiveMode'])

def create_backup(pre_data:PreExecutionData, script_data):
    up.print_header('Backup Start')

    backup_dest = script_data['BackupDestination']
    if not os.path.exists(backup_dest):
        up.print('Error: Backup destination does not exist.')
        up.print('Backup destination: ' + '"' + backup_dest + '"')
        return False
    elif not os.path.isdir(backup_dest):
        up.print('Error: Backup destination is not a directory.')
        return False

    if pre_data.backup_to_delete:
        backup_to_delete_tempfile = pre_data.backup_to_delete + '.temp'
        os.replace(pre_data.backup_to_delete, backup_to_delete_tempfile)

    archive_format = script_data['ArchiveFormat']
    if archive_format in ['zip', '7z']:
        success = create_archive(pre_data, script_data, archive_format=archive_format)
    else:
        up.print('ERROR: Unknown archive type: "' + archive_format + '"')
        success = False

    if pre_data.backup_to_delete:
        if success:
            os.remove(backup_to_delete_tempfile)
        else:
            os.replace(backup_to_delete_tempfile, pre_data.backup_to_delete)
            if os.path.exists(pre_data.backup_to_delete):
                os.remove(backup_to_delete_tempfile)

    up.print_footer('Backup End')
    return success
