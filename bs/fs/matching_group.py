from gplib import PackableDict, Dictable

class MatchingGroup(Dictable):
    class _d(PackableDict):
        def __init__(self):
            self.ie_action = 'exclude' # 'include' | 'exclude'

            # Apply To

            self.apply_to_files = False
            self.apply_to_folders = False

            # This is for resolving a matching group to exclude future
            #   additions to a folder while including all current
            #   additions. Add 'Resolve Options' area to window for this?
            self.apply_recursive = True
            self.min_file_size = -1
            self.max_file_size = -1
            self.min_folder_size = -1
            self.max_folder_size = -1

            # Apply If
            
            self.within_paths = []
            self.not_within_paths = []
            self.apply_if_extensions = []
            self.do_not_apply_if_extensions = []
            self.min_parent_folder_size = -1
            self.max_parent_folder_size = -1

            # Apply Group If

            self.max_backup_size_before = -1
            self.max_backup_size_after = -1
            self.min_backup_size_before = -1
            self.min_backup_size_after = -1
            self.max_total_size_diff = -1
            self.min_total_size_diff = -1

            # Patterns

            self.strip_extensions = False
            self.match_case = False
            self.use_regex = False
            self.whole_name = False
            self.match_all = False
            self.patterns = []
    def __init__(self, d=None):
        self.d = self._d()
        if d != None:
            self.load_dict(d)
    def make_invalid_none(self):
        def negative_to_none(x):
            if x == None or x >= 0:
                return x
            return None
        d = self.d
        d.min_file_size = negative_to_none(d.min_file_size)
        d.max_file_size = negative_to_none(d.max_file_size)
        d.min_folder_size = negative_to_none(d.min_folder_size)
        d.max_folder_size = negative_to_none(d.max_folder_size)
        d.min_parent_folder_size = negative_to_none(d.min_parent_folder_size)
        d.max_parent_folder_size = negative_to_none(d.max_parent_folder_size)

        d.max_backup_size_before = negative_to_none(d.max_backup_size_before)
        d.max_backup_size_after = negative_to_none(d.max_backup_size_after)
        d.min_backup_size_before = negative_to_none(d.min_backup_size_before)
        d.min_backup_size_after = negative_to_none(d.min_backup_size_after)
        d.max_total_size_diff = negative_to_none(d.max_total_size_diff)
        d.min_total_size_diff = negative_to_none(d.min_total_size_diff)
