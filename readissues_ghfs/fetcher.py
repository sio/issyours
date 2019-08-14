'''
Create a backup of GitHub issues in JSON files on local filesystem
'''


from readissues_ghfs.api import GitHubAPI, GitHubTimestamp



class GitHubFetcher:
    '''
    Fetch GitHub issues data and store it on local filesystem
    '''

    ABOUT = 'GitHub Issues Archive made with <https://github.com/sio/readissues>'
    STAMP_FILE = 'fetcher.json'
    STAMP_VERSION = 1


    def __init__(self, repo, directory, token):
        self.repo = repo
        self.directory = directory
        self.api = GitHubAPI(token)


    def fetch(self):
        owner, project = self.repo.split('/')

        since = None  # TODO: read previous timestamp from directory
        for issue in self.api.issues(owner, project, since):
            self.save_issue(issue)
            comments_url = issue['comments_url']
            for comment in self.api.comments(url=comments_url, since=...):
                self.save_comment(comment)
            events_url = issue['events_url']
            for event in self.api.events(url=events_url, since=...):
                self.save_event(event)
            self.write_timestamp(issue)
        self.write_timestamp(global)


    def read_stamp(self, issue_no=None):
        '''Read timestamp files left from previous runs'''
        stamp_path = self._stamp_path(issue_no)
        if not os.path.exists(stamp_path):
            return None
        with open(stamp_path) as f:
            stamp = json.load(f)
        self._stamp_validate(stamp, issue_no)
        return datetime.utcfromtimestamp(stamp['timestamp'])


    def write_stamp(self, issue_no=None):
        '''Write signature file after successful completion of whole job or its atomic part'''
        stamp = dict(
            timestamp=int(datetime.utcnow().timestamp()),
            repo=self.repo,
            fetcher=self.__class__.__name__,
            about=self.ABOUT,
            stamp_version=self.STAMP_VERSION,
        )
        if issue_no:
            stamp['issue_no'] = issue_no
        write_json(stamp, self._stamp_path(issue_no))


    def _stamp_path(self, issue_no=None):
        '''Calculate path to stamp file'''
        elements = [self.directory, self.STAMP_FILE]
        if issue_no:
            elements.insert(1, issue_no)
        return os.path.join(*(str(e) for e in elements))


    def _stamp_validate(self, stamp, issue_no=None):
        '''Validate stamp file to avoid data corruption with overwriting'''
        validate = {
            'repo' = self.repo,
            'fetcher' = self.__class__.__name__,
            'stamp_version' = self.STAMP_VERSION,
        }
        if issue_no:
            validate['issue_no'] = issue_no
        for title, correct in validate.items():
            received = stamp[title]
            if correct != received:
                raise FetcherStampValidationError(title, correct, received)
        if 'timestamp' not in stamp:
            raise FetcherStampValidationError('timestamp', 'any value', 'nothing')



class FetcherStampValidationError(ValueError):
    '''
    Raised when stamp data does not match current fetcher object.
    This will help to avoid data corruption with accidental overwriting.
    '''

    template = ('data on disk does not come from this fetcher: '
                '{title!r} was expected to be {correct!r} '
                'but got {received!r} instead')

    def __init__(self, title, correct, received):
        message = self.template.format(**locals())
        super().__init__(message)



def write_json(dictionary, filename):
    '''Serialize a dictionary into a JSON file'''
    serialized = json.dumps(dictionary, indent=2, sort_keys=True)
    safe_write(filename, serialized)


def safe_write(filename, content):
    '''Safely (over)write a small file'''
    raise NotImplementedError
