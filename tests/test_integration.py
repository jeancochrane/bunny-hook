from unittest import TestCase
import io
import os
import sys
import shutil

import env
from api.worker import Worker
from decorators import mock_scripts


class stdout(list):

    def __enter__(self):
        # Save initial value of sys.stdout
        self.stdout = sys.stdout

        # Point sys.stdout at an IO object on this class
        sys.stdout = self._stringio = io.StringIO()
        return self

    def __exit__(self, *args):
        # Save stdout to this object
        self.extend(self._stringio.getvalue().splitlines())

        # Reset sys.stdout
        sys.stdout = self.stdout


class TestIntegration(TestCase):
    '''
    Test integrations between different parts of the app.

    To run builds, this test suite uses a special repo, jeancochrane/bunny-test,
    that includes the bare minimum components that are necessary for running a
    build.
    '''
    def setUp(self):
        payload = {
            'ref': 'refs/head/master',
            'repository': {
                'name': 'bunny-test'
            },
            'clone_url': 'https://github.com/jeancochrane/bunny-test.git'
        }

        self.worker = Worker(payload)

    @mock_scripts
    def test_deploy(self):
        '''
        Using this repo as an example, actually run the `deploy` code.

        Mock out Worker.run_scripts, so that we don't run any actual deploy scripts.
        '''
        # Clone the repo as a subdirectory in the tests repo, so that we can
        # clean it up easily
        with stdout() as output:
            self.worker.deploy(tmp_path='./bunny-test')

        # Assert repo exists in build location
        self.assertTrue(os.path.exists('bunny-test'))

        # Remove new repo
        shutil.rmtree('bunny-test')
