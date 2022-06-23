import os
from dataclasses import dataclass

from bs.fs.vfs import VFSBS as VFS, VirtualFSBS
from bs.script_data import ScriptDataBS
from gplib.fs import utils as fs_utils
from bs.script import utils as b_util

def clean_invalids(script_data:ScriptDataBS):
    sd_dict = script_data.to_dict()
    def negative_to_none(x):
        if sd_dict[x] != None and sd_dict[x] < 0:
            sd_dict[x] = None
    negative_to_none('MaxBackups')
    negative_to_none('BackupOldAge')
    negative_to_none('BackupRecentAge')
    script_data.load_dict(sd_dict)

@dataclass
class PreExecutionData:
    def __init__(self):
        self.resolved_date_postfix:str = None
        self.dest_filename:str = None
        self.dest_path:str = None

        self.vfsdata_static:VirtualFSBS.vfsdata = None
        self.vfsdata_final:VirtualFSBS.vfsdata = None

        self.existing_backups:list = None
        self.existing_backups_recent:list = None
        self.existing_backups_old:list = None
        self.existing_backups_normal:list = None
        self.backup_to_delete:str = None
        self.existing_backups_most_recent:str = None
        self.existing_backups_total_size:int = None

        self.vfs_final:VFS = None
    
    @classmethod
    def collect_data(cls, script_data:ScriptDataBS):
        vfs_static = VFS()
        pre_data = PreExecutionData()

        pre_data.resolved_date_postfix = fs_utils.DateString.process(script_data.BackupDatePostfix)
        pre_data.dest_filename = script_data.BackupFilename[0] + pre_data.resolved_date_postfix + script_data.BackupFilename[1]
        pre_data.dest_path = os.path.normpath(os.path.join(script_data.BackupDestination, pre_data.dest_filename))

        # Inclusion

        vfs_static.build_from_ie_lists(script_data.IncludedItems, script_data.ExcludedItems)
        vfs_final = vfs_static.clone()
        vfs_final.process_matching_groups_dict(script_data.MatchingGroupsList)
        pre_data.vfsdata_static = vfs_static.calc_vfsdata()
        pre_data.vfsdata_final = vfs_final.calc_vfsdata()
        pre_data.vfs_final = vfs_final

        backup_destination = script_data.BackupDestination
        backup_basename = script_data.BackupFilename[0]
        backup_date_string = script_data.BackupDatePostfix
        backup_extension = script_data.BackupFilename[1]
        pre_data.existing_backups = []
        if os.path.exists(backup_destination) and os.path.isdir(backup_destination):
            files = [f for f in os.listdir(backup_destination) if os.path.isfile(os.path.normpath(os.path.join(backup_destination, f)))]
            for filename in files:
                if b_util.is_file_backup(filename, backup_basename, backup_date_string, backup_extension):
                    filepath = os.path.normpath(os.path.join(backup_destination, filename))
                    pre_data.existing_backups.append(filepath)


        max_backups = script_data.MaxBackups
        old_age_secs = script_data.BackupOldAge
        recent_age_secs = script_data.BackupRecentAge
        pull_age_from_postfix = script_data.PullAgeFromPostfix
        if pull_age_from_postfix:
            date_string = script_data.BackupDatePostfix
        else:
            date_string = None
        def get_backup_age(path):
            if pull_age_from_postfix:
                return fs_utils.DateString.extract_timestamp(date_string, path)
            else:
                return os.path.getctime(path)

        if recent_age_secs != None:
            eb_recent = [f for f in pre_data.existing_backups if fs_utils.is_within_age_seconds(f, upper=recent_age_secs, date_string=date_string)]
        else:
            eb_recent = []
        pre_data.existing_backups_recent = eb_recent
        
        if old_age_secs != None:
            eb_old = [f for f in pre_data.existing_backups if fs_utils.is_within_age_seconds(f, lower=old_age_secs, date_string=date_string)]
        else:
            eb_old = []
        pre_data.existing_backups_old = eb_old

        eb_normal = pre_data.existing_backups_normal = [f for f in pre_data.existing_backups if (not f in eb_recent) and (not f in eb_old)]
        
        pre_data.backup_to_delete = None
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
            pre_data.backup_to_delete = oldest

        most_recent = None
        most_recent_ctime = None
        eb_total_size = 0
        for b in pre_data.existing_backups:
            b_ctime = get_backup_age(b)
            eb_total_size += os.path.getsize(b)
            if most_recent == None:
                most_recent = b
                most_recent_ctime = b_ctime
            elif b_ctime > most_recent_ctime:
                most_recent = b
                most_recent_ctime = b_ctime
        pre_data.existing_backups_most_recent = most_recent
        pre_data.existing_backups_total_size = eb_total_size

        return pre_data

@dataclass
class PostExecutionData:
    def __init__(self):
        self.archive_size:int = None
        self.archive_collective_size:int = None
    
    @classmethod
    def collect_data(cls, script_data:ScriptDataBS, pre_data:PreExecutionData):
        pass # TODO