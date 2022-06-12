import json
import os.path

class PackFIO:
    def __init__(self, path_definition:dict[tuple[str,str],list[str]], packfio_data):
        """PackFIO: Packaging File I/O"""
        self.paths = []
        self.base_paths = {} # base path -> packed base path
        for (base, base_packed), paths in path_definition.items():
            self.base_paths[base] = base_packed
            for path in paths:
                self.paths.append(path)
        self.packfio_data = packfio_data


    def is_packed(self):
        return bool(self.packfio_data)


    def read_file(self, path, require_known=True):
        if self.is_packed():
            if path in self.packfio_data:
                return self.packfio_data[path]
            else:
                raise FileNotFoundError('Not in packed files:', str(path))
        if require_known and not path in self.paths:
            raise RuntimeError('Tried to read file that won\'t be zipped', path)
        with open(path, 'r') as file_in:
            text = file_in.read()
        return text
    def write_file(self, path, text):
        if self.is_packed():
            raise RuntimeError('Tried to write to packed data')
        with open(path, 'w') as file_out:
            file_out.write(text)



    def get_packing_path(self, packing_dir, path):
        for base_path, base_path_packed in self.base_paths.items():
            if path.startswith(base_path):
                relpath = os.path.relpath(path, base_path)
                packing_relpath = os.path.normpath(os.path.join(base_path_packed, relpath))
                return os.path.normpath(os.path.join(packing_dir, packing_relpath))
        raise RuntimeError('Failed to get packing path', path)
    def pack_files(self, packing_dir, packed_data_relpath):
        if self.is_packed():
            raise RuntimeError('Tried to pack when already packed')
        packed_data_path = os.path.normpath(os.path.join(packing_dir, packed_data_relpath))
        packed_files = {}
        for path in self.paths:
            packing_path = self.get_packing_path(packing_dir, path)
            with open(packing_path, 'r') as file_in:
                packed_files[path] = file_in.read()
        packed_text = 'packfio_data = ' + json.dumps(packed_files)
        with open(packed_data_path, 'w') as file_out:
            file_out.write(packed_text)