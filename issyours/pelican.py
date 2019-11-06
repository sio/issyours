'''
Pelican plugin for rendering issues archive on static website
'''


import logging
import os
import re
from itertools import chain
from pkg_resources import resource_string
from shutil import copyfileobj
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
                raise
            log.warning(
                ('Theme provides no template for {!r}, '
                 'falling back to a very basic one').format(name)
            )
            self._templates[name] = self.env.from_string(code.decode('utf-8'))
            return self._templates[name]


    def generate_context(self):
        self.url_rewriter = URLRewriter(self.settings)

        date_format = self.settings['DEFAULT_DATE_FORMAT']  # TODO: multiple languages?
        self.context['local_date'] = lambda dt: dt.strftime(date_format)

        self.issue_readers = {}
        if 'ISSYOURS_SOURCES' not in self.settings:
            raise ValueError('required Pelican settings not found: ISSYOURS_SOURCES')
        for reader, extras in self.settings['ISSYOURS_SOURCES'].items():
            extras = extras or {}
            prefix = extras.get('prefix', '')
            if prefix in self.issue_readers:
                raise ValueError('non-unique prefix in ISSYOURS_SOURCES: {!r}'.format(prefix))
            self.issue_readers[prefix] = reader

        self.issue_template = self.get_template('issue')
        self.index_template = self.get_template('issues')

        if self.settings.get('ISSYOURS_AVATAR_SAVE_AS') is None:  # None for default value, '' to disable avatars
            self.settings['ISSYOURS_AVATAR_SAVE_AS'] = 'issues/avatars/{prefix}/{slug}'

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
        self.index_url = self.settings.get(
            'ISSYOURS_INDEX_URL',
            'issues/{prefix}/index.html'
        )
        self.index_dest = self.settings.get(
            'ISSYOURS_INDEX_SAVE_AS',
            self.index_url if self.index_url.endswith('.html') else self.index_url + '/index.html'
        )
        self.attach_pattern = self.settings.get(
            'ISSYOURS_ATTACHMENT_SAVE_AS',
            'attachments/{issue}/{name}'
        )


    def generate_output(self, writer):
        for prefix, reader in self.issue_readers.items():
            def get_issue(uid):
                issue = reader.issue(uid)
                return IssueWrapper(
                    issue=issue,
                    prefix=prefix,
                    url_pattern=self.url_pattern,
                    dest_pattern=self.dest_pattern,
                    rewriter=self.url_rewriter,
                )

            avatar_pattern = self.settings['ISSYOURS_AVATAR_SAVE_AS']
            def avatar_url(person):
                if not person.picture:
                    return None
                return avatar_pattern.format(slug=person.nickname, prefix=prefix)

            def attachment_url(attachment, issue):
                return self.attach_pattern.format(issue=issue.slug, name=attachment.name)

            issue_uids = list(reader.issue_uids())
            context = self.context.copy()
            context['get_issue'] = get_issue
            writer.write_file(
                name=_pattern(self.index_dest, prefix=prefix),
                template=self.index_template,
                context=context,
                relative_urls=self.settings['RELATIVE_URLS'],
                paginated={'issues': issue_uids},
                template_name='issues',
                url=_pattern(self.index_url, prefix=prefix),
            )
            for uid in issue_uids:
                context = self.context.copy()
                context['issue'] = issue = get_issue(uid)
                context['avatar_url'] = avatar_url
                context['attachment_url'] = attachment_url
                writer.write_file(
                    name=issue.save_as,
                    template=self.issue_template,
                    context=context,
                    relative_urls=self.settings['RELATIVE_URLS'],
                    url=issue.url,
                )
                comment_attachments = (a for c in issue.comments() for a in c.attachments())
                for attach in chain(issue.attachments(), comment_attachments):
                    attach_filename = os.path.join(writer.output_path, attachment_url(attach, issue))
                    os.makedirs(os.path.dirname(attach_filename), exist_ok=True)
                    with open(attach_filename, 'wb') as attachment:
                        copyfileobj(attach.stream, attachment)
                        log.debug('Written attachment for issue %s: %s', issue.slug, attach_filename)


            if not avatar_pattern:
                continue
            for person in reader.persons():
                if not person.picture:
                    continue
                avatar_path = os.path.join(writer.output_path, avatar_url(person))
                os.makedirs(os.path.dirname(avatar_path), exist_ok=True)
                with open(avatar_path, 'wb') as avatar:
                    copyfileobj(person.picture, avatar)
                    log.debug('Written user picture for %s: %s', person.nickname, avatar_path)



