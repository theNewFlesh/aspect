import os
from pprint import pprint
from flask import Flask, render_template, request, make_response, jsonify
from flask_bootstrap import Bootstrap
import jinja2
import yaml
from aspect.core.utils import module_relative_path as modpath
# --------------------------------------------------------------------------------

# DATA_FILE = modpath(__file__, 'static/test-data.yml')
DATA_FILE = '/Users/alex/Desktop/new-data.yml'

def setup(data_file):
    env = jinja2.Environment(
            keep_trailing_newline=True,
            loader=jinja2.FileSystemLoader(modpath(__file__, 'templates'))
    )

    with open(data_file) as f:
        data = yaml.load(f)

    with open(modpath(__file__, 'static/css/style.css'), 'w') as f:
        css = env.get_template('css/style.css.j2').render(data)
        f.write(css)

    return data

data = setup(DATA_FILE)

app = Flask('test',
    static_folder=modpath(__file__, 'static'),
    template_folder=modpath(__file__, 'templates')
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
