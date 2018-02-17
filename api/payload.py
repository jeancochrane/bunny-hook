class Payload(object):
    '''
    Parse a payload from the GitHub API.
    '''
    def __init__(self, payload):
        self.dict = payload

    def validate(self, registered_branch):
        '''
        Check that the payload is well formed and corresponds to a registered
        branch.
        '''
        # Check that the push event matches the condition for new builds
        ref = self.get('ref')

        # Parse
        if ref:
            # For docs on the GitHub PushEvent payload, see
            # https://developer.github.com/v3/activity/events/types/#pushevent
            branch = ref.split('/')[-1]
            repo = self.get('repository')

            if branch == registered_branch and repo:
                return True

        return False

    def get(self, attr):
        '''
        Return a miscellaneous attribute from the payload, or None if no such
        attribute exists.
        '''
        return self.dict.get(attr)

    def get_branch(self):
        '''
        Return the name of the branch recorded in the payload.
        '''
        ref = self.get('ref')
        return ref.split('/')[-1]

    def get_origin(self):
        '''
        Return the URL that the repo can be cloned from.
        '''
        return self.get('clone_url')

    def get_name(self):
        '''
        Return the name of the repo recorded in the payload.
        '''
        repository = self.get('repository')
        return repository.get('name')

    @property
    def as_dict(self):
        '''
        Return the payload as a dictionary.
        '''
        return self.dict
