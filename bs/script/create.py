import os

from bs.script import archive
from bs.script.data import PreExecutionData
from bs.script_data import ScriptDataBS
from gplib.text.utils import uprint

def create_archive(pre_data:PreExecutionData, script_data:ScriptDataBS, archive_format):
    print('Backing up as: {}'.format(archive_format))

    archive_base_folder_path = script_data.BackupFilename[0] + pre_data.resolved_date_postfix
    dest_dir_path = script_data.BackupDestination
    archiver = archive.Archiver(pre_data.vfs_final, pre_data.dest_path, dest_dir_path, archive_base_folder_path, archive_format=archive_format)
    return archiver.archive_vfs(script_data, script_data.ArchiveMode)

def create_backup(pre_data:PreExecutionData, script_data:ScriptDataBS):
    backup_dest = script_data.BackupDestination
    if not os.path.exists(backup_dest):
        print('Error: Backup destination does not exist.')
        print('Backup destination: ' + '"' + backup_dest + '"')
        return False
    elif not os.path.isdir(backup_dest):
        print('Error: Backup destination is not a directory.')
        return False

    if pre_data.backup_to_delete:
        backup_to_delete_tempfile = pre_data.backup_to_delete + '.temp'
        os.replace(pre_data.backup_to_delete, backup_to_delete_tempfile)

    archive_format = script_data.ArchiveFormat
    if archive_format in ['zip', '7z']:
        success = create_archive(pre_data, script_data, archive_format=archive_format)
    else:
        print('ERROR: Unknown archive type: "' + archive_format + '"')
        success = False

    if pre_data.backup_to_delete:
        if success:
            os.remove(backup_to_delete_tempfile)
        else:
            os.replace(backup_to_delete_tempfile, pre_data.backup_to_delete)
            if os.path.exists(pre_data.backup_to_delete):
                os.remove(backup_to_delete_tempfile)

    return success
