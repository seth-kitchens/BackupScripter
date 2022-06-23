import shutil
from typing import Iterable
import zipfile
import os
import tempfile
import stat

import py7zr

from bs.fs import vfs as bs_vfs
from bs.script_data import ScriptDataBS

def strip_extensions(name:str):
    lstripped = name.lstrip('.')
    if not len(lstripped):
        return name, ''
    i = name.find('.', name.find(lstripped[0]))
    if i < 0:
        return name, ''
    return name[:i], name[i+1:]
    
def unique_basename_dict(paths:Iterable):
    """Takes an Iterable of paths and makes a dict mapping the paths to their basenames modified to be unique
    example:\n
        ['A/X', 'A/X', 'A/B/X', 'A/Y', 'A/B/Z'] will become:\n
        {
            'A/X': 'X',
            'A/B/X': 'X_1',
            'A/Y': 'Y',
            'A/B/Z': 'Z'
        }"""
    path_set = set(paths)
    d = {}
    basenames = set()
    for path in path_set:
        name = os.path.basename(path)
        if not name in basenames:
            d[path] = name
            basenames.add(name)
        else:
            l, r = strip_extensions(name)
            n = 2
            unique_name = '{}_{}{}'.format(l, n, r)
            while unique_name in basenames:
                n += 1
                unique_name = '{}_{}{}'.format(l, n, r)
            d[path] = unique_name
            basenames.add(unique_name)
    return d

def rmtree_readonly(path_to_remove):
    """shutil.rmtree but also remove read only"""
    def error_func(func, path, excinfo):
        os.chmod(path, stat.S_IWRITE)
        os.remove(path)
    shutil.rmtree(path_to_remove, onerror=error_func)

class Archiver:
    def __init__(self, vfs, dest_path, dest_dir_path, base_folder_name, archive_format) -> None:
        self.vfs:bs_vfs.VFSBS = vfs
        self.dest_path = dest_path
        self.dest_dir_path = dest_dir_path # will be same as dest_path if archiving to folder
        self.base_folder_name = base_folder_name
        self.archive_format = archive_format

    def vfs_path_to_archive_path(self, path, basename_dict):
        """
        Take a path from a VFS (self.vfs) and get the resulting archive path
        """
        vfs_root_entry = self.vfs.find_root_entry(path)
        vfs_root_path = vfs_root_entry.path
        rel_path_to_vfs_root = os.path.relpath(path, vfs_root_path)
        # archive_root_basename = os.path.basename(vfs_root_path)
        archive_root_basename = basename_dict[vfs_root_path]
        archive_path = os.path.normpath(os.path.join(archive_root_basename, rel_path_to_vfs_root))
        return archive_path

    def archive_vfs(self, script_data:ScriptDataBS, mode):
        """
        mode:
            'compile' copies all roots to a temp folder then archives them
            'append' appends files one by one to the archive
        """
        if os.path.exists(self.dest_path):
            print('ERROR: Can\'t overwrite: ' + self.dest_path)
            return False
        if not os.path.exists(self.dest_dir_path):
            print('ERROR: Parent dir doesn\'t exist: ' + self.dest_dir_path)
            return False
        self.vfs.calc_all()
        #script_data.IncludedItems, script_data.ExcludedItems = self.vfs.make_ie_lists()
        
        if os.path.exists(self.dest_path):
            os.remove(self.dest_path)
        
        mode_is_compile = (mode == 'compile')
        mode_is_append = (mode == 'append')
        if not (mode_is_compile or mode_is_append):
            raise ValueError

        format_is_zip = (self.archive_format == 'zip')
        format_is_7z = (self.archive_format == '7z')
        if not (format_is_zip or format_is_7z):
            raise ValueError
    
        if mode_is_compile and format_is_zip:
            print('Archive mode "Compile" unneccessary for zip format. Switching to "Append" mode...')
            mode_is_compile = False
            mode_is_append = True
        
        roots = self.vfs.get_root_entries()
        root_paths = [root.path for root in roots]
        basename_dict = unique_basename_dict(root_paths)
        files_to_backup = self.vfs.collect_included_files()
        n_files = len(files_to_backup)

        if mode_is_compile:
            print('Archive Mode: Compile')
            temp_dir = tempfile.mkdtemp()
            print('Copying {} files to temp directory...'.format(n_files))
            for i, path in enumerate(files_to_backup):
                archive_path = self.vfs_path_to_archive_path(path, basename_dict)
                temp_path = os.path.normpath(os.path.join(temp_dir, archive_path))
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                shutil.copy(path, temp_path)
                print('\r{}/{} copied'.format(i+1, n_files), end='')
            print('')
            print('Archiving compiled files...')
            if format_is_7z:
                with py7zr.SevenZipFile(self.dest_path, 'w') as archive:
                    archive.writeall(temp_dir, self.base_folder_name)
            print('Removing temp directory...')
            rmtree_readonly(temp_dir)
        
        
        elif mode_is_append:
            print('Archive Mode: Append')
            if format_is_zip:
                def append(i_file, path, archive_path):
                    with zipfile.ZipFile(self.dest_path, 'a') as archive:
                        archive.write(path, archive_path)
            elif format_is_7z:
                def append(i_file, path, archive_path):
                    mode = 'w' if i_file == 0 else 'a'
                    with py7zr.SevenZipFile(self.dest_path, mode) as archive:
                        archive.write(path, archive_path)

            print('Archiving {} files...'.format(n_files))
            for i, path in enumerate(files_to_backup):
                archive_path = self.vfs_path_to_archive_path(path, basename_dict)
                archive_path = os.path.normpath(os.path.join(self.base_folder_name, archive_path))
                append(i, path, archive_path)
                print('\r{}/{} archived'.format(i+1, n_files), end='')
            print('')

        return True