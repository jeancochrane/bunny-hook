# app.py -- routes for the app
import json
import logging
import hmac
from datetime import datetime

from flask import request, make_response, g

from api import app
from api.queue import Queue
from api.payload import Payload

try:
    from api.secrets import TOKENS
except ImportError:
    logging.error('Required secrets file not found. See api/secrets.example.py for setup information.')


def prep_response(request, resp, status_code):
    '''
    Utility function for logging and returning HTTP responses.

    Arguments:
        - request (Request) -> Flask Request object
        - resp (dict)       -> JSON to return
        - status_code (int) -> HTTP status code
    '''
    # Log data on this request/response cycle
    curr = str(datetime.now())
    metadata = '''
        Time: {curr}
        Response code: {status_code}
        Response body: {resp}
        Request headers: {headers}
        Request payload: {payload}
    '''.format(curr=curr,
               headers=request.headers,
               payload=request.get_json(),
               status_code=status_code,
               resp=resp)

    logging.debug(metadata)

    response = make_response(json.dumps(resp), status_code)
    response.headers['Content-Type'] = 'application/json'
    return response


def queue(payload_json, branch_name):
    '''
    Drop new work into the queue to prepare builds.

    Arguments:
        - payload_json (dict):      -> POST request information received from GitHub
        - branch_name (string) -> Name of the branch that was POSTed to
    '''
    payload = Payload(payload_json)

    if payload.validate(branch_name):
        # This branch is approved for builds, so queue up work
        queue = Queue()
        queue.add(payload_json)

        status_code = 202
        status = 'Build started for ref %s of repo %s' % (payload.get('ref'),
                                                          payload.get('repository')['name'])

    else:
        # Branch not approved; nothing to do
        status_code = 400

        if payload.get('ref'):
            status = 'Skipping build for unregistered branch "{ref}"'.format(ref=payload.get('ref'))
        else:
            status = 'Malformed request payload: {payload}'.format(payload=payload.as_dict)

    # Return response
    resp = {'status': status}
    return prep_response(request, resp, status_code)


def get_hmac(token):
    '''
    Check the HMAC hexadigest signature of a token (GitHub's way of creating
    hashes for authentication).

    Arguments:
        - token (str) -> Secret key to use for the hash.
    '''
    token_sig = hmac.new(token.encode('utf-8'), digestmod='sha1')
    return 'sha1=' + token_sig.hexdigest()


@app.route('/hooks/github/<branch_name>', methods=['POST'])
def receive_post(branch_name):
    '''
    Receive and respond to POST requests, either denying access or queuing
    new work in the process.

    Arguments:
        - branch_name (str) -> the branch that is being POSTed to (extracted
                               as a URL param by Flask)
    '''
    # Validate the request
    # Docs: https://developer.github.com/webhooks/securing/#validating-payloads-from-github
    post_sig = request.headers.get('X-Hub-Signature')

    if post_sig:
        try:
            if hmac.compare_digest(get_hmac(TOKENS[branch_name]), post_sig):
                # Payload is good; queue up work
                payload_json = request.get_json()
                return queue(payload_json, branch_name)
            else:
                # None of the tokens matched
                status = 'Request signature failed to authenticate'

        except KeyError:
            # TOKENS[branch_name] isn't set
            status = 'No token configured for ' + branch_name

    else:
        status = 'Authentication signature not found'

    # Return response
    resp = {'status': status}
    return prep_response(request, resp, 403)
