from copy import deepcopy
from collections import defaultdict
from inspect import *
from itertools import *
import os
from pprint import pformat
import re
# ------------------------------------------------------------------------------

def module_relative_path(module, path):
    root = os.path.dirname(os.path.abspath(module))
    new_path = []
    for dir_ in path.split(os.sep):
        if dir_ == '..':
            root = os.path.dirname(root)
        elif dir_ == '.':
            pass
        else:
            new_path.append(dir_)
    new_path = os.path.join(root, *new_path)
    return os.path.abspath(new_path)

def aspect_to_dataframe(aspect):
    import pandas as pd
    pd.options.display.width = 1000

    def add_instance(item, id_, instance):
        item[id_] = instance
        return item

    data = pd.DataFrame(aspect._specs.values())
    data['instances'] = None
    data.instances = data.instances.apply(lambda x: {})

    cols = ['fullname', 'name', 'module', 'class_', 'kind',  'level', 'args',
            'kwargs', 'varargs', 'varkwargs', 'object', 'instances']
    data = data[cols]

    for id_, item in aspect._library.iteritems():
        row = data[
            (data.module == item['module']) &
            (data.class_ == item['class_']) &
            (data.name == '__init__')
        ]
        data.loc[row.index, 'instances'] = data.loc[row.index, 'instances'].apply(
            lambda x: add_instance(x, id_, item['instance'])
        )

    return data

def get_level(item):
    lut = {
             'public': '^__init__$|^[^_]',
        'semiprivate': '^_[^_A-Z]',
            'private': '^_[A-Z].*[^_][^_]$',
            'builtin': '^__(?!init).*__$'
    }
    for key, regex in lut.iteritems():
        if re.search(regex, item):
            return key
    return 'unknown'

def function_to_spec(func):
    spec = getargspec(func).__dict__
    args = spec['args']
    kwargs = spec['defaults']

    if len(args) > 0:
        if args[0] == 'self':
            args = args[1:]

    if kwargs == None:
        kwargs = {}
    else:
        kwargs = {k:v for k,v in zip(args[-len(kwargs):], kwargs)}
        args = args[:len(args) - len(kwargs)]

    spec['args'] = args
    spec['kwargs'] = kwargs
    spec['varkwargs'] = spec['keywords']
    del spec['defaults']
    del spec['keywords']

    spec['level'] = get_level(func.__name__)
    return spec

def class_to_specs(class_):
    def attribute_to_spec(attr):
        spec = attr.__dict__
        spec['class_'] = spec['defining_class'].__name__
        del spec['defining_class']

        spec['args'] = []
        spec['varargs'] = None
        spec['kwargs'] = {}
        spec['varkwargs'] = None

        spec['level'] = get_level(spec['name'])
        if spec['kind'] == 'method' and spec['level'] != 'builtin':
            spec.update(function_to_spec(getattr(class_, spec['name'])))
        return spec

    for attr in classify_class_attrs(class_):
        yield attribute_to_spec(attr)

def get_module_specs(module):
    def func(item):
        try:
            if getmodule(item).__name__ == module.__name__:
                if isclass(item) or isfunction(item):
                    return True
            return False
        except:
            return False

    for name, obj in getmembers(module, predicate=func):
        if isfunction(obj):
            spec = dict(name=name, object=obj, module=module.__name__, kind='function')
            spec['class_'] = None
            spec.update(function_to_spec(obj))
            yield spec

        elif isclass(obj):
            for cspec in class_to_specs(obj):
                spec = dict(name=name, module=module.__name__)
                spec.update(cspec)
                spec['object'] = obj
                yield spec

def fire(func, args=[], kwargs={}):
    if args != [] and kwargs != {}:
        return func(*args, **kwargs)

    if args != [] and kwargs == {}:
        return func(*args)

    if args == [] and kwargs != {}:
        return func(**kwargs)

    if args == [] and kwargs == {}:
        return func()
# ------------------------------------------------------------------------------

