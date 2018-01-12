# app.py -- routes for the app

import json

from flask import request, make_response

from api import app

@app.route('/hooks/github/<branch_name>', methods=['POST'])
def parse(branch_name):

    # Initialize vars
    post = request.get_json()

    resp, status_code = {'status': 'ok'}, 200

    # Parse the request

    # Validate that the request came from GitHub

    # Kick off work
    print(branch_name)

    # Return response
    response = make_response(json.dumps(resp), status_code)
    response.headers['Content-Type'] = 'application/json'
    return response
