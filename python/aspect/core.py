import re
from itertools import *
from inspect import *
from pprint import pprint, pformat
from utils import *
from random import randint
from warnings import warn
# ------------------------------------------------------------------------------

class Aspect(dict):
    def __init__(self, levels=['public', 'semiprivate', 'private', 'builtin']):
        self.levels    = levels
        self.specs     = Item(classes={}, functions={})
        self.library   = Item(classes={}, functions={})
        self.instances = {}
        
    def __repr__(self):
        return '\n\n'.join([
            pformat(self.levels),
            pformat(self.specs),
            pformat(self.library),
            pformat(self.instances)
        ])
    # --------------------------------------------------------------------------

    def request(self, spec):
        for action, spec_ in spec.iteritems():
            if action == 'create':
                yield self.create(spec_)
            elif action == 'read':
                yield self.read(spec_)
            elif action == 'update':
                yield self.update(spec_)
            elif action == 'delete':
                yield self.delete(spec_)
            elif action == 'execute':
                yield self.execute(spec_)
            else:
                warn(action + ' is not a valid action')

    def create(self, spec):
        class_, spec = spec.iteritems().next()

        if spec == None:
            spec = self.specs.classes[class_]

        init = spec['methods']['__init__']
        instance = self.library.classes[class_]
        # id_ = str(randint(0, 1000000000)).zfill(10)
        id_ = randint(0, 1000000000)
        self.instances[id_] = fire(instance, init)

        response = {
            'create': {
                class_: id_
            }
        }
        return response

    def read(self, spec):
        id_, spec = spec.iteritems().next()

        if isinstance(id_, str): #class
            item = self.library.classes[id_]
        else: #instance
            item = self.instances[id_]

        attr, _ = spec.iteritems().next()
        value = getattr(item, attr)

        response = {
            'read': {
                id_: {
                    attr: value
                }
            }
        }
        return response

    def update(self, spec):
        id_, spec = spec.iteritems().next()

        instance = self.instances[id_]
        attr, value = spec.iteritems().next()
        setattr(instance, attr, value)

        response = {
            'update': {
                id_: {
                    attr: value
                }
            }
        }
        return response

    def delete(self, spec):
        id_, _ = spec.iteritems().next()

        del self.instances[id_]

        response = {
            'delete': {
                id_: True
            }
        }
        return response

    def execute(self, spec):
        id_, spec = spec.iteritems().next()

        func = None
        method = None

        # instance method
        if isinstance(id_, int):
            instance = self.instances[id_]

            func, spec = spec.iteritems().next()
            method = func

            if spec == None:
                class_ = instance.__class__.__name__
                spec = self.specs.classes[class_]['methods'][func]
            
            func = getattr(instance, func)
            
        else:
            # class method
            if self.library.classes.has_key(id_):
                class_ = self.library.classes[id_]

                func, spec = spec.iteritems().next()
                method = func
                func = getattr(class_, func)
                if spec == None:
                    spec = self.specs.classes[id_]

            # module function
            elif self.library.functions.has_key(id_):
                func = self.library.functions[id_]
                if spec == None:
                    spec = self.specs.functions[id_]

        output = fire(func, spec)

        if method:
            output = {method: output}
        response = {
            'execute': {
                id_: output
            }
        }
        return response
    # --------------------------------------------------------------------------

    def register(self, item):
        item_type = get_item_type(item)
        
        if item_type in ['class', 'instance']:
            spec = class_to_aspect(item, levels=self.levels)
            self.specs.classes[item.__name__] = spec
            self.library.classes[item.__name__] = item

            return item 
        
        elif item_type in ['function', 'generator_function', 'method']:        
            spec = function_to_aspect(item)
            self.specs.functions[item.__name__] = spec
            self.library.functions[item.__name__] = item
            
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
# ------------------------------------------------------------------------------

def main():
    '''
    Run help if called directly
    '''
    
    import __main__
    help(__main__)
# ------------------------------------------------------------------------------

__all__ = ['Aspect']

if __name__ == '__main__':
    main()