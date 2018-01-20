import os
from unittest import TestCase, main
from unittest.mock import Mock, create_autospec
from subprocess import CompletedProcess

import env
from api.worker import Worker
from api.exceptions import WorkerException


def mock_subprocess(func):
    '''
    Decorator for mocking worker methods that run subprocesses.
    '''
    def new_test(self, *args, **kwargs):
        return_value = CompletedProcess([], returncode=0)

        self.worker.run_command = create_autospec(self.worker.run_command,
                                                return_value=return_value)

        self.worker.run_script = create_autospec(self.worker.run_script,
                                                return_value=return_value)
        func(self, *args, **kwargs)

    return new_test


class TestWorker(TestCase):

    def setUp(self):
        # Use this repo for the integration test
        repo_name = 'bunny-hook'
        origin = 'https://github.com/jeancochrane/bunny-hook.git'

        self.worker = Worker(repo_name, origin)

    def test_run_command_succeeds(self):
        cmd = self.worker.run_command(['echo', '"Run command succeeded!"'])
        self.assertEqual(cmd.returncode, 0)

    def test_run_command_errors(self):
        with self.assertRaises(WorkerException) as e:
            self.worker.run_command(['bash', 'exit', '1'])

    def test_run_script(self):
        cmd = self.worker.run_script(os.path.join(os.getcwd(), 'tests', 'scripts', 'pass.sh'))
        self.assertEqual(cmd.returncode, 0)

    def test_run_script_errors(self):
        with self.assertRaises(WorkerException) as e:
            self.worker.run_script(os.path.join(os.getcwd(), 'tests', 'scripts', 'fail.sh'))

    @mock_subprocess
    def test_deploy_without_commands(self):
        '''
        Mock out all subprocess calls and test that the rest of the `deploy`
        command runs.
        '''
        good_configs = os.path.join(os.getcwd(), 'tests', 'configs', 'good-configs')
        deployed = self.worker.deploy(tmp_path=good_configs)
        self.assertTrue(deployed)

    @mock_subprocess
    def test_empty_config_file(self):
        '''
        Test an error is raised when the config file is found, but empty.
        '''
        empty_config = os.path.join(os.getcwd(), 'tests', 'configs', 'empty-config')
        with self.assertRaises(WorkerException) as e:
            self.worker.deploy(tmp_path=empty_config)

        expected_msg = 'deploy.yml appears to be empty'
        self.assertIn(expected_msg, str(e.exception))

    @mock_subprocess
    def test_no_config_file(self):
        '''
        Test an error is raised when no config file is found.
        '''
        with self.assertRaises(WorkerException) as e:
            self.worker.deploy()

        expected_msg = 'Could not locate a `deploy.yml` file in your repo'
        self.assertIn(expected_msg, str(e.exception))

    @mock_subprocess
    def test_two_config_files(self):
        '''
        Test an error is raised when two config files are found.
        '''
        two_configs = os.path.join(os.getcwd(), 'tests', 'configs', 'two-configs')
        with self.assertRaises(WorkerException) as e:
            self.worker.deploy(tmp_path=two_configs)

        expected_msg = 'Found two config files in this repo! Delete one and try again'
        self.assertIn(expected_msg, str(e.exception))

    @mock_subprocess
    def test_no_clone_directive_in_config_file(self):
        '''
        Test that an error is raised when no clone directive is found in the
        config file.
        '''
        no_clone_config = os.path.join(os.getcwd(), 'tests', 'configs', 'no-clone')
        with self.assertRaises(WorkerException) as e:
            self.worker.deploy(tmp_path=no_clone_config)

        expected_msg = 'is missing `clone` directive'
        self.assertIn(expected_msg, str(e.exception))

    def test_deploy(self):
        '''
        Integration test! Use this repo to actually run the `deploy` code.
        '''
        self.fail()
