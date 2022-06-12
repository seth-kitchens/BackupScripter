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

class UtilityPrinter:
    print_target = sys.stdout
    last_print = ''
    def set_default_target(t=sys.stdout):
        if   t == 'stdout' or t == 'out':           up.print_target = sys.stdout
        elif t == 'stderr' or t == 'err':           up.print_target = sys.stderr
        elif t == 'None'   or t == 'none' or not t: up.print_target = None
        else:
            print('ERROR: Unknown print target')
            up.print_target = t

    def print(*args, sep=' ', end='\n', file='default'):
        if args:
            s = str(args[0])
        else:
            s = ''
        
        for i in range(1, len(args)):
            s += sep + str(args[i])
        s += end
        
        if file == 'default':
            file = up.print_target
        if file:
            print(s, end='', file=file)
        return s

    def print_line(c='-', length=None, spacing=0, end='\n', target='default'):
        length = length if length else gplib.g.line_length
        if c == '\n' or not c:
            s = ''
        else:
            segment = c[0] + ' ' * spacing
            segment_count = int(length / len(segment))
            s = segment * segment_count
            if len(s) < length:
                s += c
        up.last_print = 'line'
        return up.print(s, end=end, file=target)
    def print_thin_line(c='-'):
        up.print_line(c=c, spacing=2)

    def print_banner(text, c1='-', c2='-', length=None, end='\n', target='default'):
        s =  up.print_line(c=c1, length=length, target=None)
        s += text + '\n'
        s += up.print_line(c=c2, length=length, end='', target=None)
        up.last_print = 'banner'
        return up.print(s, end=end, file=target)

    def print_header(text, c='-', length=None, end='\n', target='default'):
        s = ''
        if up.last_print not in ['footer']:
            s +=  up.print_line(c=c, length=length, target=None)
        s += text + '\n'
        s += up.print_line(c=c, length=length, spacing=2, end='', target=None)
        up.last_print = 'header'
        return up.print(s, end=end, file=target)

    def print_footer(text, c='-', length=None, end='\n', target='default'):
        s =  up.print_line(c=c, length=length, spacing=2, target=None)
        s += text
        s += '\n'
        s += up.print_line(c=c, length=length, end='', target=None)
        up.last_print = 'footer'
        return up.print(s, end=end, file=target)

    def print_section_banner(text, c='#', length=None, end='\n', target='default'):
        length = length if length else gplib.g.line_length
        s =  up.print_line(c=c, length=length, target=None)
        s += ''.rjust(2, c) + ' ' + text + ' ' + ''.rjust((length - 4 - len(text)), c) + '\n'
        s += up.print_line(c=c, length=length, end='', target=None)
        up.last_print = 'section_banner'
        return up.print(s, end=end, file=target)
up = UtilityPrinter

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
