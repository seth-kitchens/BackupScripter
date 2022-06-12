import zipfile
import os
import time

import nssgui as nss

class Archiver:
    def __init__(self, vfs, dest_path, dest_dir_path, base_folder_name) -> None:
        self.vfs:nss.VFS = vfs
        self.dest_path = dest_path
        self.dest_dir_path = dest_dir_path # will be same as dest_path if archiving to folder
        self.base_folder_name = base_folder_name

    def fs_path_to_archive_path(self, path):
        vfs_root_entry = self.vfs.find_root_entry(path)
        vfs_root_path = vfs_root_entry.path
        rel_path_to_vfs_root = os.path.relpath(path, vfs_root_path)
        archive_root_basename = os.path.basename(vfs_root_path)
        archive_root_path = os.path.normpath(os.path.join(self.base_folder_name, archive_root_basename))
        archive_path = os.path.normpath(os.path.join(archive_root_path, rel_path_to_vfs_root))
        return archive_path

    def archive_file(self, fs_path, a_path):
        with zipfile.ZipFile(self.dest_path, 'a') as zipper:
            zipper.write(fs_path, a_path)
        return

    def archive_vfs(self, script_data):
        if os.path.exists(self.dest_path):
            print('ERROR: Can\'t overwrite: ' + self.dest_path)
            return False
        if not os.path.exists(self.dest_dir_path):
            print('ERROR: Parent dir doesn\'t exist: ' + self.dest_dir_path)
            return False
        vfs = self.vfs
        vfs.calc_all()
        vfs.make_ie_lists(script_data)
        
        if os.path.exists(self.dest_path):
            os.remove(self.dest_path)
        files_to_backup = vfs.collect_included_files()
        for fs_path in files_to_backup:
            a_path = self.fs_path_to_archive_path(fs_path)
            print('Archiving File: ' + fs_path)
            self.archive_file(fs_path, a_path)

        return True