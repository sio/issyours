# Read-only archive for any issue tracker

## Project status

Minimum viable product. You can already use Issyours to create usable HTML
archive for GitHub issues.

Breaking changes in configuration files are unlikely, but not impossible.
You should test that new version works for you if updating.


## Overview

This project aims to enable developers to own the data they submit to an issue
tracker. Issyours offers more than just a data dump for backup purposes, it
creates fully browsable issues archive ready to be deployed as a static web
site.

Issyours currently supports exporting GitHub Issues and Pull Requests and
rendering them with Pelican static site generator. More data sources are to be
supported, the project was meant to be easily extensible from day one.

The core components of Issyours work as layers:

- *Fetcher* obtains raw data from issue tracker and saves in to a persistent
  *Storage*
- *Reader* provides an uniform API for reading issue data from *Storage*
- *Renderer* creates a static web site for viewing issues available via
  *Reader*

## Installation

Issyours can be installed with pip:

```
pip install "https://github.com/sio/issyours/tarball/master"
```

That provides you with Python packages for `issyours` and `issyours_github`
and a command line application `issyours-github`.


## Usage

Issyours is an plugin for Pelican. Refer to [Pelican documentation] for
introductory overview. All configuration happens within Pelican settings file
([sample]).

Enable Issyours plugin:

```python
import issyours.pelican
PLUGINS = [issyours.pelican]
```

Configure at least one data source:

```python
from issyours_github import GitHubReader
ISSYOURS_SOURCES = {
    GitHubReader(repo='...', directory='...'): None,
}
```

After configuring Pelican and Issyours run `pelican $BLOG_CONTENT -o
$SITE_OUTPUT -s $CONFIG_FILE` to generate HTML pages for the static website.

[Pelican documentation]: http://docs.getpelican.com/en/stable/
[sample]: pelican_demo.py


## Support and contributing

If you need help with using Issyours, please create
**[an issue](https://github.com/sio/issyours/issues)**. Issues are also the
primary venue for reporting bugs and posting feature requests. General
discussion related to this project is also acceptable and very welcome!

In case you wish to contribute code or documentation, feel free to open **[a
pull request](https://github.com/sio/issyours/pulls)**. That would certainly
make my day!

I'm open to dialog and I promise to behave responsibly and treat all
contributors with respect. Please try to do the same, and treat others the way
you want to be treated.

If for some reason you'd rather not use the issue tracker, contacting me via
email is OK too. Please use a descriptive subject line to enhance visibility
of your message. Also please keep in mind that public discussion channels are
preferable because that way many other people may benefit from reading past
conversations. My email is visible under the GitHub profile and in the commit
log.


## License and copyright

Copyright 2019 Vitaly Potyarkin

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.


## Development roadmap

See [TODO list](TODO.md).
