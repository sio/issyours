# Configuration options for Issyours

## Global configuration

###### ISSYOURS_DEBUG

Setting this environment variable to any value enables more verbose output
across all Issyours components.


## Pelican plugin configuration

Issyours provides a plugin for Pelican static site generator. All
configuration is done in the Pelican settings file (e.g. `pelicanconf.py`).
See [sample](../pelican_demo.py).


### Data sources (required)

###### ISSYOURS_SOURCES

A dictionary where keys are *Reader* instances and values are either
`None` or dictionaries providing extra metadata for *Reader*. Currently
the only supported metadata field is "prefix".

Example:

```python
ISSYOURS_SOURCES = {
    GitHubReader(repo='owner/project', directory=r'/path/to/local/backup'): {
        'prefix': 'GH',
    },
}
```


### Output paths and URLs (optional)

These are the patterns for saving files in the output directory and for URLs
to refer to them. All paths and URLs are relative to the output directory.
All patterns rely internally on Python [string
formatting](https://docs.python.org/3/library/stdtypes.html#str.format)
(see: `help(str.format)`)


###### ISSYOURS_ATTACHMENT_SAVE_AS

The path to save issue attachments to.

Default: `attachments/{issue}/{name}`

Available substitutions:

- `{issue}` - issue slug (usually prefix+uid)
- `{name}` - attachment filename provided by *Reader*

###### ISSYOURS_AVATAR_SAVE_AS

The path to save person's profile pictures to.

Default: `issues/avatars/{prefix}/{slug}`

Available substitutions:

- `{slug}` - unique person's identifier (usually, login or nickname)
- `{prefix}` - prefix assigned to the *Reader* in Pelican config

###### ISSYOURS_ISSUE_URL

The URL to refer to specific issue by.

Default: `issue/{slug}.html`

Available substitutions:

- `{slug}` - issue identifier that is unique across all enabled *Readers*
  (currently prefix+uid)
- `{prefix}` - prefix assigned to the *Reader* in Pelican config
- `{uid}` - issue identifier that is unique only within its parent *Reader*

###### ISSYOURS_ISSUE_SAVE_AS

The path to save issue page to.

Default: calculated from `ISSYOURS_ISSUE_URL`

Available substitutions:

- `{slug}` - issue identifier that is unique across all enabled *Readers*
  (currently prefix+uid)
- `{prefix}` - prefix assigned to the *Reader* in Pelican config
- `{uid}` - issue identifier that is unique only within its parent *Reader*

###### ISSYOURS_INDEX_URL

Base URL for issue index pages. Honors [PAGINATION_PATTERNS] from Pelican config.

Default: `issues/{prefix}/index.html`

Available substitutions:

- `{prefix}` - prefix assigned to the *Reader* in Pelican config

###### ISSYOURS_INDEX_SAVE_AS

The path to save index pages to. Honors [PAGINATION_PATTERNS] from Pelican config.

Default: calculated from `ISSYOURS_INDEX_URL`

Available substitutions:

- `{prefix}` - prefix assigned to the *Reader* in Pelican config

[PAGINATION_PATTERNS]: https://docs.getpelican.com/en/stable/settings.html?highlight=pagination_patterns#pagination


### URL rewrite rules (optional)

###### ISSYOURS_REWRITE_URLS

Regex substitution rules for URL targets in issue and comment body. Applied
in *Renderer* during generation of the static website. Large number of rules
may slow site generation a bit.

Rules may target either a specific *Reader* by prefix or all enabled *Readers*
at once.

Example:

```python
ISSYOURS_REWRITE_URLS = {
    None: {  # Global rewrite rules
    },
    'GH': {  # For this prefix only
        r'http[s]?://github.com/golang/([^>]+)': r'https://my-golang-mirror.net/\1',
        r'http[s]?://git-scm.com/([^>]+)': r'git-docs://\1',
    },
}
```
