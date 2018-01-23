# queue.py -- run tasks from a queue


def queue_method():
    '''
    Decorator that adds a `delay` function to a method of a class instance,
    allowing that method to be queued up instead of run synchronously.

    Major props to @evz for establishing this paradigm for functions.
    '''
    def delay(*args, **kwargs):
        pass

    f.delay = delay
    return f


def run_queue():
    '''
    Infinite loop to check for work and pull it off the queue.
    '''
    while True:
        pass

if __name__ == '__main__':

    run_queue()
