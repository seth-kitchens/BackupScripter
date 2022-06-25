import os
import re
from datetime import datetime

__all__ = [
    'DateString'
]

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
        if not isinstance(postfix, str):
            return None
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
        if 0 in [year, month, day]:
            return None
        if 'HH' in date_string:
            hour = pull('HH')
        else:
            hour = pull('hh')
        minute = pull('mm')
        second = pull('ss')
        if None in [year, month, day, hour, minute, second]:
            return None
        return datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
