import os
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import jinja2
import yaml
from utils import *

DATA_FILE = module_relative_path('static/test-data.yml')

def setup(data_file):
    env = jinja2.Environment(
            keep_trailing_newline=True,
            loader=jinja2.FileSystemLoader(module_relative_path('templates'))
    )

    with open(data_file) as f:
        data = yaml.load(f)

    with open(module_relative_path('static/css/style.css'), 'w') as f:
        css = env.get_template('css/style.css.j2').render(data)
        f.write(css)

    return data

data = setup(DATA_FILE)

app = Flask('test',
    static_folder=module_relative_path('static'),
    template_folder=module_relative_path('templates')
)

# bootstrap = Bootstrap(app)

@app.context_processor
def utility_processor():
    return dict(
        library_to_list=library_to_list,
        to_list=to_list
    )

@app.route('/')
def index():
    return render_template('html/index.html.j2', **data)

if __name__ == '__main__':
    app.run(debug=True)
