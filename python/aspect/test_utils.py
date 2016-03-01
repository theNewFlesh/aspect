class Test(object):
    width = 10
    def __init__(self):
        self.name = 'test_name'
    
    def height(self):
        return 10

    @property
    def age(self):
        return 10

    def do_something(self, a,b,c, kw1=1, kw2=4):
        return a,b,c, kw1, kw2

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
                    'name': None
                }
            }
        },

        'read2': {
            'read': {
                id_: {
                    'age': None
                }
            }
        },

        'read3': {
            'read': {
                id_: {
                    'width': None
                }
            }
        },

        'update': {
            'update': {
                id_: {
                    'name': 'namey-mcnamerton'
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
                    'do_something': {
                        'args': [1,2,3],
                        'kwargs': {'kw1': 2, 'kw2': 8}
                    }
                }
            }
        },

        'execute2': {
            'execute': {
                'Test': {
                    'some_func': {
                        'args': [1,2],
                        'kwargs': {'flags': 2, 'ignore': False}
                    }
                }
            }
        },

        'execute3': {
            'execute': {
                'module_func': {
                    'args': [1,2],
                    'kwargs': {'flags': 2, 'ignore': False}
                }
            }
        }
    }
    return specs