# TODO list for Issyours

- [ ] GitHubFetcher improvements
    - [ ] When issue is referenced from another issue or pull request, it is
          not visible in its API response, therefore not rendered by us (git-bug#175)
    - [ ] Code review comments attached to individual lines of code are not
          exported (git-bug#57)
- [ ] GitHubReader content improvements
    - [ ] Inline emojis (git-bug#175)
    - [ ] Emoji reactions
    - [ ] GFM todo lists (git-bug#175)
    - [ ] GFM strikethrough (git-bug#71)
- [ ] Internal hyperlinks and mentions in GitHubReader
    - [ ] Issues and pull requests
    - [ ] User mentions
    - [ ] Attachment links
- [ ] Internal hyperlinks in Renderer (with other Pelican pages)
- [ ] URL rewrite rules
- [ ] Multi-prefix common index for issues (based on date?)
- [ ] README for the project
- [ ] Explain licensing: Pelican is a dependency, Matomo is inspiration
- [ ] Bump versions before publishing (fetcher format, Python package, user
      agent)
- [ ] Test on a large dataset
- [ ] Profile memory and CPU usage
