import re
from itertools import *
from inspect import *
from pprint import pprint, pformat
from utils import *
from random import randint
from warnings import warn
from functools import wraps
# ------------------------------------------------------------------------------

class Aspect(object):
	def __init__(self, levels=['public', 'semiprivate', 'private', 'builtin'], json_response=True):
		self._response  = json_response
		self._levels    = levels
		self._specs     = Item(classes={}, functions={})
		self._library   = Item(classes={}, functions={})
		self._instances = {}
		
	def __repr__(self):
		return '\n\n'.join([
			pformat({'json_response': self._response}),
			pformat({'levels': self._levels}),
			pformat(self._specs),
			pformat(self._library),
			pformat(self._instances)
		])
	# --------------------------------------------------------------------------

	def request(self, spec):
		for action, spec_ in spec.iteritems():
			if action == 'create':
				yield self._create(spec_)
			elif action == 'read':
				yield self._read(spec_)
			elif action == 'update':
				yield self._update(spec_)
			elif action == 'delete':
				yield self._delete(spec_)
			elif action == 'execute':
				yield self._execute(spec_)
			else:
				warn(action + ' is not a valid action')

	def _create(self, spec):
		class_, spec = spec.iteritems().next()

		if spec == None:
			spec = self._specs.classes[class_]

		init = spec['methods']['__init__']
		instance = self._library.classes[class_]
		# id_ = str(randint(0, 1000000000)).zfill(10)
		id_ = randint(0, 1000000000)
		self._instances[id_] = fire(instance, init)

		response = id_
		if self._response:
			response = {
				'create': {
					class_: response
				}
			}
		return response

	def _read(self, spec):
		id_, spec = spec.iteritems().next()

		if isinstance(id_, str): #class
			item = self._library.classes[id_]
		else: #instance
			item = self._instances[id_]

		attr, _ = spec.iteritems().next()
		value = getattr(item, attr)

		response = value
		if self._response:
			response = {
				'read': {
					id_: {
						attr: response
					}
				}
			}
		return response

	def _update(self, spec):
		id_, spec = spec.iteritems().next()

		instance = self._instances[id_]
		attr, value = spec.iteritems().next()
		setattr(instance, attr, value)

		response = getattr(instance, attr) == value
		if self._response:
			response = {
				'update': {
					id_: {
						attr: response
					}
				}
			}
		return response

	def _delete(self, spec):
		id_, _ = spec.iteritems().next()

		del self._instances[id_]

		response = not self._instances.has_key(id_)
		if self._response:
			response = {
				'delete': {
					id_: response
				}
			}
		return response

	def _execute(self, spec):
		id_, spec = spec.iteritems().next()

		func = None
		method = None

		# instance method
		if isinstance(id_, int):
			instance = self._instances[id_]

			func, spec = spec.iteritems().next()
			method = func

			if spec == None:
				class_ = instance.__class__.__name__
				spec = self._specs.classes[class_]['methods'][func]
			
			func = getattr(instance, func)
			
		else:
			# class method
			if self._library.classes.has_key(id_):
				class_ = self._library.classes[id_]

				func, spec = spec.iteritems().next()
				method = func
				func = getattr(class_, func)
				if spec == None:
					spec = self._specs.classes[id_]

			# module function
			elif self._library.functions.has_key(id_):
				func = self._library.functions[id_]
				if spec == None:
					spec = self._specs.functions[id_]

		response = fire(func, spec)
		if self._response:
			if method:
				response = {method: response}
			response = {
				'execute': {
					id_: response
				}
			}
		return response
	# --------------------------------------------------------------------------

	def register(self, item):
		if is_visible(item.__name__, self._levels):
			item_type = get_object_type(item)
			if item_type in ['class', 'abstract']:
				spec = class_to_aspect(item, levels=self._levels)
				self._specs.classes[item.__name__] = spec
				self._library.classes[item.__name__] = item

				return item 
			
			elif item_type in ['function', 'generator_function', 'method']:
				spec = function_to_aspect(item)
				self._specs.functions[item.__name__] = spec
				self._library.functions[item.__name__] = item
				
				return item
				# @wraps(item)
				# def wrapper(*args, **kwargs):
				#     return func(*args, **kwargs)
				# return wrapper

	# def deregister(self, item):
	#     key = item.__name__
	#     for cls_ in self._specs.classes.values():
	#         if cls_['methods'].has_key(key):
	#             cls_['methods'].pop(meth)
	#     return item
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