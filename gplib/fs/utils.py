import os
import re
import time
from datetime import datetime

# Date Strings

class DateString:
    @classmethod
    def process(cls, date_string:str='_YYYYMMDD_HHmmss', dt:datetime=None):
        now = dt if dt else datetime.now()

        codes = {}
        codes['YYYY'] = now.strftime('%Y')
        codes['MM'] = now.strftime('%m')
        codes['DD'] = now.strftime('%d')
        codes['HH'] = now.strftime('%H')
        codes['hh'] = now.strftime('%I')
        codes['mm'] = now.strftime('%M')
        codes['ss'] = now.strftime('%S')
        codes['UU'] = str(int(now.timestamp())).rjust(10, '0')
        for key, value in codes.items():
            date_string = date_string.replace(key, value)
        return date_string
    
    @classmethod
    def split(cls, date_string:str, path_or_name:str):
        basename:str = os.path.basename(path_or_name)
        i_ext = basename.find('.')
        ext = basename[i_ext:]
        len_postfix = len(date_string.replace('UU', '_' * 10))
        i_postfix = -1 * (len_postfix + len(ext))
        left = basename[:i_postfix]
        postfix = basename[i_postfix:i_ext]
        return left, postfix, ext

    @classmethod
    def extract_postfix(cls, date_string:str, path_or_name:str):
        """Pull postfix from path or filename. Strips extensions (doesn't work if '.' in filename)"""
        _, postfix, _ = cls.split(date_string, path_or_name)
        return postfix
    
    @classmethod
    def extract_timestamp(cls, date_string:str, path_or_name:str):
        """Pull timestamp from path/filename with date string. Returns None upon failure."""
        postfix = cls.extract_postfix(date_string, path_or_name)
        if postfix == None:
            return None
        dt = cls.postfix_to_datetime(date_string, postfix)
        if dt == None:
            return None
        return dt.timestamp()
    
    @classmethod
    def matches(cls, date_string:str, path_or_name:str):
        return (cls.extract_timestamp(date_string, path_or_name) != None)

    @classmethod
    def postfix_to_datetime(cls, date_string:str, postfix:str):
        match = re.search('UU', date_string)
        if match != None:
            l = match.start(0)
            timestamp = postfix[l:l+10]
            if not re.search('^[0-9]+$', timestamp):
                return None
            return datetime.fromtimestamp(float(timestamp))

        def pull(pattern): # pull digits of same-length code from postfix
            match = re.search(pattern, date_string)
            if match == None:
                return 0
            s = postfix[match.start(0):match.end(0)]
            if not re.search('^[0-9]+$', s):
                return None
            return int(s)

        year = pull('YYYY')
        month = pull('MM')
        day = pull('DD')
        if 'HH' in date_string:
            hour = pull('HH')
        else:
            hour = pull('hh')
        minute = pull('mm')
        second = pull('ss')
        if None in [year, month, day, hour, minute, second]:
            return None
        return datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)

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

def is_within_age_days(path, lower=-1, upper=-1, date_string=None):
    seconds_in_day = 60 * 60 * 24
    return is_within_age_seconds(path, lower * seconds_in_day, upper * seconds_in_day, date_string=date_string)

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

def create_file_safely(path, lines, end=''):
    if os.path.exists(path):
        print('ERROR: File already exists: ' + path)
        return False
    if not os.path.exists(parent_dir(path)):
        print('ERROR: Destination must exist: ' + parent_dir(path))
        return False
    file = open(path, 'w')
    for line in lines:
        file.write(line + end)
    file.close()
    return

# returns indices of start and end of first match found
def find_mre(lines:list[str], mre):
    """
    ---
    Find multi-line regex in lines
    
    ---
    Args:
        lines: list of lines 
        mre: list of regex's
    ---
    Returns:
        tuple[int, int]: indices of start and end of first match found, respectively
    """
    if not mre:
        return -1, -1
    for i_line in range(len(lines)):
        for i_re in range(len(mre) + 1):
            if i_re >= len(mre):
                # match found
                return i_line, i_line + i_re - 1
            if i_line + i_re > len(lines):
                break
            if not re.search(mre[i_re], lines[i_line + i_re]):
                break
    return -1, -1

# mre = multiline regex
def copy_file_lines_regex(path, mre_from, mre_to=None, do_include_from=True, do_include_to=False):
    lines = file_to_lines(path)

    if not mre_from:
        return []

    # Remove code
    from_match_start, from_match_end = find_mre(lines, mre_from)
    if from_match_start < 0 or from_match_end < 0:
        print('ERROR: mre_from not matched')
        return []
    from_index = from_match_start if do_include_from else from_match_end + 1

    if mre_to:
        to_match_start, to_match_end = find_mre(lines, mre_to)
        if to_match_start < 0 or to_match_end < 0:
            print('ERROR: mre_to not matched')
            return []
        to_index = to_match_end + 1 if do_include_to else to_match_start
    else:
        to_index = len(lines)

    return lines[from_index:to_index]

def is_path_in_path(subpath: str, path: str):
    subpath = os.path.normpath(subpath)
    return subpath.startswith(os.path.abspath(path)+os.sep)

def file_to_string(path):
    file = open(path, 'r')
    text = file.read()
    file.close()
    return text

def file_to_lines(path):
    file = open(path, 'r')
    lines = []
    for line in file:
        lines.append(line)
    return lines