class IssueWrapper:
    '''Helper class that adds some methods to any given issue object'''


    def __init__(self, issue, prefix, url_pattern, dest_pattern, rewriter):
        self._issue = SimpleNamespace(
            ref=issue,
            prefix=prefix,
            url_pattern=url_pattern,
            dest_pattern=dest_pattern,
            rewriter=rewriter,
        )


    def __getattr__(self, attr):
        return getattr(self._issue.ref, attr)


    @property
    def body(self):
        return self._issue.rewriter.rewrite(self._issue.ref.body, self._issue.prefix)


    def comments(self):
        for comment in self._issue.ref.comments():
            yield CommentWrapper(comment, self._issue.prefix, self._issue.rewriter)


    def feed(self):
        for item, kind in self._issue.ref.feed():
            if kind == 'comment':
                yield CommentWrapper(item, self._issue.prefix, self._issue.rewriter), kind
            else:
                yield item, kind


    @property
    def url(self):
        '''Return URL for referring to this issue'''
        return self._format(self._issue.url_pattern)


    @property
    def save_as(self):
        '''Return file path for saving issue page'''
        return self._format(self._issue.dest_pattern)


    @property
    def prefix(self):
        return self._issue.prefix


    @property
    def slug(self):
        return self.prefix + self.uid


    def _format(self, pattern):
        '''Format string based on issue fields'''
        return _pattern(
            pattern,
            prefix=self.prefix,
            uid=self.uid,
            slug=self.slug,
        )



class CommentWrapper:
    '''Helper class that adds some methods to any given comment object'''


    def __init__(self, comment, prefix, rewriter):
        self._comment = SimpleNamespace(
            ref=comment,
            prefix=prefix,
            rewriter=rewriter,
        )


    def __getattr__(self, attr):
        return getattr(self._comment.ref, attr)


    @property
    def body(self):
        return self._comment.rewriter.rewrite(self._comment.ref.body, self._comment.prefix)



class URLRewriter:
    '''
    Handle custom URL rewrites in issue body and in comments
    '''

    HREF = r'(?P<_prefix><[^>]+href=\s*"\s*){}(?P<_postfix>\s*"[^>]*>)'
    SUB  = r'\g<_prefix>{}\g<_postfix>'

    def __init__(self, settings):
        config = settings.get('ISSYOURS_REWRITE_URLS', {})
        self.rules = {}
        for prefix, rules in config.items():
            self.rules[prefix] = self._compile(rules)


    def _compile(self, rules):
        compiled = {}
        for regex, substitution in rules.items():
            regex = re.compile(self.HREF.format(regex))
            subst = self.SUB.format(_increment_backrefs(substitution))
            compiled[regex] = subst
        return compiled


    def rewrite(self, html_string, reader_prefix):
        '''Apply rewrite rules to HTML string'''
        output = html_string
        for prefix in (None, reader_prefix):
            for regex, substitution in self.rules.get(prefix, {}).items():
                output = regex.sub(substitution, output)
        return output



def _increment_backrefs(pattern, increment=1):
    '''Increment all backreferences by a number'''
    BACKSLASH = '\\'
    NUMBER = 'number'
    EMPTY = ''
    DIGITS = set('0123456789')
    output = []
    number = EMPTY
    previous = EMPTY
    for char in chain(pattern, [EMPTY]):
        if char in DIGITS \
        and (previous == BACKSLASH or previous == NUMBER):
            number += char
            previous = NUMBER
        else:
            if number:
                output.append(str(int(number) + increment))
                number = EMPTY
            output.append(char)
            if previous == BACKSLASH and char == BACKSLASH:
                previous = EMPTY
            else:
                previous = char
    return ''.join(output)


def _pattern(pattern, __double_slash=re.compile('//*'), **kw):
    '''Format index patterns'''
    return __double_slash.sub('/', pattern.format(**kw))


def get_generators(pelican_object):
    return IssueGenerator


def register():
    signals.get_generators.connect(get_generators)
