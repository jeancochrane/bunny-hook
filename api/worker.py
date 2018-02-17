# worker.py -- runs work (build scripts)
import os
import subprocess

import yaml

from api.exceptions import WorkerException
from api.payload import Payload


class Worker(object):
    '''
    Perform a build based on a GitHub API payload.
    '''
    def __init__(self, payload):
        '''
        Initialize the Worker with attributes from the payload that are
        necessary for cloning the repo.
        '''
        self.payload = Payload(payload)

        self.repo_name = self.payload.get_name()
        self.origin = self.payload.get_origin()
        self.branch = self.payload.get_branch()

    def run_command(self, cmd):
        '''
        Helper method that wraps `subprocess.run` to run commands and fail noisily.
        '''
        try:
            return subprocess.run(cmd, check=True, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            raise WorkerException(str(e))

    def run_script(self, script_path):
        '''
        Run a shell script from a file.

        This should probably have some more sophisticated permissioning (e.g.
        chrooting) before going live.
        '''
        # Make script executable -- Python chmod docs:
        # https://docs.python.org/3/library/stat.html#stat.S_IXOTH
        os.chmod(script_path, 0o775)

        return self.run_command(['bash', script_path])

    def deploy(self, tmp_path=None):
        '''
        Run build and deployment based on the config file.
        '''
        print('Deploying %s' % self.repo_name)

        # Check if git repo exists -- if not, make it
        if no_repo:
            if not tmp_path:
                # Repo should have been cloned to /tmp/<repo-name>
                tmp_path = os.path.abspath(os.path.join(os.sep, 'tmp', self.repo_name))

            print('Cloning {origin} into {tmp_path}...'.format(origin=self.origin,
                                                            tmp_path=tmp_path))
            self.run_command(['git', 'clone', '--depth=1', self.origin, tmp_path])
            self.run_command(['git', 'checkout', self.branch])
        else:
            self.run_command(['git', 'fetch', '--all'])
            self.run_command(['git', 'checkout', self.branch])
            self.run_command(['git', 'reset', '--hard', 'origin/{}'.format(self.branch)])

        # Check for a yaml file
        yml_file = os.path.join(tmp_path, 'deploy.yml')
        yaml_file = os.path.join(tmp_path, 'deploy.yaml')

        if not (os.path.isfile(yml_file) or os.path.isfile(yaml_file)):
            raise WorkerException('Could not locate a `deploy.yml` file in your repo.')

        if os.path.isfile(yml_file) and os.path.isfile(yaml_file):
            raise WorkerException('Found two config files in this repo! Delete one and try again.')

        if os.path.isfile(yml_file):
            config_file = yml_file
        else:
            config_file = yaml_file

        # Parse the config file
        print('Loading config file from %s...' % config_file)
        with open(config_file) as cf:
            config = yaml.load(cf)

        if not config:
            raise WorkerException('Deployment file %s appears to be empty' % config_file)

        clone_path = config.get('clone')
        build_scripts = config.get('build', [])
        deploy_scripts = config.get('deploy', [])

        # Enforce required directives
        if not clone_path:
            raise WorkerException('Deployment file %s is missing `clone` directive' % config_file)

        # Run build scripts, if they exist
        for script in build_scripts:
            script_path = os.path.join(clone_path, script)
            print('Running build script %s...' % script_path)
            self.run_script(script_path)

        # Move repo from tmp to the clone path
        print('Moving repo from {tmp_path} to {clone_path}...'.format(tmp_path=tmp_path,
                                                                      clone_path=clone_path))
        self.run_command(['rsync', 'avz', 'delete', tmp_path, clone_path])

        # Run deploy scripts, if they exist
        for script in deploy_scripts:
            script_path = os.path.join(clone_path, script)
            print('Running deployment script %s...' % script_path)
            self.run_script(script_path)

        print('Finished deploying %s!' % self.repo_name)

        return True
