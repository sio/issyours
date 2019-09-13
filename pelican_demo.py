#
# Pelican configuration
#


import issyours.pelican
PLUGINS = [issyours.pelican]



#
# Issyours plugin configuration
#


from issyours_github import GitHubReader


ISSYOURS_ISSUE_URL = 'issue/{slug}/'
ISSYOURS_ISSUE_SAVE_AS = 'issue/{slug}/index.html'
ISSYOURS_LIST_URL = 'issues/{slug}/'
ISSYOURS_LIST_SAVE_AS = 'issues/{slug}/index.html'
ISSYOURS_PAGINATION = (
    (1, '{base_name}/', '{base_name}/index.html'),
    (2, '{base_name}/{number}/', '{base_name}/{number}/index.html'),
)
ISSYOURS_SOURCES = {
    GitHubReader: {
        'init': {
            'repo': r'MichaelMure/git-bug',
            'directory': r'J:\_issyours_archives\git-bug',
        },
        'prefix': 'GH',
    },
}
ISSYOURS_REWRITE_URLS = {
}
