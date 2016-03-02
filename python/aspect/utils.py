import re
from itertools import *
from inspect import *
from pprint import pprint, pformat
from warnings import warn
# ------------------------------------------------------------------------------

class Item(dict):
    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)
        for key, val in self.iteritems():
            setattr(self, key, val)
    
    def __setitem__(self, key, val):
        super(Item, self).__setitem__(key, val)
        setattr(self, key, val)
# ------------------------------------------------------------------------------

def get_object_type(object_):
    if ismodule(object_):
        return 'module'
    elif isabstract(object_):
        return 'abstract'
    elif isclass(object_):
        return 'class'
    elif ismethod(object_):
        return 'method'
    elif isdatadescriptor(object_):
        return 'data_descriptor'
    elif isfunction(object_):
        return 'function'
    elif isgenerator(object_):
        return 'generator'
    elif isgeneratorfunction(object_):
        return 'generator_function'
    elif isroutine(object_):
        return 'routine'
    elif isbuiltin(object_):
        return 'builtin'
    else:
        return 'unknown'

def get_member_info(item):
    for key, val in getmembers(item):
        type_ = get_object_type(val)
        if type_ != 'unknown':
            yield key, val, type_
        else:
            if re.search('^__.*__$', key):
                yield key, val, 'builtin'
            elif hasattr(item, key):
                yield key, val, 'attribute'
            else:
                yield key, val, 'unknown'

def filter_items(items, levels, key_func=lambda x: x):
    lut = {
             'public': '^[^_]',
        'semiprivate': '^_[^_A-Z]',
            'private': '^_[A-Z].*[^_][^_]$',
            'builtin': '^__.*__$'
    }
    regex = '|'.join([lut[x] for x in levels])
    regex += '|__init__'
    return filter(lambda x: re.search(regex, key_func(*x)), items)

def fire(func, spec):
    args = []
    kwargs = {}
    if spec.has_key('args'):
        args = spec['args']
    if spec.has_key('kwargs'):
        kwargs = spec['kwargs']

    if args != [] and kwargs != {}:
        return func(*args, **kwargs)

    if args != [] and kwargs == {}:
        return func(*args)

    if args == [] and kwargs != {}:
        return func(**kwargs)

    if args == [] and kwargs == {}:
        return func()

def function_to_aspect(func):
    argspec = getargspec(func)
    args = argspec.args
    kwargs = argspec.defaults
    
    if args[0] == 'self':
        args = args[1:]

    if kwargs == None:
        kwargs = {}
    else:
        kwargs = {k:v for k,v in zip(args[-len(kwargs):], kwargs)}
        args = args[:len(kwargs)]        
        
    return {
             'args': [],
        'arg_names': args,
           'kwargs': kwargs
        #   'varargs': argspec.varargs != None,
        # 'varkwargs': argspec.keywords != None
    }
        
def class_to_aspect(class_, levels=['public', 'semiprivate', 'private']):
    init = function_to_aspect(class_.__init__)
    instance = class_(*init['args'], **init['kwargs'])
    
    # retrieve and merge class and instance members 
    members = {k:(v,t) for k,v,t in get_member_info(instance)}
    class_members = {k:(v,t) for k,v,t in get_member_info(class_)}
    members.update(class_members)
    members = [[k, v[0], v[1]] for k,v in members.iteritems()]
    
    members = filter_items(members, levels, key_func=lambda k,v,t: k)
    
    methods = ['method', 'function', 'generator_function']
    methods = filter(lambda x: x[2] in methods, members)
    methods = {k:function_to_aspect(v) for k,v,t in methods}
    
    attrs_ = ['attribute', 'data_descriptor']
    attrs_ = filter(lambda x: x[2] in attrs_, members)
    attrs = {}
    for k,v,t in attrs_:
        if t != 'attribute':
            v = None
        attrs[k] = v
    
    spec = {'attrs': attrs, 'methods': methods}
    return spec
# ------------------------------------------------------------------------------

def main():
    '''
    Run help if called directly
    '''
    
    import __main__
    help(__main__)
# ------------------------------------------------------------------------------

__all__ = [
    'Item',
    'get_object_type',
    'get_member_info',
    'filter_items',
    'fire',
    'function_to_aspect',
    'class_to_aspect'
]

if __name__ == '__main__':
    main()