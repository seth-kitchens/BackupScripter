import os
from logging import *

#recent_path = logpath('recent.log')
#old_path = logpath('old.log')

def info_line():
    info('-' * 50)
def init_logging(start_msg, log_folder):
    all_path = os.path.normpath(log_folder + '/bs.log')
    old_path = os.path.normpath(log_folder + '/bs.old.log')
    if os.path.exists(all_path):
        st = os.stat(all_path)
        if st.st_size > 50_000:
            with open(all_path, 'r') as file_in:
                text = file_in.read()
            with open(old_path, 'a') as file_out:
                file_out.write(text)
            os.remove(all_path)
    basicConfig(filename=all_path, encoding='utf-8', level=INFO)
    info_line()
    info(start_msg)
    info_line()
    

