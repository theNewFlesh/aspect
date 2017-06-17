from copy import deepcopy
from collections import *
from functools import wraps, partial
from inspect import *
from itertools import *
from pprint import pformat, pprint
from random import randint
import re
import sys

from schematics.exceptions import ValidationError
import yaml

from aspect.core.utils import *
from validators import *
# ------------------------------------------------------------------------------

class Aspect(object):
    def __init__(self, levels=['public'], config=None):
        '''
        Args:
            levels opt(list):
                options include:
                    'public'
                    'semiprivate'
                    'private'
                    'builtin'
                default: ['public']
        '''
        self.levels     = levels
        self._specs     = {}
        self._library   = {}
        self._blacklist = {}
        self._config    = self._to_config(config)
    # --------------------------------------------------------------------------

    def __repr__(self):
        output = [
                   'LEVELS:', '\t' + ', '.join(self.levels) + '\n',
                    'SPECS:', pformat(self._specs) + '\n',
                  'LIBRARY:', pformat(self._library) + '\n',
        ]
        return '\n'.join(output)
    # --------------------------------------------------------------------------

    def _to_config(self, fullpath):
        if fullpath:
            with open(fullpath) as f:
                config = Config(yaml.load(f)).to_native()

            lib = {}
            for key, val in config['library'].items():
                val['fullname'] = key
                lib[key] = LibraryItem(val).to_native()

            config['library'] = lib

            for key, val in config['library'].items():
                if val['blacklist']:
                    self._blacklist[key] = val

            return config
        # ----------------------------------------------------------------------

        dash = dict(
            flex_grow=1,
            flex_shrink=0,
            height='250px',
            html='<div></div>',
            id=0,
            title='card-0',
            width='250px'
        )

        conf = dict(
            title='aspect',
            api_url='http://localhost:5000/api',
            dashboard=[dash],
            library={}
        )

        return conf

    def _in_blacklist(self, spec):
        return self._blacklist.has_key(self._get_fullname(spec))

    def _get_fullname(self, spec):
        if spec['class_']:
            return '.'.join([ spec['module'], spec['class_'], spec['name'] ])
        return '.'.join([ spec['module'], spec['name'] ])
    # --------------------------------------------------------------------------

    def register(self, module):
        specs = get_module_specs(sys.modules[module])
        specs = filter(lambda x: x['level'] in self.levels, specs)
        specs = filter(lambda x: not self._in_blacklist(x), specs)

        for spec in specs:
            name = self._get_fullname(spec)
            spec['fullname'] = name
            if self.config['library'].has_key(name):
                spec.update(self._config['library'][name])
            self._specs[name] = spec

    def deregister(self, func=None, class_=None):
        def decorator(func):
            spec = dict(
                module=getmodule(func).__name__,
                class_=None,
                name=func.__name__,
                blacklist=True
            )
            if class_:
                spec['class_'] = class_

            name = self._get_fullname(spec)
            spec['fullname'] = name
            self._blacklist[name] = spec

            @wraps
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator
    # --------------------------------------------------------------------------

    def request(self, spec, json_errors=True):
        if json_errors:
            try:
                return self._request(spec)
            except ValidationError as e:
                return {'error': e.messages}
        else:
            return self._request(spec)

    def _request(self, spec):
        action = spec['action']
        if action == 'create':
            spec = CreateSpec(spec)
            spec.validate()
            return self._create(spec)

        elif action == 'read':
            spec = ReadSpec(spec)
            spec.validate()
            return self._read(spec)

        elif action == 'update':
            spec = UpdateSpec(spec)
            spec.validate()
            return self._update(spec)

        elif action == 'delete':
            spec = DeleteSpec(spec)
            spec.validate()
            return self._delete(spec)

        elif action == 'execute':
            if spec.has_key('function'):
                spec = FunctionSpec(spec)
                spec.validate()
                return self._execute_function(spec)

            elif spec.has_key('method'):
                spec = MethodSpec(spec)
                spec.validate()
                return self._execute_method(spec)

        else:
            raise ValidationError(action + ' is not a valid action')
    # --------------------------------------------------------------------------

    def _search(self, spec):
        def validate(rows, keys, row_keys):
            for key, rkey in zip(keys, row_keys):
                if spec.has_key(key):
                    rows = filter(lambda row: row[rkey] == spec[key], rows)
                    if len(rows) < 1:
                        raise ValidationError(spec[key] + ' ' +  key + ' not found')
            return rows

        if spec.has_key('id_'):
            id_ = spec['id_']
            if not self._library.has_key(id_):
                raise ValidationError( str(id_) + ' id not found' )

            spec['module'] = self._library[id_]['module']
            spec['class_'] = self._library[id_]['class_']

        rows = self._specs.values()
        rows = validate(rows, ['module', 'class_'], ['module', 'class_'])
        rows = validate(rows, ['method', 'attribute', 'function'], ['name'] * 3)

        return rows
    # --------------------------------------------------------------------------

    def _create(self, spec):
        row = self._search(spec.to_native())
        row = filter(lambda x: x['name'] == '__init__', row)
        if len(row) > 1:
            raise ValidationError( 'multiple inits found for ' + spec['class_'] )
        row = row[0]

        id_ = randint(1000000000, 9999999999)
        while id_ in self._library.keys():
            id_ = randint(1000000000, 9999999999)

        item = {
            'instance': fire(row['object'], row['args'], row['kwargs']),
            'module': row['module'],
            'class_': row['class_']
        }
        self._library[id_] = item

        response = id_
        return response

    def _read(self, spec):
        row = self._search(spec.to_native())
        response = getattr(self._library[ spec['id_'] ]['instance'], spec['attribute'])
        return response

    def _update(self, spec):
        row = self._search(spec.to_native())
        if len(row) > 1:
            raise ValidationError( 'multiple ' + spec['attribute'] + ' attributes found for ' + row[0]['class_'] )

        id_ = spec['id_']
        attr = spec['attribute']
        value = spec['value']

        setattr(self._library[id_]['instance'], attr, value)
        response = getattr(self._library[id_]['instance'], attr) == value

        return response

    def _delete(self, spec):
        id_ = spec['id_']
        response = False

        if self._library.has_key(id_):
            del self._library[id_]
            response = not self._library.has_key(id_)
        else:
            raise ValidationError('no instance with ' + str(id_) + ' id exists')

        return response

    def _execute_method(self, spec):
        row = self._search(spec.to_native())
        if len(row) > 1:
            raise ValidationError( 'multiple ' + spec['method'] + ' methods found for ' + spec['class_'] )

        func = getattr(self._library[ spec['id_'] ]['instance'], spec['method'])
        response = fire(func, spec['args'], spec['kwargs'])
        return response

    def _execute_function(self, spec):
        row = self._search(spec.to_native())
        if len(row) > 1:
            raise ValidationError( 'multiple ' + spec['function'] + ' functions found for ' + spec['module'] )
        row = row[0]

        response = fire(row['object'], spec['args'], spec['kwargs'])
        return response
    # --------------------------------------------------------------------------

    def to_client_data(self, default={}):
        return ClientDataConformer(
            self._specs, self._config, default=default
        ).data

    def to_dataframe(self):
        return aspect_to_dataframe(self)

    @property
    def config(self):
        return deepcopy(self._config)
# ------------------------------------------------------------------------------

def main():
    pass
# ------------------------------------------------------------------------------

__all__ = ['Aspect']

if __name__ == '__main__':
    help(main)
