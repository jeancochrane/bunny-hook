# queue.py -- run tasks from a queue


class Queue(object):
    # Hard-coded connection string? Or read config file?

    def add(self, repo_name, origin):
        # Name of the repo
        self.repo_name = repo_name

        # Git origin
        self.origin = origin

    def pop(self):
        # Take the most recent job off the queue

    def run(self):
        while True:
            work = self.pop()
            if work:
                # run work

def run_queue():
    '''
    Infinite loop to check for work and pull it off the queue.
    '''
    while True:
         

if __name__ == '__main__':

    queue = Queue()
    queue.run()

