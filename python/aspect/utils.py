import re
from itertools import *
from inspect import *
from pprint import pprint, pformat
# ------------------------------------------------------------------------------

class Item(dict):
    def __init__(self, args=None, **kwargs):
        if args:
            super(Item, self).__init__(args, **kwargs)
        else:
            super(Item, self).__init__(**kwargs)
        
        if args:
            for x in args:
                print(x)
                if not isinstance(x[0], str):
                    warn(str(x[0]) + ' is not a string, skipping.')
                    continue
                setattr(self, x[0], x[1])
                
        elif kwargs:
            for key, val in kwargs.iteritems():
                setattr(self, key, val)
    
    def __setitem__(self, key, val):
        super(Item, self).__setitem__(key, val)
        setattr(self, key, val)
# ------------------------------------------------------------------------------

def get_item_type(item):
    if ismodule(item):
        return 'module'
    elif isabstract(item):
        return 'class'
    elif isclass(item):
        return 'instance'
    elif ismethod(item):
        return 'method'
    elif isinstance(item, property):
        return 'property'
    elif isfunction(item):
        return 'function'
    elif isgenerator(item):
        return 'generator'
    elif isgeneratorfunction(item):
        return 'generator_function'
    elif isbuiltin(item):
        return 'builtin'
    else:
        return 'unknown'

def filter_items(items, levels, key_func=lambda x: x):
    lut = {
             'public': '^[^_]',
        'semiprivate': '^_[^_A-Z]',
            'private': '^_[A-Z].*[^_][^_]$',
            'builtin': '^__.*__$'
    }
    regex = '|'.join([lut[x] for x in levels])
    regex += '|__init__'
    return filter(lambda x: re.search(regex, key_func(x)), items)

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
        args = args[:len(kwargs)+1]        
        
    return {
             'args': [],
        'arg_names': args,
           'kwargs': kwargs
        #   'varargs': argspec.varargs != None,
        # 'varkwargs': argspec.keywords != None
    }
        
def class_to_aspect(class_, levels=['public', 'semiprivate', 'private', 'builtin']):   
    members = getmembers(class_)
    members = filter_items(members, levels, lambda x: x[0])
    
#     lut = {
#              'public': '^[^_]',
#         'semiprivate': '^_[^_A-Z]',
#             'private': '^_[A-Z].*[^_][^_]$',
#             'builtin': '^__.*__$'
#     }
    
#     mem = dict(members)
#     if mem.has_key('__class__'):
#         name = mem['__class__'].__name__
#         if name != 'type':
#             lut['semiprivate'] = '^_' + '(?!'+ name + '|_)'
#             lut['private'] = '^_' + name + '__'
    
#     regex = '|'.join([lut[x] for x in levels])
#     members = filter(lambda x: re.search(regex, x[0]), members)
    
    methods = ['method', 'function', 'generator_function']
    methods = filter(lambda x: get_item_type(x[1]) in methods, members)
    methods = {k:function_to_aspect(v) for k,v in methods}
    
    attrs = ['unknown']
    attrs = filter(lambda x: get_item_type(x[1]) in attrs, members)
    attrs = {attr: getattr(class_, attr) for attr, mem in attrs}
    
    props = ['property']
    props = filter(lambda x: get_item_type(x[1]) in props, members)
    props = {attr: getattr(class_, attr).fget(class_) for attr, mem in props}
    
    spec = {'class_attributes': attrs, 'methods': methods, 'properties': props}
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
    'get_item_type',
    'filter_items',
    'fire',
    'function_to_aspect',
    'class_to_aspect'
]

if __name__ == '__main__':
    main()