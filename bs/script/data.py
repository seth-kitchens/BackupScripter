import os
from dataclasses import dataclass
import nssgui as nss
import time

from bs.fs.vfs import VFSBS as VFS, VirtualFSBS
from bs.script_data import ScriptDataBS
from bs import g
from gplib import utils as gp_utils
from bs.script import utils as b_utils
from gplib import DateString, uprint


def clean_invalids(script_data:ScriptDataBS):
    sd_dict = script_data.to_dict()
    def negative_to_none(x):
        if sd_dict[x] != None and sd_dict[x] < 0:
            sd_dict[x] = None
    negative_to_none('MaxBackups')
    negative_to_none('BackupOldAge')
    negative_to_none('BackupRecentAge')
    script_data.load_dict(sd_dict)

def is_within_age_seconds(path, lower=-1, upper=-1, date_string=None):
    ctime = None
    if date_string != None and (len(os.path.basename(path)) >= len(date_string)):
        date_postfix = DateString.extract_postfix(date_string, path)
        ctime = DateString.postfix_to_datetime(date_string, date_postfix).timestamp()
    if ctime == None:
        ctime = os.path.getctime(path)
    age = time.time() - ctime
    if lower >= 0 and age < lower:
        return False
    if upper >= 0 and age > upper:
        return False
    return True


