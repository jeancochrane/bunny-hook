# queue.py -- run tasks from a queue
from api.worker import Worker


class Queue(object):
    # Hard-coded connection string? Or read from config file?

    def add(self, payload):
        # Package up the payload and drop it into the queue
        pass

    def pop(self):
        # Take the most recent job off the queue
        pass

    def run(self):
        while True:
            work = self.pop()
            if work:
                worker = Worker()
                worker.deploy(work)
