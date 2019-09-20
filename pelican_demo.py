#
# Pelican configuration
#


import issyours.pelican
PLUGINS = [issyours.pelican]

RELATIVE_URLS = True
DEFAULT_PAGINATION = 15
LOCALE = 'en_US.UTF-8'
DEFAULT_LANG = 'en'

THEME = '../pelican-alchemy/alchemy'
THEME_TEMPLATES_OVERRIDES = ['issyours_themes/alchemy']
THEME_CSS_OVERRIDES = ['theme/css/override.css']
BOOTSTRAP_CSS = 'https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/yeti/bootstrap.min.css'
STATIC_PATHS = ['../issyours_themes/alchemy/override.css']
EXTRA_PATH_METADATA = {
    '../issyours_themes/alchemy/override.css': {'path': 'theme/css/override.css'}
}


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
            'directory': r'../../_issyours_archives/git-bug',
        },
        'prefix': 'GH',
    },
}
ISSYOURS_REWRITE_URLS = {
}
