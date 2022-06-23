import os
from bs.script.data import PreExecutionData, PostExecutionData
from bs.script_data import ScriptDataBS
import nssgui as nss
from gplib.text.utils import uprint
from gplib.cmd import utils as cmd_utils
from bs import g

def print_pre_execution_details(pre_data:PreExecutionData, script_data:ScriptDataBS):
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

def print_pre_execution_key_details(pre_data:PreExecutionData, script_data:ScriptDataBS):
    print('Backup File Name:', pre_data.dest_filename)
    print('Backup Destination:', script_data.BackupDestination)
    print()

    vfsdata = pre_data.vfsdata_final
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

def confirm_pre_execution_data(pre_data:PreExecutionData, script_data:ScriptDataBS):
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

def print_post_execution_details(post_data:PostExecutionData, script_data:ScriptDataBS):
    print('')
    pass # TODO