# worker.py -- runs work (build scripts). Eventually, should run off of a Redis queue


class Worker(object):
    '''
    Class for handling all of the build stuff. Assume synchronous execution.
    '''
    def __init__(self, repo, origin):
        # Name of the repo
        self.repo = repo

        # Git origin
        self.origin = origin

    def clone(self, path):
        '''
        Clone the repo to a location.
        '''
        pass

    def parse(self):
        '''
        Parse a config file from the repo.
        '''
        # Parse YAML and save the config
        self.config = {'clone_path': ''}

    def build(self):
        '''
        Run build scripts.
        '''
        pass

    def deploy(self):
        '''
        Move files to the deployment location, and run deploy scripts.
        '''
        pass

    def run(self):
        '''
        Run the commands for the worker synchronously.
        '''
        self.clone('/tmp/' + self.repo)
        self.parse()

        self.clone(self.config['clone_path'])
        self.build()
        self.deploy()
