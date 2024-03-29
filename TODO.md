# TODO list for Issyours

- GitHubFetcher improvements
    - When issue is referenced from another issue or pull request, it is not
      visible in its API response, therefore not rendered by us (git-bug#175)
    - Code review comments attached to individual lines of code are not
      exported (git-bug#57)
- GitHubReader content improvements
    - Emoji reactions (add to HTML body)
    - Multi-level todo lists (LibPQ#17)
- Internal hyperlinks and mentions in GitHubReader
    - Issues and pull requests
    - User mentions
    - Attachment links
- Internal hyperlinks in Renderer (with other Pelican pages)
- Multi-prefix common index for issues (based on date?)
- Test on a large dataset
- Profile memory and CPU usage

> References in parentheses contain repo and issue number where the feature is
> in use. MichaelMure/git-bug is used as default test dataset
