from unittest import TestCase
import json
import sys

from werkzeug.datastructures import Headers

import env
import test_secrets
sys.modules['api.secrets'] = test_secrets
import api
from api.routes import get_hmac


class TestAPI(TestCase):

    @classmethod
    def setUpClass(cls):
        '''
        Set up some class-wide attributes for testing.
        '''
        api.app.testing = True
        cls.app = api.app.test_client()
        cls.tokens = test_secrets.TOKENS

        # Good and bad authentication credentials
        cls.good_sig = get_hmac(cls.tokens['master'])
        cls.bad_sig = get_hmac('bogus token')

        cls.good_data = json.dumps({
                'ref': 'refs/head/master',
                'repository': {
                    'name': 'test-repo'
                }
            })

    def test_successful_request(self):
        '''
        Test a successful request.
        '''
        headers = Headers()
        headers.add('X-Hub-Signature', self.good_sig)

        post_request = self.app.post('/hooks/github/master',
                                     content_type='application/json',
                                     data=self.good_data,
                                     headers=headers)

        self.assertEqual(post_request.status_code, 202)

        response = json.loads(post_request.data.decode('utf-8'))
        expected = 'Build started for ref refs/head/master of repo test-repo'
        self.assertEqual(response.get('status'), expected)

    def test_authentication_failed(self):
        '''
        Test a bad request where the secret token doesn't authenticate.
        '''
        headers = Headers()
        headers.add('X-Hub-Signature', self.bad_sig)


        post_request = self.app.post('/hooks/github/master',
                                     content_type='application/json',
                                     data=self.good_data,
                                     headers=headers)

        self.assertEqual(post_request.status_code, 403)

        response = json.loads(post_request.data.decode('utf-8'))
        expected = 'Request signature failed to authenticate'
        self.assertEqual(response.get('status'), expected)

    def test_incorrect_branch_name(self):
        '''
        When the ref path from GitHub is different from the hook branch name,
        make sure that the app does nothing.
        '''
        headers = Headers()
        headers.add('X-Hub-Signature', self.good_sig)

        post_request = self.app.post('/hooks/github/deploy',
                                     content_type='application/json',
                                     data=self.good_data,
                                     headers=headers)

        self.assertEqual(post_request.status_code, 403)

        response = json.loads(post_request.data.decode('utf-8'))
        msg = 'No token configured for deploy'
        self.assertEqual(response.get('status'), msg)

    def test_no_ref(self):
        '''
        Test a bad request (does not contain the `ref` attribute).
        '''
        post_data = json.dumps({'test': 'test'})

        headers = Headers()
        headers.add('X-Hub-Signature', self.good_sig)

        post_request = self.app.post('/hooks/github/master',
                                     content_type='application/json',
                                     data=post_data,
                                     headers=headers)

        self.assertEqual(post_request.status_code, 400)

        response = json.loads(post_request.data.decode('utf-8'))
        expected = "Malformed request payload: {'test': 'test'}"
        self.assertEqual(response.get('status'), expected)
