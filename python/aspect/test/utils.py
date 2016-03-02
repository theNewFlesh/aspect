from aspect.core.aspect import Aspect
aspect = Aspect()
aspect.levels = ['public']
aspect.json_response = True
# ------------------------------------------------------------------------------

def get_specs(id_=0, module=1):
	c = 'Test' + str(module)
	m = 'method' + str(module)
	f = 'module_func' + str(module)
	specs = {
		'create1': {
			'create': {
				c: {
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
				c: None
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

		'delete1': {
			'delete': {
				id_: None
			}
		},

		'execute1': {
			'execute': {
				id_: {
					m: {
						'args': [1],
						'kwargs': {}
					}
				}
			}
		},

		'execute2': {
			'execute': {
				c: {
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
		'execute5': {
			'execute': {
				f: {
					'args': [1,2],
					'kwargs': {'kiwi': 2}
				}
			}
		}
	}
	return specs
# ------------------------------------------------------------------------------

def main():
	'''
	Run help if called directly
	'''
	
	import __main__
	help(__main__)
# ------------------------------------------------------------------------------

__all__ = [
	'get_specs',
	'aspect'
]

if __name__ == '__main__':
	main()