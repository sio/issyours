# Using and creating themes for Issyours

Issyours renders content that upstream Pelican was not meant to support, so
normal Pelican themes will not produce good results. To achieve quality output
the theme needs to provide two extra templates:

- "issue.html" to render individual issue pages
- "issues.html" to render issues index (paginated)

If your theme does not provide these templates Issyours will show a warning
and will render pages with fallback templates. Those templates are very basic
and are not intended to be used for anything serious. They are provided only
to test that all other components work as expected.


## Creating new themes

Please refer to [Pelican documentation][introduction] for an introduction to
Pelican themes.

In addition to the templates required by Pelican you'll need to create
templates for "issue.html" and "issues.html".

Following variables are added to the default context for these templates:

- issue.html
    - `issue`: an `issyours.pelican.IssueWrapper` object for current issue
    - `avatar_url(person)`: a function that converts `Person` object into a
      corresponding avatar URL
    - `attachment_url(attachment, issue)`: a function that returns URL to an
      attachment file for current issue
- issues.html
    - `get_issue(uid)`: a function that produces `IssueWrapper` object from
      given identifier
- Both templates can make use of `local_date()` function that converts a
  datetime object to a string representation desirable by user.

[introduction]: http://docs.getpelican.com/en/stable/themes.html


## Using existing theme by overriding templates

Instead of creating a whole theme from scratch you may want to add Issyours
support to an existing Pelican theme.

That does not require you to maintain a fork of the theme you like. You can
write extra templates and provide them via `THEME_TEMPLATES_OVERRIDES` in
Pelican settings, for example:

```python
THEME = '/path/to/awesome/pelican/theme'
THEME_TEMPLATES_OVERRIDES = [
    '/path/to/extra/templates/for/that/theme',
]
```

Read more about overriding templates in [Pelican documentation][overrides].

[overrides]: https://docs.getpelican.com/en/stable/settings.html?highlight=THEME_TEMPLATES_OVERRIDES#themes


## Using default theme

If you like what you see in [demo], you might be fine with default
Issyours theme. It is based on [Alchemy] and extra templates are provided
by Issyours Python package.

Install Issyours with default theme:

```
pip install "https://github.com/sio/issyours/tarball/master[with-default-theme]"
```

Include default theme, extra templates and extra stylesheets in Pelican
settings:

```python
import alchemy
THEME = alchemy.path()

THEME_TEMPLATES_OVERRIDES = [issyours.templates.override('alchemy')]
THEME_CSS_OVERRIDES = ['theme/css/override.css']
TEMPLATE_PAGES = {'override.css.html': 'theme/css/override.css'}
```

You can style Alchemy with any of [Boostwatch] themes:

```python
BOOTSTRAP_CSS = 'https://stackpath.bootstrapcdn.com/bootswatch/4.3.1/yeti/bootstrap.min.css'
```

[demo]: https://issyours.ml/demo/issues
[Alchemy]: https://github.com/nairobilug/pelican-alchemy
[Boostwatch]: https://bootswatch.com/
