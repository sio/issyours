# Design document for Issyours (historical)

> This design document was adapted from author's personal notes. It will
> not be kept updated as the development continues but still may be
> interesting to some.

> This project was born from author's continuous reflections on
> [distributed issue tracking](distributed.md).

The wish to have distributed issue tracking system is often motivated by the
wish to own the project's data more than by the need to support a truly
distributed workflow. In such cases a read-only web archive that mirrors
information from current issue tracker might become a solution.

When all issue data is readily available from a controlled web host it is less
scary to use third party services for the actual issue management. In such
scenario the issue tracking service gets demoted to the rank of a mere
application that you use to generate and manipulate your data - the data that
you own and that you store wherever you like. Backups in machine readable form
are not enough because they are not human-accessible at any given moment. It
is still costly to abandon current service provider so the lock-in is not
fully lifted.

Others have already arrived to the same conclusion. Matomo team had even
created [an application][matomo-app] to mirror their GitHub issues [to their
website][matomo-mirror]. I want to create a similar application that would
cover more use cases. What I'd like to do differently:

- Generate static web site instead of running PHP web application
- Use modular structure to enable support for other issue trackers in future

[matomo-app]: https://github.com/matomo-org/github-issues-mirror
[matomo-mirror]: https://issues.matomo.org/


## Overview of datasets collected by GitHub

The first supported target will be GitHub. It is the most popular issue
tracking platform for open source projects at the moment and it is the place
where the projects I'm interested in backing up are hosted.

GitHub collects the following data for each project:

- **Source code** - already easily backed up and mirrored thanks to git.
- **Wiki** - also a git repository.
- **Issues and Pull Requests** - the target of my application.
- **Projects** - can be simplified to a type of issue labels *(Update:
  unfortunately, Projects are not yet visible via API)*.
- **Milestones** - can be simplified to a type of issue labels.
- **Actions** - are out of scope for this document.


## Modular architecture

To enable flexibility and to be able to support different issue trackers in
future the architecture of the application will be layered.

#### Components

*Fetcher* -- *Storage* -- *Reader* -- *Renderer*

- *Fetcher* obtains raw data and saves it to *Storage*
- *Reader* reads data from *Storage* and provides it in uniform fashion
- *Renderer* takes data from *Reader* and creates a static web site

Each layer should interact only with the adjacent ones. The layers are
explained more below.

#### Fetcher

This part has the most loose coupling with the rest of the application.
*Fetcher* can be provided by the issue tracking service, such as export or
backup mechanism. It can also be a standalone application that is used to
back up all the issue information from the service.

#### Storage

This layer is not an application but a set of conventions for persistently
storing the data. It can be a filesystem hierarchy standard or a database
schema or anything else.

#### Reader

*Reader* is the library that provides uniform API to read the data contained
in *Storage*.

#### Renderer

This is a static site generator that creates a nice looking web site from data
fed to it by *Reader*. I plan to extend [Pelican] for this purpose.

[Pelican]: https://getpelican.com


## Issues data model

*Reader* and *Renderer* are expected to operate on the following data classes:

- Issue
- Person
- IssueComment
- IssueEvent (a stripped down comment?)
- IssueLabel


## Reader API draft

The *Reader* object produces all the objects mentioned above. The objects
themselves are meant to be read only.

- Instanciation: `r = Reader(path=...)`
- Issues generator: `r.issues(sort_by=...)`
- Individual issue access: `i = r.issue(uid)`
- Related objects: `i.events(sort_by=...)`, `i.comments(sort_by=...)`
- Issue tracker member: `p = r.person(nickname)`


## Gotchas and implementation details

**Features:**

- Handle internal hyperlinks. Generate automatic hyperlinks when issue number
  is mentioned.
    - Automatic detection of interlinks (mentions) has to happen in *Reader*
      because conventions on these mentions vary between the service platforms
    - *Reader* knows nothing about URL conventions used by *Renderer*, so it
      should create some uniform URLs for interlinks that will be rewritten
      later
- Allow setting uid prefix for each *Reader* object. It will help to avoid
  collisions when importing issues from multiple sources.
- Allow customizable URL rewrites.
    - URL substitution must be done in *Renderer* because it needs to take
      into account all existing *Storages*. Also, the scope of the rules must
      be configurable: global or for some *Storages* only.
- GitHub API stores reactions to issues and comments in a separate V3 endpoint
  (`.../reactions`) - use that with condiitonal requests to fetch reactions
  data.

**Implementation:**

- Pelican needs all the entries to appear in the context sometimes:
    - Use lazy object wrappers
    - Use weakref cache of *Issue* objects within *Reader* (see:
      WeakValueDictionary)
    - Provide access to UID list before creating any actual *Issue* instances.
      To be used for pagination.
    - Add custom *Generator* to Pelican via plugin
    - Do not use Pelican reader by file extension. Our *Reader* must not rely
      on *Storage* being file based.
    - Use caching in Pelican. Maybe only output caching. If output caching is
      not enough, create custom writer for Pelican that skips unmodified
      issues.
- High-level overview of integration with Pelican
    - Custom generator populates the context with issue content objects
    - Custom content objects for issues (make them as lazy as possible)
    - Custom theme to support issue content objects and their index
