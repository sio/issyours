'''
Pelican plugin for rendering issues archive on static website
'''


import logging
from pkg_resources import resource_string
from types import SimpleNamespace

from pelican import signals
from pelican.generators import Generator, PelicanTemplateNotFound

log = logging.getLogger(__name__)



class IssueGenerator(Generator):
    '''
    Obtain issue information from storage and create nice pages for each issue
    '''


    def get_template(self, name):
        try:
            return super().get_template(name)
        except PelicanTemplateNotFound:
            package = __name__.split('.')[0]
            code = resource_string(package, 'templates/{}.html'.format(name))
            if not code:
                raise e
            log.warning(
                ('Theme provides no template for {!r}, '
                 'falling back to a very basic one').format(name)
            )
            self._templates[name] = self.env.from_string(code.decode('utf-8'))
            return self._templates[name]


    def generate_context(self):  # TODO
        self.rewrite_rules = self.settings['ISSYOURS_REWRITE_URLS']

        self.issue_readers = {}
        for cls, kwargs in self.settings['ISSYOURS_SOURCES'].items():
            issue_reader = cls(**kwargs.get('init', {}))
            prefix = kwargs.get('prefix', '')
            self.issue_readers[prefix] = issue_reader

        pagination = self.settings['PAGINATED_TEMPLATES']
        if 'issues' not in pagination:
            pagination['issues'] = None  # Use default number of items per page

        self.url_pattern = self.settings.get(
            'ISSYOURS_ISSUE_URL',
            'issue/{slug}.html'
        )
        self.dest_pattern = self.settings.get(
            'ISSYOURS_ISSUE_SAVE_AS',
            self.url_pattern if self.url_pattern.endswith('.html') else self.url_pattern + '/index.html'
        )
        self.issue_template = self.get_template('issue')

        self.index_url = self.settings.get(
            'ISSYOURS_LIST_URL',
            'issues/index.html'
        )
        self.index_dest = self.settings.get(
            'ISSYOURS_LIST_SAVE_AS',
            self.index_url if self.index_url.endswith('.html') else self.index_url + '/index.html'
        )
        self.index_template = self.get_template('issues')


    def generate_output(self, writer):  # TODO
        for prefix, reader in self.issue_readers.items():
            def get_issue(uid):
                issue = reader.issue(uid)
                return IssueWrapper(
                    issue=issue,
                    prefix=prefix,
                    url_pattern=self.url_pattern,
                    dest_pattern=self.dest_pattern,
                )

            issue_uids = list(reader.issue_uids())
            writer.write_file(
                name=self.index_dest,
                template=self.index_template,
                context=dict(get_issue=get_issue),
                relative_urls=self.settings['RELATIVE_URLS'],
                paginated={'issues': issue_uids},
                template_name='issues',
                url=self.index_url,
            )
            for uid in issue_uids:
                issue = get_issue(uid)
                writer.write_file(
                    name=issue.save_as,
                    template=self.issue_template,
                    context=dict(issue=issue),
                    relative_urls=self.settings['RELATIVE_URLS'],
                    url=issue.url,
                )



class IssueWrapper:
    '''Helper class that adds some methods to any given issue object'''


    def __init__(self, issue, prefix, url_pattern, dest_pattern):
        self._issue = SimpleNamespace(
            ref=issue,
            prefix=prefix,
            url_pattern=url_pattern,
            dest_pattern=dest_pattern,
        )


    def __getattr__(self, attr):
        return getattr(self._issue.ref, attr)


    @property
    def url(self):
        '''Return URL for referring to this issue'''
        return self._format(self._issue.url_pattern)


    @property
    def save_as(self):
        '''Return file path for saving issue page'''
        return self._format(self._issue.dest_pattern)


    def _format(self, pattern):
        '''Format string based on issue fields'''
        issue = self._issue.ref
        prefix = self._issue.prefix
        return pattern.format(
            prefix=prefix,
            uid=issue.uid,
            slug=issue.uid,
        )



def get_generators(pelican_object):
    return IssueGenerator


def register():
    signals.get_generators.connect(get_generators)
