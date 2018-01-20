class PayloadException(Exception):
    '''
    Something went wrong with the payload from the GitHub API.
    '''
    pass

class WorkerException(Exception):
    '''
    Something went wrong in the worker process.
    '''
    pass
