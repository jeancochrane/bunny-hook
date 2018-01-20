from unittest import TestCase

import env
from api.worker import Worker
from decorators import mock_scripts


class TestIntegration(TestCase):
    '''
    Integration tests.
    '''
    def setUp(self):
        repo_name = 'bunny-hook'
        origin = 'https://github.com/jeancochrane/bunny-hook.git'

        self.worker = Worker(repo_name, origin)

    @mock_scripts
    def test_deploy(self):
        '''
        Using this repo as an example, actually run the `deploy` code.

        Mock out Worker.run_scripts, so that we don't run any actual deploy scripts.
        '''
        self.worker.deploy()

        # Assert build scripts got called

        # Assert deploy scripts got called

        # Assert tmp repo is moved

        # Assert repo exists in build location

        # Remove new repo
