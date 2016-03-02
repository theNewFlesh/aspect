class Test(object):
	class_attr = 99
	_class_attr = 100
	__class_attr = 101

	def __init__(self):
		self.instance_attr = 'a'
		self._instance_attr = 'b'
		self.__instance_attr = 'c'
	
	@property
	def property_(self):
		return self.instance_attr
	
	@property
	def _property(self):
		return self._instance_attr
	
	@property
	def __property(self):
		return self.__instance_attr
	
	def deregistered_method(self, arg):
		return 'deregistered method fired'

	def method(self, arg):
		return arg
	
	def _method(self, kwarg=1):
		return kwarg
	
	def __method(self, *args, **kwargs):
		return args, kwargs

def get_specs(id_):
	specs = {
		'create1': {
			'create': {
				'Test': {
					'methods': {
						'__init__': {
							'args': [],
							'kwargs': {}
						}
					}
				}
			}
		},

		'create2': {
			'create': {
				'Test': None
			}
		},


		'read1': {
			'read': {
				id_: {
					'instance_attr': None
				}
			}
		},

		'read2': {
			'read': {
				id_: {
					'class_attr': None
				}
			}
		},

		'read3': {
			'read': {
				id_: {
					'_instance_attr': None
				}
			}
		},

		'update': {
			'update': {
				id_: {
					'instance_attr': 'new_value'
				}
			}
		},

		'delete': {
			'delete': {
				id_: None
			}
		},

		'execute1': {
			'execute': {
				id_: {
					'method': {
						'args': [1],
						'kwargs': {}
					}
				}
			}
		},

		'execute2': {
			'execute': {
				'Test': {
					'_method': {
						'args': [],
						'kwargs': {'kwarg': 2}
					}
				}
			}
		},

		'execute3': {
			'execute': {
				'__method': {
					'args': [1,2],
					'kwargs': {'flags': 2, 'ignore': False}
				}
			}
		},
		'execute4': {
			'execute': {
				id_: {
					'deregistered_method': {
						'args': [1],
						'kwargs': {}
					}
				}
			}
		},
	}
	return specs