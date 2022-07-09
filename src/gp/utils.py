import os
import re
import sys
from datetime import datetime
from typing import Any, Iterable

import nssgui as nss


# move functions here to a better location if there is one, and at least several functions belonging there

### text

default_cmd_width = 80


class uprint:

    def line(c='-', length=80, spacing=0, end='\n'):
        if c == '\n' or not c:
            s = ''
        else:
            segment = c[0] + ' ' * spacing
            segment_count = int(length / len(segment))
            s = segment * segment_count
            if len(s) < length:
                s += c
        print(s, end=end)

    def thin_line(c='-'):
        uprint.line(c=c, spacing=2)

    def side_by_side(iterables: Iterable[Iterable], max_table_width=default_cmd_width):
        pcs = []
        for it in iterables:
            pc = nss.PrintColumn()
            pc.add_rows(it)
            pcs.append(pc)
        nss.PrintColumn.print_section(pcs, max_table_width)
    
    def side_by_side_dicts(d1, d2):
        pc1 = nss.PrintColumn(2)
        pc1.add_dict(d1)

        pc2 = nss.PrintColumn(2)
        pc2.add_dict(d2)

        nss.PrintColumn.print_section([pc1, pc2])


def clone_string_unique(s, not_in_strings=None):
    if not_in_strings == None:
        not_in_strings = []
    if (match := re.search('_([0-9]+)$', s)) != None:
        i = int(match.group(1)) + 1
        s = s[:match.start()] + '_'
    else:
        i = 1
        s = s + '_'
    while (s + str(i)) in not_in_strings:
        i += 1
    return s + str(i)


def remove_blank_lines(text):
    lines = text.split('\n')
    lines = [line for line in lines if line.strip()]
    return '\n'.join(lines)


def has_chars(chars, s):
    for c in chars:
        if c in s:
            return True
    return False


def remove_chars(chars, s):
    for c in chars:
        s = s.replace(c, '')
    return s


def center_decimal_string(s, side, lpad=' ', rpad='0'):
    if '.' not in s:
        s = s.rjust(side, ' ') + ' ' * (side + 1)
    else:
        parts = s.split('.')
        s = parts[0].rjust(side, lpad) + '.' + parts[1].ljust(side, rpad)
    return s


### data


def get_instance_vars(obj):
    names = set(dir(obj)).difference(dir(obj.__class__))
    return {name:obj.__dict__[name] for name in names}


### cmd


def prompt_do_continue(continue_text='Continue?'):
    print(continue_text + ' (y/n)\n> ', end='')
    answer = input()
    yes_answers = ['y', 'yes', 'yeah', 'continue']
    return (answer.lower() in yes_answers)


def prompt_any_input(text='Enter any input to continue.'):
    print(text)
    print('> ', end='')
    input()
    return


### fs


def find_nonexistent_dir(path):
    if os.path.exists(path):
        return ''
    ne = path
    parent = ne
    while not os.path.exists(parent):
        ne = parent
        parent = parent_dir(parent)
    return ne


def parent_dir(path, repeat_times=0):
    parent_path = os.path.abspath(os.path.join(path, os.pardir))
    if repeat_times:
        return parent_dir(parent_path, repeat_times-1)
    return parent_path


### project


def print_current_time():
    print('Current Time:', datetime.today().strftime('%m/%d'), datetime.now().strftime('%H:%M:%S'))


def open_in_terminal(exe, args:Iterable=None, close_on_success=True):
    if args == None:
        args = []
    command = 'start cmd /k {} {}'.format(sys.executable, exe)
    if close_on_success:
        args.append('^&^& exit')
    if args:
        command += ' {}'.format(' '.join(args))
    os.system(command)
