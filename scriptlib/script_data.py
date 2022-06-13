import json
import os
import sys
from pprint import pprint

from gplib.fs import utils as fs_utils

class ScriptVariable:
    def __init__(self, name, default_value, info=None, info_button=None, to_string_func=None, load_string_func=None, do_save=True) -> None:
        self.name = name
        self.default_value = default_value
        self.value = self.default_value
        self.info = info
        self.info_button = info_button if info_button != None or not info else bool(len(info) < 50)
        self.to_string_func = to_string_func
        self.load_string_func = load_string_func
        self.do_save = do_save
    def get(self):
        return self.value
    def set(self, value):
        self.value = value
    def to_string(self):
        if self.to_string_func:
            return self.to_string_func(self.value)
        return json.dumps(self.value)
    def load_string(self, s):
        if self.load_string_func:
            self.value = self.load_string_func(s)
        else:
            self.value = json.loads(s)

class ScriptDataGroup:
    def __init__(self, name, svs):
        self.name = name
        self.svs = svs

class ScriptMetadataGroup:
    def __init__(self, name, svs):
        self.name = name
        self.svs = svs
        for sv in self.svs:
            sv.do_save = False

class ScriptDataManager:
    GETDATA = '--getdata'
    def __init__(self, packfio, script_data_file=None, read_only=False):
        self.groups = []
        self.svs = {}
        self.script_data_file = script_data_file
        self.packfio = packfio
        self.read_only = read_only
    def __getitem__(self, name):
        return self.svs[name].get()
    def __setitem__(self, name, value):
        if self.read_only:
            raise RuntimeError('ScriptDataManager is in read only mode')
        self.svs[name].set(value)
    def set_read_only(self, value=True):
        self.read_only = value
    def define_variables(self, groups):
        for group in groups:
            self.groups.append(group)
            for sv in group.svs:
                self.svs[sv.name] = sv
    def to_dict(self):
        d = {}
        for name, sv in self.svs.items():
            d[name] = sv.get()
        return d
    def load_dict(self, d):
        for name, sv in self.svs.items():
            if name in d:
                sv.set(d[name])
    def save_to_file(self, path=None, force_save=False):
        path = path if path else self.script_data_file
        if not path:
            raise Exception('Save file has not been specified')
        data = {}
        for name, sv in self.svs.items():
            if sv.do_save or force_save:
                data[name] = sv.to_string()
        if path == self.script_data_file:
            self.packfio.write_file(path, json.dumps(data, indent=4))
        else:
            with open(path, 'w') as file_out:
                file_out.write(json.dumps(data))
    def load_save_file(self, path=None, require_known=True):
        path = path if path else self.script_data_file
        if not self.packfio.is_packed():
            if not os.path.exists(path):
                raise ValueError('Cannot open, does not exist: "' + path + '"')
            if not os.path.isfile(path):
                raise ValueError('Cannot open, not a file: "' + path + '"')
        data = json.loads(self.packfio.read_file(path, require_known=require_known))
        for name, sv in self.svs.items():
            if name in data:
                sv.load_string(data[name])
    def verify_file_is_script(path):
        if not path.endswith('.pyz'):
            return False
        return True
    def load_pyz(self, path):
        if not self.__class__.verify_file_is_script(path):
            raise ValueError('File is not a .pyz script')
        stripped_name = path[:-4]
        comm_file = stripped_name + fs_utils.DateString.process('_YYYYMMDD_HHmm') + '.temp'
        command = '{} "{}" {} {}'.format(sys.executable, path, self.GETDATA, comm_file)
        os.system(command)
        self.load_save_file(comm_file, require_known=False)
        os.remove(comm_file)
    def get_data(self):
        i_flag = sys.argv.index(self.GETDATA)
        comm_file = sys.argv[i_flag+1]
        if os.path.exists(comm_file):
            raise FileExistsError(comm_file)
        parent_dir = fs_utils.parent_dir(comm_file)
        if not os.path.isdir(parent_dir):
            raise Exception('Bad parent folder', parent_dir)
        self.save_to_file(comm_file)
    def print(self):
        pprint(self.to_dict())

class ScriptEditor:
    def __init__(self):
        pass