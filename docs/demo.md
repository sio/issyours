# Issyours demonstration

Makefiles bundled with Issyours source code allow you to generate a working
demo website very quickly. Use this to get a first look at Issyours or as a
supplement to documentation when configuring your own setup.

Your system will not be modified at all. Building steps are executed in
virtual environment and all generated artifacts can be discarded with `make clean`


## Building demo web site

Clone/download this repo and the reference theme:

```
$ git clone "https://github.com/sio/issyours.git"
$ git clone "https://github.com/nairobilug/pelican-alchemy.git"
TODO: Upstream theme does not match reference build
```

Check that Python is available via `python3` command: `python3 --version`.
Set `PY` environment variable to contain the proper Python command if `python3` is
not the right one for you.

Obtain [oAuth token](https://github.com/settings/tokens) from GitHub and save
it to `ISSYOURS_GITHUB_TOKEN` environment variable:

```
$ export ISSYOURS_GITHUB_TOKEN=a88a5...
```

Switch to Issyours directory and run GNU Make:

```
$ cd issyours
$ make demo
```

This will generate all website pages and save them to `demo-output` directory.
Python virtual environment will be automatically created and will be reused
for repeated `make` invocations.

You can browse HTML pages from the filesystem or launch a local webserver and
browse them via <http://localhost:8000/issues>:

```
$ make serve
```


## Customizing demo build

Use these environment variables to alter the behavior of demo build:
- `DEMO_REPO` *(default: sio/bash-complete-partial-path)* -
  the repo to mirror issues and pull requests from
- `DEMO_STORAGE` *(default: demo-github-data)* -
  directory to save data from GitHub
- `DEMO_THEME` *(default: ../pelican-alchemy/alchemy)* -
  path to Pelican theme