class ClientDataConformer(object):
    def __init__(self, specs, config, default={}):
        self._specs = specs
        self._config = config
        self._default = default

    def to_args(self, args):
        return [dict(name=arg, value=None) for arg in args]

    def to_kwargs(self, kwargs):
        return [dict(name=key, value=val) for key, val in kwargs.items()]

    def to_function(self, item):
        spec = dict(
            name=item['name'],
            args=self.to_args(item['args']),
            kwargs=self.to_kwargs(item['kwargs'])
        )
        spec = self.configure_spec(item, spec)
        return spec

    def add_object(self, parent, key, item):
        if key not in parent:
            parent[key] = []
        parent[key].append(item)

    def configure_spec(self, item, spec):
        name = item['fullname']
        lib = self._config['library']
        if lib.has_key(name):
            conf = lib[name]

            if conf.has_key('default_args'):
                spec['args'] = self.to_kwargs(conf['default_args'])

            if conf.has_key('default_kwargs'):
                spec['kwargs'] = self.to_kwargs(conf['default_kwargs'])

        return spec

    @property
    def data(self):
        modules = defaultdict(lambda: {})
        for item in self._specs.values():
            kind = item['kind']
            mod = modules[item['module']]
            if item['class_'] is None:
                if kind == 'function':
                    func = self.to_function(item)
                    self.add_object(mod, 'functions', func)

                if kind == 'data':
                    var = dict(name=item['name'], value=self._default)
                    self.add_object(mod, 'variables', var)

            else:
                cls_name = item['class_']
                cls = dict(name=item['class_'])
                if 'classes' not in mod:
                    mod['classes'] = [cls]
                else:
                    temp = list(filter(lambda x: x['name'] == cls_name, mod['classes']))
                    if temp != []:
                        cls = temp[0]
                    else:
                        mod['classes'].append(cls)

                if kind == 'method':
                    meth = self.to_function(item)
                    self.add_object(cls, 'methods', meth)
                if kind == 'data':
                    attr = dict(name=item['name'], value=self._default)
                    self.add_object(cls, 'attributes', attr)
                if kind == 'property':
                    prop = dict(name=item['name'], value=self._default)
                    self.add_object(cls, 'properties', prop)

            modules[item['module']] = mod

        modules = dict(modules)

        config = deepcopy(self._config)
        del config['library']
        config.update(dict(library=modules))
        return config
    # ------------------------------------------------------------------------------

    # def to_config(config):
    #     def conform_library(items):
    #         lib = []
    #         for item in items:
    #             temp = dict(
    #                 name=None,
    #                 module=None,
    #                 class_=None,
    #                 kind=None,
    #                 default_args=[],
    #                 default_kwargs={},
    #                 default_value=None,
    #                 blacklist=False
    #             )
    #             temp.update(item)
    #             lib.append(temp)
    #         return lib

    #     with open(config) as f:
    #         conf = yaml.load(f)

    #     if 'library' in config:
    #         lib = conform_library(config['library'])

    #     api_url: http://localhost:5000/api
    #     title: aspect

    #     dashboard = [
    #             dict(
    #                 title='card-0'
    #                 html='<div></div>'
    #                 flex_grow='1'
    #                 flex_shrink='0'
    #                 width='250px'
    #                 height='250px'
    #                 id='0'
    #             )
    #         ] * 6

    #     blacklist = []
    #     for item in filter(lambda x: x['blacklist'] == True, lib):
    #         blacklist[item['module']].append(item['name'])

    #     lib = filter(lambda x: x['blacklist'] == False, lib)
    #     config['library'] = list(lib)
    #     return config
# ------------------------------------------------------------------------------

def main():
    '''
    Run help if called directly
    '''

    import __main__
    help(__main__)
# ------------------------------------------------------------------------------

__all__ = [
    'module_relative_path',
    'aspect_to_dataframe',
    'get_level',
    'function_to_spec',
    'class_to_specs',
    'get_module_specs',
    'fire',
    'ClientDataConformer'
    # 'to_config'
]

if __name__ == '__main__':
    main()
