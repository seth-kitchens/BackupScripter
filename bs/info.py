
# join list of strs with sep=space if no whitespace already at end of line
def join(ss:list[str]):
    if not ss:
        return ''
    len_ss = len(ss)
    for i in range(len_ss - 1):
        if not ss[i]:
            ss[i] = '\n'
        elif not ss[i][-1].isspace():
            ss[i] = ss[i] + ' '
    return ''.join(ss)

class window_main:
    window = join([
        '- Script File -\n',
        'Settings for the script file created',
        '\n\n',
        '- Backup File -\n',
        'Settings for the backup file created by the script',
        '\n\n',
        '- To Backup -\n',
        'Information about items included. "Static" only shows data for',
        'items statically included, while "Final" shows data for everything',
        'included after matching groups are applied. Note that these are actually',
        'applied at script runtime, and the data will be different.',
        '\n\n',
        '- Backup Settings -\n',
        'Settings for the script unrelated to inclusion. For more information',
        'click [?] next to Max Backups'
    ])
    backup_filename_date = join([
        'This string is first processed then appended to the end of',
        'the filename, before the extension, at the time of executing',
        'the backup script. Patterns representing parts',
        'of a date or time are replaced with the respective information at',
        'time of backup. The patterns are set-width with leading zeros. If',
        '"Pull Age From Filename" is set, then this segment of the filename',
        'will be used to date existing backups.\n',
        '\n',
        'Patterns:\nYYYY: Year\nMM: Month\nDD: Day\nHH: Hour(24)\nhh: Hour(12)\n',
        'mm: Minute\nss: Second\nUU: Unix time\n'
    ])
    backup_settings = join([
        '- Max Backups -\n',
        'Any files in the same backup',
        'destination folder with the same name, extension and date postfix (from a different time)',
        'will be identified as an existing backup. These files will count toward the max and may be deleted.',
        '\n\n',
        '- Recent Age -\n',
        'Backups younger than this are "recent" and will be overwritten',
        'before older backups. If there are multiple recent backups, the oldest of them will',
        'be overwritten',
        '\n\n',
        '- Old Age -\n',
        'Backups older than this are "old" and will not',
        'count toward the max or be overwritten',
        '\n\n',
        '- Pull Age From Filename -\n',
        'If this is selected, dates of files identified as like backups will be determined',
        'by the date postfix rather than the file metadata'
    ])

class window_manage_included:
    window = join([
        '- Static Inclusion -\n',
        'Include or exclude files and folders here by manually selecting them. Excluding a root item',
        'will remove it from the explorer. Removing a nested item will exclude it. Data shown in',
        'the file explorer includes:\n\n',
        'Status: Included/Excluded\n',
        'Inc Size: Recursive size included\n',
        'Exc Size: Recursive size excluded\n',
        'I-F: Included folders. Includes self.\n',
        'I-f: Included files. Includes self\n',
        'E-F: Excluded folders. Includes self\n',
        'E-f: Excluded files. Includes self\n',
        '\n\n',
        '- Matching Groups -\n',
        'Include files at script runtime based on patterns and conditions. These matching groups are named',
        'and applied in order. Use the arrows on the left to reorder them. You can view how the matching',
        'groups look at any point in the list with the "Preview Here" button (includes selected), or view',
        'all with the "Preview All" button. The "Resolve Here" and "Resolve All" buttons permanently transform the',
        'matching groups into static inclusion. In the details box, highlighted text shows selected options',
        'within the matching group that are taking effect. Orange highlighted text shows effects that are expected',
        'to be in error.'
    ])

class matching_groups_list:
    window = join([
        '- Action -\n',
        'Exclude or Include. The action that is applied to matched files/folders. Include',
        'not yet implemented',
        '\n\n',
        '- Patterns -\n',
        'Patterns to match file names or folder names against\n',
        '- Strip Extensions: Strips periods and all characters following before matching\n',
        '- Match Whole Name: Pattern must match whole name and not just be found within name\n',
        '- Match Case: If checked, identical case is required to match\n',
        '- Use Regex: If checked, patterns will be regex. Otherwise, plain text\n',
        '- Match All Patterns: If checked, all patterns must match the name. Otherwise,',
        'only one needs to match\n',
        '\n\n',
        '- Apply To -\n',
        'Files/Folders. What this matching group is compared against and potentially',
        'applied to. One of these must be selected, or the group will take no effect',
        '\n\n',
        '- Apply If -\n',
        'Conditions per file/folder. If any file/folder being compared against does',
        'not match the condition, the group\'s action (include/exclude) will not be applied to it',
        '\n\n',
        '- Apply Group If -\n',
        'Conditions for the entire matching group. If these are filled in and false',
        'when this matching group is applied, the entire group will be not be applied'
    ])