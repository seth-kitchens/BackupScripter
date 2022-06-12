
# move functions here to a better location if there is one, and at least several functions belonging there

def update_member(obj, d, name):
    if name in d and name in dir(obj):
        obj.__dict__[name] = d[name]