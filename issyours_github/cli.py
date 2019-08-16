'''
Commandline entry point for GitHub Issues fetcher
'''


import os
from argparse import ArgumentParser

from issyours_github import GitHubFetcher


ENV_TOKEN = 'ISSYOURS_GITHUB_TOKEN'


def run(*a, **ka):
    args = parse_args(*a, **ka)
    github = GitHubFetcher(args.repo, args.dest, args.oauth_token)
    github.fetch()


def parse_args(*a, **ka):
    parser = ArgumentParser(description=(
        'Fetch all issues and pull requests for a specific GitHub repository. '
        'Skip data that was not updated since the last run.'
    ))
    parser.add_argument(
        'repo',
        metavar='REPO',
        help='Repository identificator in form of "owner/reponame" string',
    )
    parser.add_argument(
        'dest',
        metavar='STORAGE_DIR',
        help='Path to directory to be used for data storage',
    )
    parser.add_argument(
        '--oauth-token',
        default=os.getenv(ENV_TOKEN),
        metavar='TOKEN',
        help=('OAuth token for accessing GitHub API. '
              'By default its value should be provided via ${} environment variable. '
              'Using a commandline option is less secure and should be avoided.')
             .format(ENV_TOKEN)
    )
    args = parser.parse_args(*a, **ka)

    repo_parts = args.repo.split('/')
    if len(repo_parts) != 2 or not all(repo_parts):
        parser.error('Invalid repo identificator: {}'.format(args.repo))

    if not args.oauth_token:
        parser.error('GitHub OAuth token was not provided')

    return args
