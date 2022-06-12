from typing import Any
from abc import ABC, abstractmethod

def flip_pairs_in_list(pair_list: list[tuple[Any, Any]]):
    l = []
    for pair in pair_list:
        l.append((pair[1], pair[0]))
    return l

def get_instance_vars(obj):
    names = set(dir(obj)).difference(dir(obj.__class__))
    return {name:obj.__dict__[name] for name in names}

class PackableDict:
    def load_dict(self, d):
        if not isinstance(d, dict):
            raise TypeError('d not dict')
        for k in get_instance_vars(self).keys():
            if k != 'self' and k != 'd':
                self.__dict__[k] = d[k]
    def to_dict(self):
        d = {}
        for k, v in get_instance_vars(self).items():
            if k != 'self' and k != 'd':
                d[k] = v
        return d

class Dictable(ABC):
    def load_dict(self, d:dict):
        if not isinstance(d, dict):
            raise TypeError('d not dict')
        self.d.load_dict(d)
        return self
    def to_dict(self):
        return self.d.to_dict()
    @classmethod
    def from_dict(cls, d, *args, **kwargs):
        return cls(*args, **kwargs).load_dict(d)
