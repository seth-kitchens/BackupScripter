import os
import nssgui as nss
from gplib.text.utils import up
from gplib.cmd import utils as cmd_utils
from bs import g

def print_pe_details(execution_data, script_data):
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
        up.print(s)
    up.print_header('Backup Details')

    up.print('To Backup:')
    s = '  Included Items: '
    included_items = script_data['IncludedItems']
    if included_items:
        up_print_list(s, included_items)
    else:
        up.print(s + 'None')
    s = '  Excluded Items: '
    excluded_items = script_data['ExcludedItems']
    if excluded_items:
        up_print_list(s, excluded_items)
    else:
        up.print(s + 'None')
    up.print()

    up.print('Backup Settings')

    archive_type = script_data['ArchiveType']
    up.print('Archive Type: ' + archive_type)
    
    max_backups = script_data['MaxBackups']
    old_age_secs = script_data['BackupOldAge']
    recent_age_secs = script_data['BackupRecentAge']

    if max_backups != None and max_backups > 0:
        up.print('  Max Backups:', max_backups)
    else:
        up.print('  Max Backups: Unlimited')
    if old_age_secs != None:
        up.print('  Old Age:', nss.units.Time(old_age_secs, degree_name=nss.units.Time.SECOND).get_best())
    if recent_age_secs != None:
        up.print('  Recent Age:', nss.units.Time(recent_age_secs, degree_name=nss.units.Time.SECOND).get_best())

def print_pe_key_details(execution_data, script_data):
    up.print_line()
    up.print('Key Details')
    up.print_thin_line()

    backup_filename = script_data['BackupFileName'][0] + execution_data['ResolvedDateSuffix'] + script_data['BackupFileName'][1]
    up.print('Backup File Name:', backup_filename)
    up.print('Backup Destination:', script_data['BackupDestination'])
    up.print()

    i_size = nss.units.Bytes(script_data['IncludedSize'], degree_name='byte').get_best(decimal_digits=1)
    i_files = str(script_data['IncludedFileCount'])
    i_folders = str(script_data['IncludedFolderCount'])
    up.print('Backing up: {0} (Files: {1}, Folders: {2})'.format(i_size.rjust(9), i_files.rjust(3), i_folders.rjust(2)))

    e_size = nss.units.Bytes(script_data['ExcludedSize'], degree_name='byte').get_best(decimal_digits=1)
    e_files = str(script_data['ExcludedFileCount'])
    e_folders = str(script_data['ExcludedFolderCount'])
    up.print('      Excl. {0} (Files: {1}, Folders: {2})'.format(e_size.rjust(9), e_files.rjust(3), e_folders.rjust(2)))

    old_age_secs = script_data['BackupOldAge']
    recent_age_secs = script_data['BackupRecentAge']
    eb_all = execution_data['ExistingBackups']
    eb_normal = execution_data['ExistingBackupsNormal']
    eb_old = execution_data['ExistingBackupsOld']
    eb_recent = execution_data['ExistingBackupsRecent']
    most_recent_backup = execution_data['ExistingBackupsMostRecent']
    if most_recent_backup:
        most_recent_backup_size_bytes = os.path.getsize(most_recent_backup)
    else:
        most_recent_backup_size_bytes = 0
    most_recent_backup_size = nss.units.Bytes(most_recent_backup_size_bytes, degree_name='byte').get_best(decimal_digits=1)
    eb_total_size = nss.units.Bytes(execution_data['ExistingBackupsTotalSize'], degree_name='byte').get_best(decimal_digits=1)
    up.print('Existing Backups: ' + str(len(eb_all)), end='')
    if old_age_secs != None or recent_age_secs != None:
        up.print(' (Normal: ' + str(len(eb_normal)), end='')
        if recent_age_secs != None:
            up.print(', Recent: ' + str(len(eb_recent)), end='')
        if old_age_secs != None:
            up.print(', Old: ' + str(len(eb_old)), end='')
        up.print(')', end='')
    up.print(' (Last: ' + most_recent_backup_size + ', Total: ' + eb_total_size + ')')

    up.print('Backup to be Overwritten: ', end='')
    backup_to_delete = execution_data['BackupToDelete']
    if backup_to_delete:
        if backup_to_delete in eb_recent:
            up.print('(Recent) ', end='')
        up.print(os.path.basename(backup_to_delete), end='')
    else:
        up.print('None')
    up.print()

    up.print_line()

def confirm_pre_execution_info(execution_data, script_data):
    print_pe_details(execution_data, script_data)
    print_pe_key_details(execution_data, script_data)
    if not g.is_noinput():
        do_continue = cmd_utils.prompt_do_continue('Continue with backup?')
    else:
        do_continue = True
    return do_continue
