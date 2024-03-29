from __future__ import with_statement, print_function
from nose import with_setup
from nose.tools import assert_raises

from aspect.core.server import Aspect
from aspect.core.utils import module_relative_path as modpath

from aspect.test.test_module_1 import Test1
from aspect.test.test_module_2 import Test2
from schematics.exceptions import ValidationError

from aspect.core.utils import module_relative_path as modpath
from aspect.test.test_app import ASPECT
# ------------------------------------------------------------------------------

def id_setup():
    id_ = 1111111111
    spec = dict(
        module='aspect.test.test_module_1',
        class_='Test1',
        instance=Test1()
    )
    ASPECT._library[id_] = spec

def id_teardown():
    id_ = 1111111111
    del ASPECT._library[id_]

def create_001_test():
    spec = dict(
        action='create',
        module='aspect.test.test_module_1',
        class_='Test1',
        args=['name'],
        kwargs=dict(kwarg1=10, kwarg2=11)
    )
    response = ASPECT.request(spec)
    assert(isinstance(response, int) and len(str(response)) == 10)

@with_setup(id_setup, id_teardown)
def read_001_test():
    spec = dict(
        action='read',
        id_=1111111111,
        attribute='property_'
    )
    response = ASPECT.request(spec)
    assert(response == 'the_value_of_property_')

@with_setup(id_setup, id_teardown)
def update_001_test():
    spec = dict(
        action='update',
        id_=1111111111,
        attribute='class_attr',
        value='new_value'
    )
    response = ASPECT.request(spec)
    assert(response == True)

@with_setup(id_setup)
def delete_001_test():
    spec = dict(
        action='delete',
        id_=1111111111
    )
    response = ASPECT.request(spec)
    assert(response == True)

@with_setup(id_setup, id_teardown)
def execute_method_001_test():
    spec = dict(
        action='execute',
        id_=1111111111,
        method='method1',
        args=[1],
        kwargs={}
    )
    response = ASPECT.request(spec)
    assert(response == 'method1 fired')

def execute_function_001_test():
    spec = dict(
        action='execute',
        module='aspect.test.test_module_1',
        function='module1_func1',
        args=[1,2],
        kwargs={}
    )
    response = ASPECT.request(spec)
    print(response)
    assert( response == (1,2,{}) )

def execute_deregistered_function_001_test():
    spec = dict(
        action='execute',
        module='aspect.test.test_module_1',
        function='module1_deregistered_func2',
        args=[1,2],
        kwargs={}
    )
    with assert_raises(ValidationError):
        ASPECT.request(spec, json_errors=False)
# ------------------------------------------------------------------------------

def main():
    help(__main__)
# ------------------------------------------------------------------------------

__all__ = [
    'id_setup',
    'id_teardown',
    'create_001_test',
    'read_001_test',
    'update_001_test',
    'delete_001_test',
    'execute_method_001_test',
    'execute_function_001_test',
    'execute_deregistered_function_001_test'
]

if __name__ == '__main__':
    main()
