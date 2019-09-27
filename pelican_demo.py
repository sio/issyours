#
# Reading environment variables
#
import os
demo_repo = os.environ['DEMO_REPO']
demo_data = os.environ['DEMO_STORAGE']


#
# Pelican configuration
#


import issyours.pelican
PLUGINS = [issyours.pelican]

RELATIVE_URLS = True
DEFAULT_PAGINATION = 36
LOCALE = 'en_US.UTF-8'
DEFAULT_LANG = 'en'

import alchemy
THEME = alchemy.path()
BOOTSTRAP_CSS = 'https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/yeti/bootstrap.min.css'
THEME_TEMPLATES_OVERRIDES = ['issyours_themes/alchemy']
THEME_CSS_OVERRIDES = ['theme/css/override.css']
TEMPLATE_PAGES = {
    'override.css.html': 'theme/css/override.css',
}


#
# Issyours plugin configuration
#


from issyours_github import GitHubReader

ISSYOURS_SOURCES = {
    GitHubReader(repo=demo_repo, directory=demo_data): {},
}
