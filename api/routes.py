# app.py -- routes for the app

import json

from flask import request, make_response

from api import app
from api.exceptions import PayloadException


@app.route('/hooks/github/<branch_name>', methods=['POST'])
def parse(branch_name):

    # Initialize vars
    post = request.get_json()

    resp, status_code = {'status': 'ok'}, 200

    # Parse the request
    ref = post.get('ref')

    # Parse
    if ref:
        # For docs on the GitHub PushEvent payload, see
        # https://developer.github.com/v3/activity/events/types/#pushevent
        branch = ref.split('/')[-1]

        if branch == branch_name:
            # Action will go here
            status_code = 202
            resp['status'] = 'Running build!'
        else:
            # Nothing to do
            status_code = 402
            resp['status'] = 'Incorrect branch "{branch}" -- skipping build'.format(branch=branch)
    else:
        raise PayloadException('Could not find payload variable `ref`', post)

    # Return response
    response = make_response(json.dumps(resp), status_code)
    response.headers['Content-Type'] = 'application/json'
    return response
