import PsgUnsimplified as sgu


class VFSEntryBS(sgu.VFSEntry):

    def __init__(self, init_path, init_status):
        sgu.VFSEntry.__init__(self, init_path)
        self.children:list[VFSEntryBS]

        self.status:str = init_status # included/excluded
        self.included_size:int = 0
        self.excluded_size:int = 0
        self.included_folders:int = 0
        self.included_files:int = 0
        self.excluded_folders:int = 0
        self.excluded_files:int = 0

    ### VSEntry

    @classmethod
    def from_parent(cls, parent, init_path):
        child = VFSEntryBS(init_path, parent.status)
        parent.connect_child(child)
        return child
    
    ### VSEntryBS

    def has_excluded(self):
        if self.excluded_size > 0 or self.excluded_folders > 0:
            return True
        return False

    def has_included(self):
        if self.included_size > 0 or self.included_folders > 0:
            return True
        return False

    def calc_included_size(self):
        self.included_size = sum(self.for_children(VFSEntryBS.calc_included_size, recurse=False))
        if self.is_included() and self.is_file():
            self.included_size += self.size
        return self.included_size

    def get_included_size(self):
        return self.included_size

    def calc_excluded_size(self):
        self.excluded_size = sum(self.for_children(VFSEntryBS.calc_excluded_size, recurse=False))
        if self.is_excluded() and self.is_file():
            self.excluded_size += self.size
        return self.excluded_size

    def get_excluded_size(self):
        return self.excluded_size

    def calc_included_folder_count(self):
        self.included_folders = sum(self.for_children(
            VFSEntryBS.calc_included_folder_count, recurse=False))
        if self.is_included() and self.is_dir():
            self.included_folders += 1
        return self.included_folders

    def get_included_folder_count(self):
        return self.included_folders

    def calc_included_file_count(self):
        self.included_files = sum(self.for_children(
            VFSEntryBS.calc_included_file_count, recurse=False))
        if self.is_included() and self.is_file():
            self.included_files += 1
        return self.included_files

    def get_included_file_count(self):
        return self.included_files

    def calc_excluded_folder_count(self):
        self.excluded_folders = sum(self.for_children(
            VFSEntryBS.calc_excluded_folder_count, recurse=False))
        if self.is_excluded() and self.is_dir():
            self.excluded_folders += 1
        return self.excluded_folders

    def get_excluded_folder_count(self):
        return self.excluded_folders

    def calc_excluded_file_count(self):
        self.excluded_files = sum(self.for_children(
            VFSEntryBS.calc_excluded_file_count, recurse=False))
        if self.is_excluded() and self.is_file():
            self.excluded_files += 1
        return self.excluded_files

    def get_excluded_file_count(self):
        return self.excluded_files
    
    def print(self, prefix = ''):
        print(prefix + self.name)
        print(prefix + '  Path: ' + self.path)
        print(prefix + '  Type: ' + self.entry_type)
        print(prefix + '  Status: ' + self.status)
        return
    
    def print_children(self, prefix = ''):
        for child in self.children:
            child.print(prefix)
            if child.is_dir():
                child.print_children(prefix + '  ')
        return
    
    def is_included(self):
        if self.status == 'included':
            return True
        return False
    def is_excluded(self):
        if self.status == 'excluded':
            return True
        return False
    
    def exclude(self, recursive=True):
        self.status = 'excluded'
        if recursive:
            for child in self.children:
                child.exclude()
        return
    
    def include(self, recursive=True):
        self.status = 'included'
        if recursive:
            for child in self.children:
                child.include()
        return
    
    def calc_ie(self):
        self.calc_included_size()
        self.calc_excluded_size()
        self.calc_included_folder_count()
        self.calc_included_file_count()
        self.calc_excluded_folder_count()
        self.calc_excluded_file_count()
        return
    
    def calc_all(self):
        self.calc_size()
        self.calc_ie()
