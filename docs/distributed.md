# Distributed issue tracking

> This document was adapted from author's personal notes. It will not be kept
> up to date but still may be interesting to some.


## Rationale

GitHub may be nice but it's a centralized service that may become a single
point of failure for an opensource project. They're already known to be
blocking users from Iran and Crimea. Depending on their services is risky.

Regular backup of all project's data is an option, but the tooling for that
is not really friendly yet.


### Why?

- It is scary to give away valuable data and to hope that cloud provider will
  keep it safe
- Cloud provider might not even return your data back to you
- Decentralized and offline collaboration


### Cons

- Unprivileged users have to be able to create new issues and comments, hence
  there is a need for web application. If we have to host a web application,
  we might as well host a conventional issue tracker and keep all the data
  safe on our personal server.
- The initial problem was not that the data needs to be distributed, but that
  the data has to be owned by the project and not by the service provider. Git
  solves that problem for the source code, because it eliminates the need to
  excessively trust the service provider.


## Existing distributed bug tracking tools

- [List of distributed bug tracking
  software](http://dist-bugs.branchable.com/software/)
- [git-bug](https://github.com/MichaelMure/git-bug) - Actively developed Go
  project. Seems to be exactly what I've been looking for. Need to investigate
  further. The project is in early stages of development yet.
- [Bugs Everywhere](http://www.bugseverywhere.org/) - Seems unmaintained (last
  commit was in 2013)
- [git-issue](https://github.com/dspinellis/git-issue) - Shell project with
  a small number of contributors. Activity is a little low, the future seems
  unclear.
- [sit](https://github.com/sit-fyi/sit) - Promising project that started good,
  but slowed down and didn't show any progress since 2018. They've been eating
  their own dogfood since the very beginning though.
- [git-dit](https://github.com/neithernut/git-dit/) - A small project that
  seems too aimed at providing Rust library, maybe at the expense of the main
  application. Started relatively long ago, but development seems slow.
  The data model they use resonates with my ideas very well.
- [ZeroNet](https://zeronet.io/) - not a bug tracking system, but it provides
  a distributed publishing platform with public forums. Data is conventionally
  stored in JSON, rendered with JavaScript.
- Mailing list with distributed backups of its archives in maildir/mbox
  format. This is what has been used by Linux and some other opensource
  projects years before Bugzilla and Trac came along. Mailman 3 provides a
  nice modern web UI for archives (hyperkitty).


## Other links

- [Decentralized Issue
  Tracking](https://beyermatthias.de/blog/2016/05/29/decentralized-issue-tracking/) -
  a blog post by a person interested in the same topic (2016). He later
  started git-dit.
- [Issue tracker plugin for DocuWiki](https://github.com/Taggic/issuetracker)
