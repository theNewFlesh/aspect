import os
from pprint import pprint
import json
from flask import Flask, render_template, request, make_response, jsonify
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
        is_list=is_list
    )

@app.route('/')
def index():
    return render_template('html/index.html.j2', **data)

@app.route('/api', methods=['POST'])
def api():
    data = request.get_json()
    print
    pprint(data)
    print

    response = jsonify(
        body=data,
        status=200,
        mimetype='application/json'
    )
    return response

if __name__ == '__main__':
    app.run(debug=True)
