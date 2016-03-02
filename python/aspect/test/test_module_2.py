from aspect.test.utils import aspect
# ------------------------------------------------------------------------------

@aspect.register
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
        return self.instance_attr
    
    @property
    def _property(self):
        return self._instance_attr
    
    @property
    def __property(self):
        return self.__instance_attr
    
    @aspect.deregister
    def deregistered_method(self, arg):
        return 'deregistered method fired'
    
    def method2(self, arg):
        return 'method2 fired'
    
    def _method(self, kwarg=1):
        return kwarg
    
    def __method(self, *args, **kwargs):
        return args, kwargs
# ------------------------------------------------------------------------------    

@aspect.register
def module_func2(apple, banana, kiwi=3):
    '''test docstring'''
    print(apple, banana, kiwi)
    print('it works')

aspect.deregister()
# ------------------------------------------------------------------------------

def main():
    '''
    Run help if called directly
    '''
    
    import __main__
    help(__main__)
# ------------------------------------------------------------------------------

__all__ = ['Test2', 'module_func2']

if __name__ == '__main__':
    main()