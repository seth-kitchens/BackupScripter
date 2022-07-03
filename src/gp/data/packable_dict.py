from src.gp import utils as gp_utils

__all__ = [
    'PackableDict',
    'Dictable'
]

class PackableDict:
    def load_dict(self, d):
        if not isinstance(d, dict):
            raise TypeError('d not dict')
        for k in gp_utils.get_instance_vars(self).keys():
            if k != 'self' and k != 'd':
                self.__dict__[k] = d[k]
    def to_dict(self):
        d = {}
        for k, v in gp_utils.get_instance_vars(self).items():
            if k != 'self' and k != 'd':
                d[k] = v
        return d

class Dictable():
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
