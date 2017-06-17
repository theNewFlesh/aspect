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

    def _to_params(self, params):
        if params is None:
            return []

        if isinstance(params, list):
            params = {p:self._default for p in params}
        return [dict(name=key, value=val) for key, val in params.items()]

    def _add_function(self, module, item):
        spec = dict(
            name=item['name'],
        )
        if item.has_key('args'):
            spec['args'] = self._to_params(item['args'])

        if item.has_key('kwargs'):
            spec['kwargs'] = self._to_params(item['kwargs'])

        spec = self._configure_func(item, spec)
        self._add_object(module, 'functions', spec)

    def _add_variable(self, module, item):
        spec = dict(
            name=item['name'],
            value=item['value']
        )
        spec = self._configure_attr(item, spec)
        self._add_object(module, 'variables', spec)

    def _add_method(self, cls, item):
        spec = dict(
            name=item['name'],
            args=self._to_params(item['args']),
            kwargs=self._to_params(item['kwargs'])
        )
        spec = self._configure_func(item, spec)
        self._add_object(cls, 'methods', spec)

    def _add_property(self, cls, item):
        spec = dict(
            name=item['name']
        )
        self._add_object(cls, 'properties', spec)

    def _add_attribute(self, cls, item):
        spec = dict(
            name=item['name']
        )
        if item.has_key('value'):
            spec['value'] = item['value']

        spec = self._configure_attr(item, spec)
        self._add_object(cls, 'attributes', spec)

    def _add_object(self, parent, key, item):
        if key not in parent:
            parent[key] = []
        parent[key].append(item)

    def _configure_func(self, item, spec):
        name = item['fullname']
        lib = self._config['library']
        if lib.has_key(name):
            conf = lib[name]

            if conf.has_key('default_args'):
                spec['args'] = self._to_params(conf['default_args'])

            if conf.has_key('default_kwargs'):
                spec['kwargs'] = self._to_params(conf['default_kwargs'])

        return spec

    def _configure_attr(self, item, spec):
        name = item['fullname']
        lib = self._config['library']
        if lib.has_key(name):
            conf = lib[name]

            if conf.has_key('default_value'):
                spec['value'] = conf['default_value']

        return spec

    @property
    def data(self):
        modules = defaultdict(lambda: {})
        for item in self._specs.values():
            kind = item['kind']
            mod = modules[item['module']]

            if item['class_'] is None:
                if kind == 'function':
                    self._add_function(mod, item)
                if kind == 'data':
                    self._add_variable(mod, item)

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
                    self._add_method(cls, item)

                if kind == 'data':
                    self._add_attribute(cls, item)

                if kind == 'property':
                    self._add_property(cls, item)

            modules[item['module']] = mod

        modules = dict(modules)

        config = deepcopy(self._config)
        del config['library']
        config.update(dict(library=modules))
        return config
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
]

if __name__ == '__main__':
    main()
