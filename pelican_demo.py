#
# Pelican configuration
#


import issyours.pelican
PLUGINS = [issyours.pelican]

RELATIVE_URLS = True
DEFAULT_PAGINATION = 36
LOCALE = 'en_US.UTF-8'
DEFAULT_LANG = 'en'

THEME = '../pelican-alchemy/alchemy'
BOOTSTRAP_CSS = 'https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/yeti/bootstrap.min.css'
THEME_TEMPLATES_OVERRIDES = ['issyours_themes/alchemy']
THEME_CSS_OVERRIDES = ['theme/css/override.css']
TEMPLATE_PAGES = {
    'override.css.html': 'theme/css/override.css',
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
    None: {  # Global rewrite rules
    },
    'GH': {  # For this prefix only
        r'http[s]?://github.com/golang/([^>]+)': r'golang/\1',
        r'http[s]?://git-scm.com/([^>]+)': r'git://\1',
    },
}
