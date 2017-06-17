from schematics.models import Model, BaseType
from schematics.types import StringType, IntType, BooleanType, URLType
from schematics.types.compound import ListType, DictType
from schematics.exceptions import ValidationError
# ------------------------------------------------------------------------------

def is_action(item):
    if item not in ['create', 'read', 'update', 'delete', 'execute']:
        raise ValidationError(item + ' is not a valid action')
    return item

def is_id(item):
    if len(str(item)) != 10:
        raise ValidationError(str(item) + ' is not a valid id')
    return item

# def id_exists(item):
#   pass

# def is_module(item):
#   pass

# def is_class(item):
#   pass

# def is_method(item):
#   pass

# def is_attribute(item):
#   pass

# def is_function(item):
#   pass
# ------------------------------------------------------------------------------

class BaseSpec(Model):
    action = StringType(required=True, validators=[is_action])
    fullname = StringType(default='')
    module = StringType(required=True)
    class_ = StringType(required=True)

class CreateSpec(BaseSpec):
    args = ListType(BaseType, default=[])
    kwargs = DictType(BaseType, default={})

class ReadSpec(BaseSpec):
    id_ = IntType(required=True, validators=[is_id])
    attribute = StringType(required=True)

class UpdateSpec(BaseSpec):
    id_ = IntType(required=True, validators=[is_id])
    attribute = StringType(required=True)
    value = BaseType(required=True)

class DeleteSpec(BaseSpec):
    id_ = IntType(required=True, validators=[is_id])

class FunctionSpec(BaseSpec):
    function = StringType(required=True)
    args = ListType(BaseType, default=[])
    kwargs = DictType(BaseType, default={})

class MethodSpec(BaseSpec):
    id_ = IntType(required=True, validators=[is_id])
    method = StringType(required=True)
    args = ListType(BaseType, default=[])
    kwargs = DictType(BaseType, default={})
# ------------------------------------------------------------------------------

class LibraryItem(Model):
    fullname=StringType(required=True)
    # name=StringType(default=None)
    # module=StringType(default=None)
    # class_=StringType(default=None)
    default_args=DictType(BaseType, default={})
    default_kwargs=DictType(BaseType, default={})
    default_value=ListType(BaseType, default=[])
    blacklist=BooleanType(required=True, default=False)

class DashboardType(BaseType):
    title=StringType(default='card-0')
    html=StringType(default='<div></div>')
    flex_grow=IntType(default=1)
    flex_shrink=IntType(default=0)
    width=StringType(default='250px')
    height=StringType(default='250px')
    id=StringType(default='0')

class Config(Model):
    api_url=URLType(default='http://localhost:5000/api')
    title=StringType(default='aspect')
    dashboard=ListType(DashboardType, default=[])
    library=DictType(BaseType, default={})
# ------------------------------------------------------------------------------

def main():
    '''
    Run help if called directly
    '''

    import __main__
    help(__main__)
# ------------------------------------------------------------------------------

__all__ = [
    'CreateSpec',
    'ReadSpec',
    'UpdateSpec',
    'DeleteSpec',
    'FunctionSpec',
    'MethodSpec',
    'LibraryItem',
    'Config'
]

if __name__ == '__main__':
    main()