@dataclass
class PreExecutionData:
    def __init__(self, script_data:ScriptDataBS):
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

        self._collect_data(script_data)
    
    def _collect_data(self, script_data:ScriptDataBS):
        vfs_static = VFS()

        self.resolved_date_postfix = DateString.process(script_data.BackupDatePostfix)
        self.dest_filename = script_data.BackupFilename[0] + self.resolved_date_postfix + script_data.BackupFilename[1]
        self.dest_path = os.path.normpath(os.path.join(script_data.BackupDestination, self.dest_filename))

        # Inclusion

        vfs_static.build_from_ie_lists(script_data.IncludedItems, script_data.ExcludedItems)
        vfs_final = vfs_static.clone()
        vfs_final.process_matching_groups_dict(script_data.MatchingGroupsList)
        self.vfsdata_static = vfs_static.calc_vfsdata()
        self.vfsdata_final = vfs_final.calc_vfsdata()
        self.vfs_final = vfs_final

        backup_destination = script_data.BackupDestination
        backup_basename = script_data.BackupFilename[0]
        backup_date_string = script_data.BackupDatePostfix
        backup_extension = script_data.BackupFilename[1]
        self.existing_backups = []
        if os.path.exists(backup_destination) and os.path.isdir(backup_destination):
            files = [f for f in os.listdir(backup_destination) if os.path.isfile(os.path.normpath(os.path.join(backup_destination, f)))]
            for filename in files:
                if b_utils.is_file_backup(filename, backup_basename, backup_date_string, backup_extension):
                    filepath = os.path.normpath(os.path.join(backup_destination, filename))
                    self.existing_backups.append(filepath)


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
                return DateString.extract_timestamp(date_string, path)
            else:
                return os.path.getctime(path)

        if recent_age_secs != None:
            eb_recent = [f for f in self.existing_backups if is_within_age_seconds(f, upper=recent_age_secs, date_string=date_string)]
        else:
            eb_recent = []
        self.existing_backups_recent = eb_recent
        
        if old_age_secs != None:
            eb_old = [f for f in self.existing_backups if is_within_age_seconds(f, lower=old_age_secs, date_string=date_string)]
        else:
            eb_old = []
        self.existing_backups_old = eb_old

        eb_normal = self.existing_backups_normal = [f for f in self.existing_backups if (not f in eb_recent) and (not f in eb_old)]
        
        self.backup_to_delete = None
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
            self.backup_to_delete = oldest

        most_recent = None
        most_recent_ctime = None
        eb_total_size = 0
        for b in self.existing_backups:
            b_ctime = get_backup_age(b)
            eb_total_size += os.path.getsize(b)
            if most_recent == None:
                most_recent = b
                most_recent_ctime = b_ctime
            elif b_ctime > most_recent_ctime:
                most_recent = b
                most_recent_ctime = b_ctime
        self.existing_backups_most_recent = most_recent
        self.existing_backups_total_size = eb_total_size

    def _print_details(self, script_data:ScriptDataBS):
        def up_print_list(label, l, max_elements=4):
            """Print list items one per line, indenting up to the opening bracket.
            If over 'max_elements' in list, line after max will be: '... ] (# more)' """
            s = label + '['
            len_s = len(s)
            len_l = len(l)
            remaining = len_l - max_elements
            if l:
                s += '"' + str(l[0]) + '"'
            for el in l[1:max_elements+1]:
                s += '\n' + ' ' * len_s + '"' + str(el) + '"'
            if remaining > 0:
                s += '\n' + ' ' * len_s + '... ] (' + str(remaining) + ' more)'
            else:
                s += ']'
            print(s)

        print('To Backup:')
        s = '  Included Items: '
        if script_data.IncludedItems:
            up_print_list(s, script_data.IncludedItems)
        else:
            print(s + 'None')
        s = '  Excluded Items: '
        if script_data.ExcludedItems:
            up_print_list(s, script_data.ExcludedItems)
        else:
            print(s + 'None')
        print()

        print('Backup Settings')

        print('Archive Type: ' + script_data.ArchiveFormat)

        if script_data.MaxBackups != None and script_data.MaxBackups > 0:
            print('  Max Backups:', script_data.MaxBackups)
        else:
            print('  Max Backups: Unlimited')
        if script_data.BackupOldAge != None:
            print('  Old Age:', nss.units.Time(script_data.BackupOldAge, degree_name=nss.units.Time.SECOND).get_best())
        if script_data.BackupRecentAge != None:
            print('  Recent Age:', nss.units.Time(script_data.BackupRecentAge, degree_name=nss.units.Time.SECOND).get_best())

    def _print_key_details(self, script_data:ScriptDataBS):
        print('Backup File Name:', self.dest_filename)
        print('Backup Destination:', script_data.BackupDestination)
        print()

        vfsdata = self.vfsdata_final
        i_size = nss.units.Bytes(vfsdata.included_size, degree_name='byte').get_best(decimal_digits=1)
        i_files = str(vfsdata.included_file_count)
        i_folders = str(vfsdata.included_folder_count)
        print('Backing up: {0} (Files: {1}, Folders: {2})'.format(i_size.rjust(9), i_files.rjust(3), i_folders.rjust(2)))

        e_size = nss.units.Bytes(vfsdata.excluded_size, degree_name='byte').get_best(decimal_digits=1)
        e_files = str(vfsdata.excluded_file_count)
        e_folders = str(vfsdata.excluded_folder_count)
        print('      Excl. {0} (Files: {1}, Folders: {2})'.format(e_size.rjust(9), e_files.rjust(3), e_folders.rjust(2)))

        old_age_secs = script_data.BackupOldAge
        recent_age_secs = script_data.BackupRecentAge
        eb_all = self.existing_backups
        eb_normal = self.existing_backups_normal
        eb_old = self.existing_backups_old
        eb_recent = self.existing_backups_recent
        most_recent_backup = self.existing_backups_most_recent
        if most_recent_backup:
            most_recent_backup_size_bytes = os.path.getsize(most_recent_backup)
        else:
            most_recent_backup_size_bytes = 0
        most_recent_backup_size = nss.units.Bytes(most_recent_backup_size_bytes, degree_name='byte').get_best(decimal_digits=1)
        eb_total_size = nss.units.Bytes(self.existing_backups_total_size, degree_name='byte').get_best(decimal_digits=1)
        print('Existing Backups: ' + str(len(eb_all)), end='')
        if old_age_secs != None or recent_age_secs != None:
            print(' (Normal: ' + str(len(eb_normal)), end='')
            if recent_age_secs != None:
                print(', Recent: ' + str(len(eb_recent)), end='')
            if old_age_secs != None:
                print(', Old: ' + str(len(eb_old)), end='')
            print(')', end='')
        print(' (Last: ' + most_recent_backup_size + ', Total: ' + eb_total_size + ')')

        print('Backup to be Overwritten: ', end='')
        backup_to_delete = self.backup_to_delete
        if backup_to_delete:
            if backup_to_delete in eb_recent:
                print('(Recent) ', end='')
            print(os.path.basename(backup_to_delete), end='')
        else:
            print('None')

    def confirm_data(self, script_data:ScriptDataBS):
        uprint.line()
        print('Backup Details')
        uprint.thin_line()
        self._print_details(script_data)
        
        uprint.line()
        print('Key Details')
        uprint.thin_line()
        self._print_key_details(script_data)
        if not g.is_noinput():
            uprint.line()
            do_continue = gp_utils.prompt_do_continue('Continue with backup?')
        else:
            do_continue = True
        return do_continue


@dataclass
class PostExecutionData:
    def __init__(self, script_data:ScriptDataBS, pre_data:PreExecutionData):
        self.archive_size:int = None
        self.archive_collective_size:int = None

        self._collect_data(script_data, pre_data)
    
    def _collect_data(self, script_data:ScriptDataBS, pre_data:PreExecutionData):
        pass # TODO
    
    def print_details(self, script_data:ScriptDataBS, pre_data:PreExecutionData):
        print('')
        pass # TODO