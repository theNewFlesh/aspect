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
	def __init__(self, levels=['public'], json_response=True):
		'''
		Args:
			levels opt(list):
				options include:
					'public'
					'semiprivate'
					'private'
					'builtin'
				default: ['public']
			
			json_response opt(bool):
				default: True
		'''
		self.json_response  = json_response
		self.levels         = levels
		self._specs         = Item(classes={}, functions={})
		self._library       = Item(classes={}, functions={})
		self._instances     = {}
		self._blacklist     = []
		
	def __repr__(self):
		return '\n\n'.join([
			pformat({'json_response': self.json_response}),
			pformat({'levels': self.levels}),
			pformat(self._specs),
			pformat(self._library),
			pformat(self._instances)
		])
	# --------------------------------------------------------------------------

	def request(self, specs):
		for action, spec in specs.iteritems():
			if action == 'create':
				yield self._create(spec)
			elif action == 'read':
				yield self._read(spec)
			elif action == 'update':
				yield self._update(spec)
			elif action == 'delete':
				yield self._delete(spec)
			elif action == 'execute':
				yield self._execute(spec)
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
		if self.json_response:
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
		if self.json_response:
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
		if self.json_response:
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
		if self.json_response:
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
		if self.json_response:
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
		if is_visible(item.__name__, self.levels):
			item_type = get_object_type(item)
			if item_type in ['class', 'abstract']:
				spec = class_to_aspect(item, levels=self.levels)
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

	def deregister(self, item=None):
		if item == None:
			for key in self._blacklist:
				for cls_ in self._specs.classes.values():
					if cls_['methods'].has_key(key):
						cls_['methods'].pop(key)
			return
		else:
			key = item.__name__
			self._blacklist.append(key)
			return item
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