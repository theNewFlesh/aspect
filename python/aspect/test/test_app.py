from __future__ import print_function
import os
from pprint import pprint

from flask import Flask, render_template, request, make_response, jsonify
from flask_bootstrap import Bootstrap
import jinja2
import yaml

from aspect.core.utils import module_relative_path as modpath
from aspect.core.server import Aspect
ASPECT = Aspect(
    config=modpath(__file__, 'test-config.yml')
)
# --------------------------------------------------------------------------------

# def render_css():
#     env = jinja2.Environment(
#             keep_trailing_newline=True,
#             loader=jinja2.FileSystemLoader(modpath(__file__, 'templates'))
#     )

#     with open(modpath(__file__, 'static/css/style.css'), 'w') as f:
#         css = env.get_template('css/style.css.j2').render(ASPECT.to_client_data())
#         f.write(css)

# render_css(ASPECT)

app = Flask('test',
    static_folder=modpath(__file__, '../client/static'),
    template_folder=modpath(__file__, '../client/templates')
)

@app.route('/')
def index():
    data = ASPECT.to_client_data()
    render_template('css/style.css.j2', **data)
    return render_template('html/index.html.j2', **data)

@app.route('/api', methods=['POST'])
def api():
    data = request.get_json()
    # data = ASPECT.request(data, json_errors=True)
    data = ASPECT.request(data, json_errors=False)
    response = jsonify(
        body=data,
        status=200,
        mimetype='application/json'
    )

    # print(ASPECT.to_dataframe())
    return response

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=False)
