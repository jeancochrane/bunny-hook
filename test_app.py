from unittest import TestCase
import json

import api


class TestAPI(TestCase):

    @classmethod
    def setUpClass(cls):

        api.app.testing = True
        cls.app = api.app.test_client()

    def test_correct_branch_name(self):
        '''
        The ref path from GitHub should be the same as the branch name.
        '''
        post_data = json.dumps({'ref': 'refs/heads/master'})
        post_request = self.app.post('/hooks/github/master',
                                     content_type='application/json',
                                     data=post_data)

        self.assertEqual(post_request.status_code, 202)

        response = json.loads(post_request.data.decode('utf-8'))
        self.assertEqual(response.get('status'), 'Running build!')

    def test_incorrect_branch_name(self):
        '''
        When the ref path from GitHub is different from the hook branch name,
        make sure that the app does nothing.
        '''
        post_data = json.dumps({'ref': 'refs/heads/master'})
        post_request = self.app.post('/hooks/github/deploy',
                                     content_type='application/json',
                                     data=post_data)

        self.assertEqual(post_request.status_code, 402)

        response = json.loads(post_request.data.decode('utf-8'))
        msg = 'Incorrect branch "master" -- skipping build'
        self.assertEqual(response.get('status'), msg)

    def test_no_ref(self):
        '''
        Test a bad request (does not contain the `ref` attribute).
        '''
        post_data = json.dumps({'test': 'test'})

        with self.assertRaises(api.exceptions.PayloadException) as excpt:
            post_request = self.app.post('/hooks/github/deploy',
                                         content_type='application/json',
                                         data=post_data)

            self.assertTrue('Could not find payload variable `ref`' in excpt) 
