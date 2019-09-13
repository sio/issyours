'''
Pelican plugin for rendering issues archive on static website
'''


from pelican import signals
from pelican.generators import Generator



class IssueGenerator(Generator):
    '''
    Obtain issue information from storage and create nice pages for each issue
    '''


    def generate_context(self):  # TODO
        self.rewrite_rules = self.settings['ISSYOURS_REWRITE_URLS']

        self.issue_readers = {}
        for cls, kwargs in self.settings['ISSYOURS_SOURCES'].items():
            issue_reader = cls(**kwargs.get('init', {}))
            prefix = kwargs.get('prefix', '')
            self.issue_readers[prefix] = issue_reader


    def generate_output(self, writer):  # TODO
        for prefix, reader in self.issue_readers.items():
            for issue in reader.issues():
                print('{prefix}-{uid}: {title}'.format(
                    prefix=prefix,
                    uid=issue.uid,
                    title=issue.title,
                ))


def get_generators(pelican_object):
    return IssueGenerator


def register():
    signals.get_generators.connect(get_generators)
