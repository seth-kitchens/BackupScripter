import os

from gplib.fs import utils as fs_utils
from bs.script import utils as b_util

def clean_invalids(data):
    def negative_to_none(x):
        if data[x] != None and data[x] < 0:
            data[x] = None
    negative_to_none('MaxBackups')
    negative_to_none('BackupOldAge')
    negative_to_none('BackupRecentAge')


def collect_pre_execution_info(execution_data, script_data):
    backup_destination = script_data['BackupDestination']
    backup_basename = script_data['BackupFileName'][0]
    backup_date_string = script_data['BackupFileNameDate']
    backup_extension = script_data['BackupFileName'][1]
    existing_backups = []
    if os.path.exists(backup_destination) and os.path.isdir(backup_destination):
        files = [f for f in os.listdir(backup_destination) if os.path.isfile(os.path.normpath(os.path.join(backup_destination, f)))]
        for filename in files:
            if b_util.is_file_backup(filename, backup_basename, backup_date_string, backup_extension):
                filepath = os.path.normpath(os.path.join(backup_destination, filename))
                existing_backups.append(filepath)
    execution_data['ExistingBackups'] = existing_backups


    max_backups = script_data['MaxBackups']
    old_age_secs = script_data['BackupOldAge']
    recent_age_secs = script_data['BackupRecentAge']
    pull_age_from_postfix = script_data['PullAgeFromPostfix']
    if pull_age_from_postfix:
        date_string = script_data['BackupFileNameDate']
    else:
        date_string = None
    def get_backup_age(path):
        if pull_age_from_postfix:
            return fs_utils.DateString.extract_timestamp(date_string, path)
        else:
            return os.path.getctime(path)

    if recent_age_secs != None:
        eb_recent = [f for f in existing_backups if fs_utils.is_within_age_seconds(f, upper=recent_age_secs, date_string=date_string)]
    else:
        eb_recent = []
    execution_data['ExistingBackupsRecent'] = eb_recent
    
    if old_age_secs != None:
        eb_old = [f for f in existing_backups if fs_utils.is_within_age_seconds(f, lower=old_age_secs, date_string=date_string)]
    else:
        eb_old = []
    execution_data['ExistingBackupsOld'] = eb_old

    eb_normal = execution_data['ExistingBackupsNormal'] = [f for f in existing_backups if (not f in eb_recent) and (not f in eb_old)]
    
    execution_data['BackupToDelete'] = None
    if max_backups != None and max_backups >= 1 and max_backups <= (len(eb_normal) + len(eb_recent)):
        if eb_recent:
            eb_overwrite = eb_recent
        else:
            eb_overwrite = eb_normal
        oldest = eb_overwrite[0]
        oldest_date = get_backup_age(oldest)
        for f in eb_overwrite:
            f_date = get_backup_age(f)
            if f_date < oldest_date:
                oldest = f
                oldest_date = f_date
        execution_data['BackupToDelete'] = oldest

    most_recent = None
    most_recent_ctime = None
    eb_total_size = 0
    for b in existing_backups:
        b_ctime = get_backup_age(b)
        eb_total_size += os.path.getsize(b)
        if most_recent == None:
            most_recent = b
            most_recent_ctime = b_ctime
        elif b_ctime > most_recent_ctime:
            most_recent = b
            most_recent_ctime = b_ctime
    execution_data['ExistingBackupsMostRecent'] = most_recent
    execution_data['ExistingBackupsTotalSize'] = eb_total_size
