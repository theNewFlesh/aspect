import os
import jinja2
from jinja2 import Environment, FileSystemLoader
# ------------------------------------------------------------------------------

def is_list(item):
    return isinstance(item, list)

def library_to_list(library):
    def _recurse(items, parent='', store=[]):
        if isinstance(items, str):
            return parent[:-1]

        if isinstance(items, list):
            for item in items:
                store.append( _recurse(item, parent, store) )

        elif isinstance(items, dict):
            parent += items['name'] + '.'
            for key, val in items.items():
                store.append( _recurse(val, parent, store) )

    output = []
    _recurse([library], store=output)
    output = filter(lambda x: x is not None, set(output))
    output = sorted(list(output))
    return output

def module_relative_path(path):
    root = os.path.dirname(os.path.abspath(__file__))
    new_path = []
    for dir_ in path.split(os.sep):
        if dir_ == '..':
            root = os.path.dirname(root)
        elif dir_ == '.':
            pass
        else:
            new_path.append(dir_)
    new_path = os.path.join(root, *new_path)
    return os.path.abspath(new_path)

def render(template_path, data, extensions, strict=False):
    dirpath = os.path.dirname(template_path)

    env = Environment(
        loader=FileSystemLoader(dirpath),
        extensions=extensions,
        keep_trailing_newline=True
    )
    if strict:
        from jinja2 import StrictUndefined
        env.undefined = StrictUndefined

    # Add environ global
    env.globals['environ'] = os.environ.get

    template = os.path.basename(template_path)
    output = env.get_template(template).render(data)
    return output.encode('utf-8')
# ------------------------------------------------------------------------------

def main():
    pass
# ------------------------------------------------------------------------------

__all__ = [
    'is_list',
    'library_to_list',
    'render',
    'module_relative_path'
]

if __name__ == '__main__':
    help(main)
