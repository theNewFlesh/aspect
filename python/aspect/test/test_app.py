from __future__ import print_function
from pprint import pprint

from aspect.test.tests import aspect
from aspect.core.utils import aspect_to_dataframe

from flask import Flask, request, Response, render_template, jsonify
app = Flask(__name__)
# ------------------------------------------------------------------------------

@app.route('/', methods=['POST'])
def index():
	'''
	flask index.html endpoint
	'''
	if request.method == 'POST':
		spec = request.get_json(silent=True)
		response = aspect.request(spec, json_errors=True)
		print(aspect_to_dataframe(aspect))
		print()
		# pprint(aspect._library)
		# print()

		return jsonify(response=response)
		# return render_template('index.html', response)
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run()
