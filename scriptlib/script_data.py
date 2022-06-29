import json
import os
import sys
from pprint import pprint

from gplib import utils as gp_utils
from gplib import DateString
from scriptlib.packfio import PackFIO

__all__ = [
    'ScriptVariable', 'ScriptMetadata',
    'ScriptData'
]

class ScriptVariable:
    def __init__(self, name, default_value, info=None, info_button=None, to_serializable_func=None, load_serializable_func=None, do_save=True) -> None:
        self.name = name
        self.default_value = default_value
        self.value = self.default_value
        self.info = info
        self.info_button = info_button if info_button != None or not info else bool(len(info) < 50)
        self.to_serializable_func = to_serializable_func
        self.load_serializable_func = load_serializable_func
        self.do_save = do_save
    def get(self):
        return self.value
    def set(self, value):
        self.value = value
    def to_serializable(self):
        if self.to_serializable_func != None:
            return self.to_serializable_func(self.value)
        return self.value
    def load_serializable(self, packable):
        if self.load_serializable_func != None:
            self.value = self.load_serializable_func(packable)
        else:
            self.value = packable
def ScriptMetadata(*args, **kwargs):
    kwargs['do_save'] = False
    return ScriptVariable(*args, **kwargs)


class ScriptData:
    GETDATA = '--getdata'
    def __init__(self, packfio, data_file):
        self.packfio:PackFIO = packfio
        self.data_file:str = data_file
    
    # 'private_name' is the member variable name, 'public_name' is the property name
    # avoiding 'variable_name/property_name' as 'variable' is ambiguous with ScriptVariable
    def is_var(self, public_name=None, private_name=None):
        if public_name != None and private_name == None:
            private_name = '_' + public_name
        if not private_name in self.__dict__:
            return False
        if not isinstance(self.__dict__[private_name], ScriptVariable):
            return False
        return True
    def var(self, public_name):
        return self.__dict__['_' + public_name]
    def to_private_name(self, public_name):
        return '_' + public_name
    def to_public_name(self, private_name):
        return private_name[1:]
    
    def to_dict(self):
        d = {}
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                name = k[1:]
                if isinstance(v, ScriptVariable):
                    name = k[1:]
                    d[name] = v.get()
        return d
    @classmethod
    def from_dict(cls, d:dict):
        if not issubclass(cls, ScriptData):
            raise TypeError
        obj = cls()
        obj.load_dict(d)
        return obj
    def load_dict(self, d:dict):
        if not issubclass(self.__class__, ScriptData):
            raise TypeError
        for k, v in d.items():
            if self.is_var(k):
                self.var(k).set(v)
    def to_serializable_dict(self, d:dict=None, save_all=False):
        """
        save_all: saves all script variables, including those with do_save=False
        """
        if d == None:
            d = {}
        for k, v in self.__dict__.items():
            if self.is_var(private_name=k) and (v.do_save or save_all):
                d[self.to_public_name(k)] = v.to_serializable()
        return d
    def load_serializable_dict(self, d:dict):
        for k, v in d.items():
            if self.is_var(public_name=k):
                self.var(k).load_serializable(v)
    
    def save_to_file(self, path=None, save_all=False, bypass_packfio=False):
        """
        path: defaults to self.data_file if None
        save_all: force save script variables with do_save=False
        bypass_packfio: write to file directly
        """
        path = path if path != None else self.data_file
        if not path:
            raise ValueError('Save file has not been specified')
        sdata = self.to_serializable_dict(save_all=save_all)
        if bypass_packfio:
            with open(path, 'w') as file_out:
                file_out.write(json.dumps(sdata))
        else:
            self.packfio.write_file(path, json.dumps(sdata, indent=4))
    def load_save_file(self, path=None, require_known=True):
        """path defaults to self.data_file if None"""
        path = path if path != None else self.data_file
        if not self.packfio.is_packed():
            if not os.path.exists(path):
                raise ValueError('Cannot open, does not exist: "' + path + '"')
            if not os.path.isfile(path):
                raise ValueError('Cannot open, not a file: "' + path + '"')
        sdata = json.loads(self.packfio.read_file(path, require_known=require_known))
        self.load_serializable_dict(sdata)
    @classmethod
    def verify_file_is_script(cls, path):
        if not path.endswith('.pyz'):
            return False
        return True
    def load_pyz(self, path):
        if not self.__class__.verify_file_is_script(path):
            raise ValueError('File is not a .pyz script')
        stripped_name = path[:-4]
        comm_file = stripped_name + DateString.process('_YYYYMMDD_HHmm') + '.temp'
        command = '{} "{}" {} {}'.format(sys.executable, path, self.GETDATA, comm_file)
        os.system(command)
        self.load_save_file(comm_file, require_known=False)
        os.remove(comm_file)
    def get_data(self):
        i_flag = sys.argv.index(self.GETDATA)
        comm_file = sys.argv[i_flag+1]
        if os.path.exists(comm_file):
            raise FileExistsError(comm_file)
        parent_dir = gp_utils.parent_dir(comm_file)
        if not os.path.isdir(parent_dir):
            raise Exception('Bad parent folder', parent_dir)
        self.save_to_file(comm_file, bypass_packfio=True)
    def print(self):
        pprint(self.to_dict())
