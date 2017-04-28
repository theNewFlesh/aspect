import os
import jinja2
from jinja2 import Environment, FileSystemLoader
# ------------------------------------------------------------------------------

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

__all__ = ['render']

if __name__ == '__main__':
    help(main)
