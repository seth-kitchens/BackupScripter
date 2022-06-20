import os
from bs.script.data import PreExecutionData
import nssgui as nss
from gplib.text.utils import uprint
from gplib.cmd import utils as cmd_utils
from bs import g

def print_pre_execution_details(pre_data:PreExecutionData, script_data):
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
    included_items = script_data['IncludedItems']
    if included_items:
        up_print_list(s, included_items)
    else:
        print(s + 'None')
    s = '  Excluded Items: '
    excluded_items = script_data['ExcludedItems']
    if excluded_items:
        up_print_list(s, excluded_items)
    else:
        print(s + 'None')
    print()

    print('Backup Settings')

    archive_format = script_data['ArchiveFormat']
    print('Archive Type: ' + archive_format)
    
    max_backups = script_data['MaxBackups']
    old_age_secs = script_data['BackupOldAge']
    recent_age_secs = script_data['BackupRecentAge']

    if max_backups != None and max_backups > 0:
        print('  Max Backups:', max_backups)
    else:
        print('  Max Backups: Unlimited')
    if old_age_secs != None:
        print('  Old Age:', nss.units.Time(old_age_secs, degree_name=nss.units.Time.SECOND).get_best())
    if recent_age_secs != None:
        print('  Recent Age:', nss.units.Time(recent_age_secs, degree_name=nss.units.Time.SECOND).get_best())

def print_pre_execution_key_details(pre_data:PreExecutionData, script_data):
    print('Backup File Name:', pre_data.dest_filename)
    print('Backup Destination:', script_data['BackupDestination'])
    print()

    i_size = nss.units.Bytes(script_data['IncludedSize'], degree_name='byte').get_best(decimal_digits=1)
    i_files = str(script_data['IncludedFileCount'])
    i_folders = str(script_data['IncludedFolderCount'])
    print('Backing up: {0} (Files: {1}, Folders: {2})'.format(i_size.rjust(9), i_files.rjust(3), i_folders.rjust(2)))

    e_size = nss.units.Bytes(script_data['ExcludedSize'], degree_name='byte').get_best(decimal_digits=1)
    e_files = str(script_data['ExcludedFileCount'])
    e_folders = str(script_data['ExcludedFolderCount'])
    print('      Excl. {0} (Files: {1}, Folders: {2})'.format(e_size.rjust(9), e_files.rjust(3), e_folders.rjust(2)))

    old_age_secs = script_data['BackupOldAge']
    recent_age_secs = script_data['BackupRecentAge']
    eb_all = pre_data.existing_backups
    eb_normal = pre_data.existing_backups_normal
    eb_old = pre_data.existing_backups_old
    eb_recent = pre_data.existing_backups_recent
    most_recent_backup = pre_data.existing_backups_most_recent
    if most_recent_backup:
        most_recent_backup_size_bytes = os.path.getsize(most_recent_backup)
    else:
        most_recent_backup_size_bytes = 0
    most_recent_backup_size = nss.units.Bytes(most_recent_backup_size_bytes, degree_name='byte').get_best(decimal_digits=1)
    eb_total_size = nss.units.Bytes(pre_data.existing_backups_total_size, degree_name='byte').get_best(decimal_digits=1)
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
    backup_to_delete = pre_data.backup_to_delete
    if backup_to_delete:
        if backup_to_delete in eb_recent:
            print('(Recent) ', end='')
        print(os.path.basename(backup_to_delete), end='')
    else:
        print('None')

def confirm_pre_execution_data(pre_data:PreExecutionData, script_data):
    uprint.line()
    print('Backup Details')
    uprint.thin_line()
    print_pre_execution_details(pre_data, script_data)
    
    uprint.line()
    print('Key Details')
    uprint.thin_line()
    print_pre_execution_key_details(pre_data, script_data)
    if not g.is_noinput():
        uprint.line()
        do_continue = cmd_utils.prompt_do_continue('Continue with backup?')
    else:
        do_continue = True
    return do_continue
