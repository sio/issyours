#
# Pelican configuration
#


import issyours.pelican
PLUGINS = [issyours.pelican]

RELATIVE_URLS = True
DEFAULT_PAGINATION = 15
LOCALE = 'en_US.UTF-8'
DEFAULT_LANG = 'en'

THEME = 'issyours_theme/alchemy'


#
# Issyours plugin configuration
#

# TODO: check that all variables provide sensible defaults or fail loudly when unset


from issyours_github import GitHubReader


#ISSYOURS_ISSUE_URL = 'issue/{slug}/'
#ISSYOURS_ISSUE_SAVE_AS = 'issue/{slug}/index.html'
#ISSYOURS_LIST_URL = 'issues/'
#ISSYOURS_LIST_SAVE_AS = 'issues/index.html'
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
