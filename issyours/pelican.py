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

        self.url_pattern = self.settings.get(
            'ISSYOURS_ISSUE_URL',
            'issue/{slug}.html'
        )
        self.dest_pattern = self.settings.get(
            'ISSYOURS_ISSUE_SAVE_AS',
            self.url_pattern if self.url_pattern.endswith('.html') else self.url_pattern + '/index.html'
        )
        self.issue_template = self.get_template('issue')


    def generate_output(self, writer):  # TODO
        for prefix, reader in self.issue_readers.items():
            for issue in reader.issues():
                dest = _format(self.dest_pattern, issue, prefix)
                url = _format(self.url_pattern, issue, prefix)
                writer.write_file(
                    name=dest,
                    template=self.issue_template,
                    context=dict(issue=issue),
                    relative_urls=self.settings['RELATIVE_URLS'],
                    url=url,
                )



def _format(pattern, issue, prefix=''):
    '''Format string based on issue fields'''
    return pattern.format(
        prefix=prefix,
        uid=issue.uid,
        slug=issue.uid,
    )


def get_generators(pelican_object):
    return IssueGenerator


def register():
    signals.get_generators.connect(get_generators)
