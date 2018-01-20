import os
from unittest import TestCase, main

import env
from api.worker import Worker
from api.exceptions import WorkerException
from decorators import mock_subprocess


class TestWorker(TestCase):

    def setUp(self):
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
        no_config = os.path.join(os.getcwd(), 'tests')
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
