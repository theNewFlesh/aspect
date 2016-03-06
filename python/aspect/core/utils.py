import re
from itertools import *
from inspect import *
from pprint import pformat
# ------------------------------------------------------------------------------

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

def main():
	'''
	Run help if called directly
	'''
	
	import __main__
	help(__main__)
# ------------------------------------------------------------------------------

# __all__ = [
# 	'Item',
# 	'get_object_type',
# 	'get_member_info',
# 	'is_visible',
# 	'fire',
# 	'function_to_aspect',
# 	'class_to_aspect'
# ]

if __name__ == '__main__':
	main()