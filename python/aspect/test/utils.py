import pandas as pd
from pandas import DataFrame

pd.options.display.width = 1000
# ------------------------------------------------------------------------------

def aspect_to_dataframe(aspect):
    def add_instance(item, id_, instance):
        item[id_] = instance
        return item
    
    data = DataFrame(aspect._specs)
    data['instances'] = None
    data.instances = data.instances.apply(lambda x: {})

    cols = ['name', 'module', 'class_', 'kind',  'level', 'args', 'kwargs', 'varargs', 'varkwargs', 'object', 'instances']
    data = data[cols]

    for id_, item in aspect._library.iteritems():
        row = data[
            (data.module == item['module']) &
            (data.class_ == item['class_']) &
            (data.name == '__init__')
        ]
        data.loc[row.index, 'instances'] = data.loc[row.index, 'instances'].apply(lambda x: add_instance(x, id_, item['instance']))
        
    return data
# ------------------------------------------------------------------------------

def main():
    help(__main__)
# ------------------------------------------------------------------------------

__all__ = [
    'aspect_to_dataframe'
]

if __name__ == '__main__':
    main()