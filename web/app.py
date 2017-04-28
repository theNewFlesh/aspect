import os
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import jinja2
import yaml

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

DATA_FILE = module_relative_path('static/data.yml')

def setup(data_file):
    env = jinja2.Environment(
            keep_trailing_newline=True,
            loader=jinja2.FileSystemLoader(module_relative_path('templates'))
    )

    with open(data_file) as f:
        data = yaml.load(f)

    with open(module_relative_path('static/css/style.css'), 'w') as f:
        css = env.get_template('style.css.j2').render(data)
        f.write(css)

    return data

data = setup(DATA_FILE)

app = Flask('test',
    static_folder=module_relative_path('static'),
    template_folder=module_relative_path('templates')
)
bootstrap = Bootstrap(app)

@app.route('/')
def index():
    return render_template('index.html.j2', **data)

if __name__ == '__main__':
    app.run(debug=True)
