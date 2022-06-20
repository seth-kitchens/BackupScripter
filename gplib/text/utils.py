import sys
from typing import Iterable
import re
import nssgui as nss
import gplib

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

default_cmd_width = 80

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

class uprint:
    def line(c='-', length=None, spacing=0, end='\n'):
        length = length if length else gplib.g.line_length
        if c == '\n' or not c:
            s = ''
        else:
            segment = c[0] + ' ' * spacing
            segment_count = int(length / len(segment))
            s = segment * segment_count
            if len(s) < length:
                s += c
        return print(s, end=end)

    def thin_line(c='-'):
        uprint.line(c=c, spacing=2)

def print_side_by_side(iterables: Iterable[Iterable], max_table_width=default_cmd_width):
    pcs = []
    for it in iterables:
        pc = nss.PrintColumn()
        pc.add_rows(it)
        pcs.append(pc)
    nss.PrintColumn.print_section(pcs, max_table_width)
    
def print_dicts_side_by_side(d1, d2):
    pc1 = nss.PrintColumn(2)
    pc1.add_dict(d1)

    pc2 = nss.PrintColumn(2)
    pc2.add_dict(d2)

    nss.PrintColumn.print_section([pc1, pc2])
