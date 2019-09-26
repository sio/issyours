# Using GitHub as a data source for Issyours

Issyours can help you to create a static website mirror of all issues and pull
requests for a GitHub project. First you use `issyours-github` to obtain the
data from GitHub, then you use Pelican with Issyours plugin to render the
static website.


## Fetcher: backing up issues and pull requests

*Fetcher* is implemented as a command line application: `issyours-github`.
It should be available in `$PATH` after you install the Python package for
Issyours.

```
usage: issyours-github [-h] [--oauth-token TOKEN] [-v] REPO STORAGE_DIR

Fetch all issues and pull requests for a specific GitHub repository. Skip data
that was not updated since the last run.

positional arguments:
  REPO                 Repository identificator in form of "owner/reponame"
                       string
  STORAGE_DIR          Path to directory to be used for data storage

optional arguments:
  -h, --help           show this help message and exit
  --oauth-token TOKEN  OAuth token for accessing GitHub API. By default its
                       value should be provided via $ISSYOURS_GITHUB_TOKEN
                       environment variable. Using a commandline option is
                       less secure and should be avoided.
  -v, --verbose        Increase output verbosity. Repeating this argument
                       multiple times increases verbosity level even further.
```


## Reader: interacting with Pelican plugin

*Reader* for the Pelican plugin should be provided as `GitHubReader` instance.

Example:

```python
from issyours_github import GitHubReader

ISSYOURS_SOURCES = {
    GitHubReader(repo='owner/project', directory=r'/path/to/issue/backup'): {
        'prefix': 'GH',  # Optional, may be omitted
    },
}
```

See [configuration docs](configuring.md) for more information on
Issyours and Pelican settings.
