# app.py -- routes for the app
import json
import logging
from hmac import new as hmac_new
from datetime import datetime

from flask import request, make_response

from api import app
from api.exceptions import PayloadException, WorkerException
from api.worker import Worker
from api.secrets import TOKENS


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


def queue(payload, branch_name):
    '''
    Drop new work into the queue to prepare builds.

    Arguments:
        - payload (dict):      -> POST request information received from GitHub
        - branch_name (string) -> Name of the branch that was POSTed to
    '''
    # Check that the push event matches the condition for new builds
    ref = payload.get('ref')

    # Parse
    if ref:
        # For docs on the GitHub PushEvent payload, see
        # https://developer.github.com/v3/activity/events/types/#pushevent
        branch = ref.split('/')[-1]
        repo = payload.get('repository')

        if branch == branch_name and repo:
            # This branch is approved for builds, so queue up work
            queue = Queue()
            queue.add(payload)

            status_code = 202
            resp['status'] = 'Build started for branch %s of repo %s' % branch, repo

        else:
            # Branch not approved; nothing to do
            status_code = 402
            resp['status'] = 'Skipping build for unregistered branch "{branch}"'.format(branch=branch)
    else:
        status = 'Could not find required attribute `ref` in the request payload'
        resp, status_code = {'status': status}, 400

    # Return response
    return prep_response(request, resp, status_code)


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
        for token in TOKENS:
            token_sig = hmac_new(token)
            if 'sha1=' + token_sig.hexdigest() == post_sig:
                # Payload is good; queue up work
                payload = request.get_json()
                return queue(payload, branch_name)

        # None of the tokens matched
        status = 'Request signature failed to authenticate'
        resp, status_code = {'status': status}, 401

    else:
        status = 'Authentication signature not found'
        resp, status_code = {'status': status}, 400

    # Return response
    return prep_response(request, resp, status_code)
