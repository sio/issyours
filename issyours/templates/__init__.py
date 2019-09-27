'''
Expanding Pelican themes for compatibility with Issyours

This module contains extra templates for adding Issyours support to
existing Pelican themes.

Use `THEME_TEMPLATES_OVERRIDES` to tell Pelican which extra templates to use.

See Pelican documentation for more information:
https://docs.getpelican.com/en/latest/settings.html?highlight=theme_templates_overrides#themes
'''


from pkg_resources import resource_filename, resource_exists


def override(theme):
    '''
    Return path to extra templates for a specific theme

    Currently the following themes are supported:
      - alchemy (https://github.com/nairobilug/pelican-alchemy)
    '''
    if not resource_exists(__name__, theme):
        raise ValueError('no overriding templates found for theme: {}'.format(theme))
    return resource_filename(__name__, theme)
