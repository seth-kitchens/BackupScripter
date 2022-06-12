from typing import Any

# Works like a dict, but keeps old values
# allows multiple of same key, but not multiple key-value pairs
class Multidict:
    def __init__(self) -> None:
        self.value_lists = {}
    def __getitem__(self, key):
        value_list = self.value_lists[key]
        if not value_list:
            return None
        return value_list[-1]
    def __setitem__(self, key, value):
        if not key in self.value_lists.keys():
            self.value_lists[key] = []
        value_list = self.value_lists[key]
        if value in value_list: # Move to back
            value_list.remove(value)
        value_list.append(value)
        
    def keys(self):
        return self.value_lists.keys()
    def values(self):
        values = []
        for value_list in self.value_lists.values():
            values.extend(value_list[-1])
        return values
    def items(self):
        pairs = []
        for key, value_list in self.value_lists.items():
            pairs.append((key, value_list[-1]))
        return pairs
    def update(self, d:dict):
        for k, v in d.items():
            self[k] = v
        return
    def update_pairs(self, l:list[tuple[Any, Any]]):
        for k, v in l:
            self[k] = v
        return
    def get_value_list(self, key):
        values = []
        for v in self.value_lists[key]:
            values.append(v)
        return values
    def all_values(self):
        values = []
        for value_list in self.value_lists.values():
            values.extend(value_list)
        return values
    def all_items(self):
        pairs = []
        for key, value_list in self.value_lists.items():
            for value in value_list:
                pairs.append((key, value))
        return pairs
    def to_dict(self):
        d = {}
        for k, v in self.items():
            d[k] = v
        return d
    def update_md(self, md):
        for k, v in md.all_items():
            self[k] = v
        return
