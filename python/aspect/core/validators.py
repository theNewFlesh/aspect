from schematics.models import Model, BaseType
from schematics.types import StringType, IntType
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
# 	pass

# def is_module(item):
# 	pass

# def is_class(item):
# 	pass

# def is_method(item):
# 	pass

# def is_attribute(item):
# 	pass

# def is_function(item):
# 	pass
# ------------------------------------------------------------------------------

class BaseSpec(Model):
	action = StringType(required=True, validators=[is_action])
	
class CreateSpec(BaseSpec):
	module = StringType(required=True)
	class_ = StringType(required=True)
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
	module = StringType(required=True)
	function = StringType(required=True)
	args = ListType(BaseType, default=[])
	kwargs = DictType(BaseType, default={})
	
class MethodSpec(BaseSpec):
	id_ = IntType(required=True, validators=[is_id])
	method = StringType(required=True)
	args = ListType(BaseType, default=[])
	kwargs = DictType(BaseType, default={})
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
	'MethodSpec'
]

if __name__ == '__main__':
	main()



