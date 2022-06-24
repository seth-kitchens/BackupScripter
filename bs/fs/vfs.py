from __future__ import annotations
import os
import re
import nssgui as nss
from os.path import normpath
from typing import Iterable

from bs.fs.matching_group import MatchingGroup
from bs.fs.vfs_entry import VFSEntryBS
from gplib import utils

def is_path_in_path(subpath: str, path: str):
    subpath = os.path.normpath(subpath)
    return subpath.startswith(os.path.abspath(path)+os.sep)

class VirtualFSBS(nss.VirtualFS):
    MATCHING_PATTERN_BANNED_CHARS = ['\r\n']
    def __init__(self, included_items=None, excluded_items=None):
        super().__init__()

        if not included_items:
            included_items = []
        if not excluded_items:
            excluded_items = []
        self.build_from_ie_lists(included_items, excluded_items)
    
    def clone(self):
        i_list, e_list = self.make_ie_lists()
        vfs = VFSBS(i_list, e_list)
        vfs.calc_all()
        return vfs
    
    def copy_from_vfs(self, vfs):
        self.remove_all()
        i_list, e_list = vfs.make_ie_lists()
        self.build_from_ie_lists(i_list, e_list)
    
    def build_from_ie_lists(self, included_items, excluded_items):
        # build vfs from all paths, included and excluded, creating a dict: (path->inc/exc)
        ie_dict = {}
        for path in included_items:
            if self.add_path(path):
                ie_dict[path] = 'included'
        for path in excluded_items:
            if self.add_path(path):
                ie_dict[path] = 'excluded'
        
        # assign each entry a status based on first parent/self entry found in ie_dict
        def cond_in_iedict(entry):
            return entry.path in ie_dict
        for entry in self.all_entries.values():
            parents = entry.find_parents_where(cond_in_iedict, recurse=False)
            entry.status = ie_dict[parents[0].path]
        
        # remove any entries where self and all parents are excluded, promoting
        #   included children where all parents are excluded to roots
        new_roots = []
        def cond_is_included(entry):
            return entry.is_included()
        def cond_no_parents_included(entry):
            if not entry.parent:
                return True
            included_parents = entry.find_parents_where(cond_is_included, recurse=False)
            return not bool(included_parents)
        for root_entry in self.root_entries.values():
            children = root_entry.find_children_where(cond_no_parents_included)
            for child in children:
                if child.is_excluded():
                    if child.path in self.root_entries.keys():
                        self.root_entries.pop(child.path)
                    self.all_entries.pop(child.path)
                    child.delete_self()
                else:
                    new_roots.append(child)
        for entry in new_roots:
            self.root_entries[entry.path] = entry
        self.calc_all()

    def process_matching_groups_dict(self, mgs_dict:dict[str,dict]):
        for mg in mgs_dict.values():
            if not isinstance(mg, dict):
                raise TypeError('mg not dict')
            self.process_matching_group(MatchingGroup.from_dict(mg))
        self.calc_all()
    def process_matching_groups(self, mgs:Iterable):
        for mg in mgs:
            if not isinstance(mg, MatchingGroup):
                raise TypeError('mg not MatchingGroup')
            self.process_matching_group(mg)
        self.calc_all()

    # returns False if a per-group condition fails (e.g. MaxBackupSizeAfter), True otherwise
    def process_matching_group(self, matching_group:MatchingGroup):
        self.calc_all()

        ### Prepare Matching Group Data

        mg = matching_group
        mg.make_invalid_none()
        d = mg.d

        if d.within_paths:
            for i, path in enumerate(d.within_paths):
                d.within_paths[i] = os.path.normpath(path)
                if not os.path.exists(d.within_paths[i]):
                    return False

        total_size_before = self.get_included_size()
        if d.max_backup_size_before != None and total_size_before > d.max_backup_size_before:
            return False
        if d.min_backup_size_before != None and total_size_before < d.min_backup_size_before:
            return False
        
        def ie_func(vfs, path):
            if d.ie_action == 'include':
                vfs.add_path(path, d.apply_recursive)
            elif d.ie_action == 'exclude':
                vfs.exclude(path, d.apply_recursive)

        # a VFS for testing the changes made by this matching group before actually applying everything at the end
        test_vfs = self.clone()

        # a VFS of the files this matching group is applied to
        if d.within_paths:
            match_vfs = VFSBS()
            for path in d.within_paths:
                match_vfs.add_path(path)
            match_vfs.calc_all()
        else:
            match_vfs = self.clone()
        
        # collect files/folders to apply to, and the info for each
        targets = {}
        for path, entry in match_vfs.all_entries.items():
            data = {}
            targets[path] = data
            name = os.path.basename(path)
            data['name'] = name
            name_parts = name.split('.')
            data['stripped_name'] = name_parts[0]
            extensions = []
            for i in range(1, len(name_parts)):
                extensions.append('.'.join(name_parts[i:]))
            data['extensions'] = extensions
            data['size'] = entry.size
            parent_folder_size = None
            if entry.parent:
                parent_folder_size = entry.parent.size
            data['parent_folder_size'] = parent_folder_size
            data['entry_type'] = entry.entry_type
        match_vfs = None # no longer needed
        
        # Filter targets based on apply-to/apply-if conditions
        matches = {}
        for path, data in targets.items():
            size = data['size']
            extensions = data['extensions']
            parent_folder_size = data['parent_folder_size']
            item_type = data['entry_type']

            if item_type == nss.VFSEntry.entry_types.FILE:
                if not d.apply_to_files:
                    continue
                if d.min_file_size != None and size < d.min_file_size:
                    continue
                if d.max_file_size != None and size > d.max_file_size:
                    continue
            if item_type == nss.VFSEntry.entry_types.DIR:
                if not d.apply_to_folders:
                    continue
                if d.min_folder_size != None and size < d.min_folder_size:
                    continue
                if d.max_folder_size != None and size > d.max_folder_size:
                    continue
            if parent_folder_size != None:
                if d.min_parent_folder_size != None and parent_folder_size < d.min_parent_folder_size:
                    continue
                if d.max_parent_folder_size != None and parent_folder_size > d.max_parent_folder_size:
                    continue
            do_continue = False
            for nwpath in d.not_within_paths:
                if os.path.samefile(nwpath, path):
                    do_continue = True
                    break
                if is_path_in_path(path, nwpath):
                    do_continue = True
                    break
            if do_continue:
                continue
            do_continue = False
            if not extensions and d.apply_if_extensions:
                continue
            for ext in extensions:
                if d.apply_if_extensions and not ext in d.apply_if_extensions:
                    do_continue = True
                    break
                elif d.do_not_apply_if_extensions and ext in d.do_not_apply_if_extensions:
                    do_continue = True
                    break
            if do_continue:
                continue
            matches[path] = data
        targets.clear()
        targets.update(matches)

        banned_chars = VFSBS.MATCHING_PATTERN_BANNED_CHARS

        # Pattern Matching
        matches.clear()
        flags = 0
        if not d.match_case:
            flags |= re.IGNORECASE
        for path, data in targets.items():
            if d.strip_extensions:
                name = data['stripped_name']
            else:
                name = data['name']
            if not (d.use_regex or d.match_case):
                name = name.lower()
            if not d.patterns:
                matches[path] = data
            
            match_found = False
            for pattern in d.patterns:
                match_found = False
                if utils.has_chars(banned_chars, pattern):
                    continue
                if not (d.use_regex or d.match_case):
                    pattern = pattern.lower()
                if d.use_regex and d.whole_name:
                    if not pattern.startswith('^'):
                        pattern = '^' + pattern
                    if not pattern.endswith('$'):
                        pattern += '$'
                    if re.search(pattern, name, flags=flags):
                        match_found = True
                elif d.use_regex and not d.whole_name:
                    if re.search(pattern, name, flags=flags):
                        match_found = True
                elif (not d.use_regex) and d.whole_name:
                    if pattern == name:
                        match_found = True
                elif (not d.use_regex) and not d.whole_name:
                    if pattern in name:
                        match_found = True
                if match_found:
                    if d.match_all:
                        continue
                    else:
                        break
            if match_found:
                matches[path] = data
        targets.clear()
        targets.update(matches)

        # if recursive, remove recursively included children
        if d.apply_recursive:
            vfs_simplified = VFSBS()
            for path, data in targets.items():
                vfs_simplified.add_path(path)
            i_simple, _ = vfs_simplified.make_ie_lists()
            matches.clear()
            for path in i_simple:
                matches[path] = targets[path]
            targets.clear()
            targets.update(matches)

        # apply changes to test VFS
        for path, data in targets.items():
            ie_func(test_vfs, path)
        test_vfs.calc_all()

        total_size_after = test_vfs.get_included_size()
        if d.max_backup_size_after != None and total_size_after > d.max_backup_size_after:
            return False
        if d.min_backup_size_after != None and total_size_after < d.min_backup_size_after:
            return False
        
        total_size_diff = abs(total_size_after - total_size_before)
        if d.max_total_size_diff != None and total_size_diff > d.max_total_size_diff:
            return False
        if d.min_total_size_diff != None and total_size_diff < d.min_total_size_diff:
            return False
        
        # apply changes to actual VFS
        for path, data in targets.items():
            ie_func(self, path)
        
        return True

    # bool functions

    def is_root(self, path):
        path = normpath(path)
        if path in self.root_entries.keys():
            return True
        return False

    def has_path(self, path):
        if self.find_root_entry(path) != None:
            return True
        return False

    # operations, get/find

    def get_root_entries(self):
        return list(self.root_entries.values())
    
    def find_entry(self, path):
        return self.all_entries[path]

    def find_root_entry(self, path):
        for root_path in self.root_entries.keys():
            if os.path.commonpath([root_path, path]) == root_path:
                return self.root_entries[root_path]
        return None
    
    def get_skeleton(self, do_get_excluded=True):
        folders = []
        for path, entry in self.all_entries.items():
            if entry.is_dir() and entry.is_included():
                folders.append(path)
        return folders

    # operations, set/add

    def add_path(self, path, recursive_include=True):
        abs_path = os.path.abspath(path)

        if not os.path.exists(path):
            return False

        # if path already in vfs, then include
        if self.has_path(abs_path):
            entry = self.find_entry(abs_path)
            entry.include()
            root_entry = self.find_root_entry(abs_path)
            root_entry.calc_ie()
            return True
        
        roots_in_path = {}
        for root_path, root_entry in self.root_entries.items():
            if is_path_in_path(root_path, abs_path):
                roots_in_path[root_path] = root_entry
        
        new_root = VFSEntryBS(abs_path, 'included')
        if recursive_include:
            for root_path in roots_in_path.keys():
                self.delete_entry(root_path)
            self.root_entries[abs_path] = new_root
            new_root.create_children()
            new_root.include()
        else:
            for root_path in roots_in_path.keys():
                self.pop_root(root_path)
            new_root.create_children(roots_in_path.copy())
            def include_if_new(entry):
                if entry.path in roots_in_path.keys():
                    return
                entry.include(recursive=False)
                for child in entry.children:
                    include_if_new(child)
            include_if_new(new_root)
        entry_set = new_root.collect_entries()
        for entry in entry_set:
            entry_path = entry.get_path()
            self.all_entries[entry_path] = entry
        for path, entry in self.root_entries.items():
            self.all_entries[path] = entry
        return True

    # operations, remove

    def remove(self, path):
        root_entry = self.find_root_entry(path)
        if path != root_entry.path:
            self.exclude(path)
        self.delete_entry(path)
    
    def pop_root(self, path, remove_excluded=True):
        entry = self.root_entries[path]
        self.root_entries.pop(path)
        self.all_entries.pop(path)
        for child in entry.children:
            self.root_entries[child.path] = child
            child.parent = None
        entry.children.clear()
        entry.delete_self()
        if remove_excluded:
            self.pop_excluded_roots()
    
    def pop_excluded_roots(self):
        has_excluded = True
        while has_excluded:
            for path, entry in list(self.root_entries.items()):
                if entry.is_excluded():
                    self.pop_root(path, remove_excluded=False)
            has_excluded = False
            for entry in self.root_entries.values():
                if entry.is_excluded():
                    has_excluded = True
                    break


    def delete_entry(self, path: str):
        entry = self.all_entries[path]
        if path in self.root_entries.keys():
            self.root_entries.pop(path)
        entry_paths = entry.get_all_paths()
        for path in entry_paths:
            self.all_entries.pop(path)
        entry.delete_all()
        return

    def remove_all(self):
        for path in list(self.root_entries.keys()):
            self.remove(path)

    # operations, other

    def exclude(self, path, recursive=True):
        root_entry = self.find_root_entry(path)
        if not root_entry:
            return
        if path == root_entry.path:
            if recursive:
                self.remove(path)
            else:
                self.pop_root(path)
        else:
            entry = self.find_entry(path)
            entry.exclude(recursive)

    # for roots

    def collect_included_files(self):
        def func(entry):
            if entry.is_file() and entry.is_included():
                return entry.path
        return self.for_entries(func)
    
    def collect_archive_lists(self):
        """
        Collect lists of files for each root
        """
        path_lists = {}
        def func(entry):
            path_lists[entry.path] = entry.get_all_paths
    
    def calc_included_size(self):
        return sum(self.for_roots(VFSEntryBS.calc_included_size))
    def get_included_size(self):
        return sum(self.for_roots(VFSEntryBS.get_included_size))
    
    def calc_excluded_size(self):
        return sum(self.for_roots(VFSEntryBS.calc_excluded_size))
    def get_excluded_size(self):
        return sum(self.for_roots(VFSEntryBS.get_excluded_size))

    def calc_included_file_count(self):
        return sum(self.for_roots(VFSEntryBS.calc_included_file_count))
    def get_included_file_count(self):
        return sum(self.for_roots(VFSEntryBS.get_included_file_count))
    
    def calc_excluded_file_count(self):
        return sum(self.for_roots(VFSEntryBS.calc_excluded_file_count))
    def get_excluded_file_count(self):
        return sum(self.for_roots(VFSEntryBS.get_excluded_file_count))

    def calc_included_folder_count(self):
        return sum(self.for_roots(VFSEntryBS.calc_included_folder_count))
    def get_included_folder_count(self):
        return sum(self.for_roots(VFSEntryBS.get_included_folder_count))
    
    def calc_excluded_folder_count(self):
        return sum(self.for_roots(VFSEntryBS.calc_excluded_folder_count))
    def get_excluded_folder_count(self):
        return sum(self.for_roots(VFSEntryBS.get_excluded_folder_count))
    
    

    

    

    # calc

    class vfsdata:
        def __init__(self, vfs:VirtualFSBS):
            # counts
            self.root_folder_count = vfs.get_root_folder_count()
            self.root_file_count = vfs.get_root_file_count()
            self.included_folder_count = vfs.get_included_folder_count()
            self.included_file_count = vfs.get_included_file_count()
            self.excluded_folder_count = vfs.get_excluded_folder_count()
            self.excluded_file_count = vfs.get_excluded_file_count()
            self.included_size = vfs.get_included_size()
            self.excluded_size = vfs.get_excluded_size()

            self.included_items, self.excluded_items = vfs.make_ie_lists()

    def make_ie_lists(self):
        i_list = []
        e_list = []

        for path, entry in self.all_entries.items():
            if entry.is_included():
                if not entry.parent:
                    i_list.append(path)
                elif entry.parent.is_excluded():
                    i_list.append(path)
                # else: entry will be included by parent
            else:
                if not entry.parent:
                    e_list.append(path)
                elif entry.parent.is_included():
                    e_list.append(path)
                # else: entry will be excluded by parent

        return i_list, e_list

    def calc_root(self, path):
        root_entry = self.find_root_entry(path)
        root_entry.calc_all()
    def calc_roots(self, paths):
        root_entries = set()
        for path in paths:
            root_entries.add(self.find_root_entry(path))
        for root_entry in root_entries:
            root_entry.calc_all()
    def calc_all(self):
        for root_entry in self.root_entries.values():
            root_entry.calc_all()

    def calc_vfsdata(self):
        self.calc_all()
        return self.vfsdata(self)
VFSBS = VirtualFSBS
