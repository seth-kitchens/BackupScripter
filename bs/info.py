
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
        'To Be Added'
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
        'will be identified as an existing backup. These files will count toward the max and may be deleted.\n',
        '\n',
        '- Recent Age -\n',
        'Backups younger than this are "recent" and will be overwritten',
        'before older backups. If there are multiple recent backups, the oldest of them will',
        'be overwritten\n',
        '\n',
        '- Old Age -\n',
        'Backups older than this are "old" and will not',
        'count toward the max or be overwritten\n',
    ])

class window_manage_included:
    window = join([
        'To Be Added'
    ])

class matching_groups_list:
    window = join([
        'Matching Groups are applied after static inclusion in the order they are listed.',
        'If no path is given, the group will be applied to everything already included by',
        'static inclusion and previous matching groups.'
    ])