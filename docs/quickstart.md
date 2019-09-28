# Getting started with Issyours

Check [demo website](https://issyours.ml/demo/issues) and [demo
tutorial](demonstration.md) for a quick look at Issyours.

Using Issyours requires some understanding of how Pelican works. Refer to
[Pelican documentation](http://docs.getpelican.com/en/stable/quickstart.html)
for introduction.

Here are the steps you should follow to build your own browsable issues
archive.


## Install Issyours

Issyours can be installed with pip. Authors recommend installing all Python
packages in [virtual environment](https://docs.python.org/3/tutorial/venv.html).

Install Issyours along with default Pelican theme

```
$ pip install "https://github.com/sio/issyours/tarball/master[with-default-theme]"
```


## Fetch issues data from the service provider

To fetch issues and pull requests from GitHub you need to obtain an
[oAuth token](https://github.com/settings/tokens) and save it to
`ISSYOURS_GITHUB_TOKEN` environment variable

```
$ export ISSYOURS_GITHUB_TOKEN=a88a5...
```

After that run provided backup utility

```
$ issyours-github "username/reponame" "/path/to/local-issue-backup"
```

Issues and pull requests will be backed up to JSON files in the specified
directory. That may take a while if target repo has a lot of recorded issues
and pull requests because of GitHub's API rate limit. Add `-vvvv` to command
line to monitor the progress more closely.

Refer to [Issyours documentation](github.md) for more information on
interacting with GitHub as data source.


## Create Pelican project and enable Issyours plugin

Create new Pelican project (see
[documentation](http://docs.getpelican.com/en/stable/quickstart.html#create-a-project))

```
$ pelican-quickstart
```

Add minimal Issyours configuration to Pelican settings

```python
# pelicanconf.py

# <..lines skipped..>

import issyours.pelican
PLUGINS = [issyours.pelican]

import alchemy
THEME = alchemy.path()
THEME_TEMPLATES_OVERRIDES = [issyours.templates.override('alchemy')]
THEME_CSS_OVERRIDES = ['theme/css/override.css']
TEMPLATE_PAGES = {'override.css.html': 'theme/css/override.css'}

from issyours_github import GitHubReader
ISSYOURS_SOURCES = {
    GitHubReader(repo='sio/HomeLibraryCatalog', directory='issue-backup'): {},
}
```

Read more about [configuring Issyours](configuring.md) and [theming
Issyours](themes.md) in documentation.


## Render static web site

Run Pelican to generate the contents of your website

```
$ pelican . -o output -s pelicanconf.py
```

Check that everything works with a local development web server:
<http://localhost:8000/issues>:

```
$ pelican --listen
```

Resulting HTML output is ready to be published with any web server.
