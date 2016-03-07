from __future__ import print_function
from aspect.test.tests import aspect
# ------------------------------------------------------------------------------

class Test2(object):
	'''Test class docstring'''
	class_attr = 99
	_class_attr = 100
	__class_attr = 101

	def __init__(self):
		self.instance_attr = 'a'
		self._instance_attr = 'b'
		self.__instance_attr = 'c'
	
	@property
	def property_(self):
		return 'the_value_of_property_'
	
	@property
	def _property(self):
		return self._instance_attr
	
	@property
	def __property(self):
		return self.__instance_attr
	
	@aspect.deregister
	def deregistered_method(self, arg):
		return 'deregistered method fired'
	
	def method1(self, arg):
		return 'method1 fired'

	def method2(self, arg1of2, arg2of2):
		return 'method2 fired'

	def method3(self, arg1of1, kwarg1of2=1, kwarg2of2=2):
		return 'method3 fired'

	def method4(self, arg1of2, arg2of2, kwarg1of2=1, kwarg2of2=2):
		return 'method4 fired'

	def method5(self, arg1of2, arg2of2, kwarg1of2=1, kwarg2of2=2, **kwargs):
		return 'method5 fired'
	
	def _method(self, kwarg1of1=1):
		return kwarg
	
	def __method(self, *args, **kwargs):
		return args, kwargs
# ------------------------------------------------------------------------------    

def module2_func1(arg1of2, arg2of2, **kwargs):
	'''module2_func1 docstring'''
	return arg1of2, arg2of2, kwargs

@aspect.deregister
def module2_deregistered_func2(arg1of2, arg2of2, kwarg1of1=3):
	'''module2_deregistered_func2 docstring'''
	return arg1of2, arg2of2, kwarg1of1

aspect.register(__name__)
# ------------------------------------------------------------------------------

def main():
	'''
	Run help if called directly
	'''
	import __main__
	help(__main__)
# ------------------------------------------------------------------------------

__all__ = ['Test2', 'module2_func1', 'module2_deregistered_func2']

if __name__ == '__main__':
	main()