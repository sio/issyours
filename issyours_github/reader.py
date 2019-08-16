'''
Read GitHub issues from JSON files on local filesystem
'''


from issyours.reader import ReaderBase

class GitHubReader(ReaderBase):
    def __init__(self):
        super().__init__()

    def _read_issue(self, uid):
        return Dummy(uid)

    def issue_uids(self, sort_by='created', desc=True):
        yield from range(1,10)


class Dummy:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)
    def __repr__(self):
        return repr(self.value)
