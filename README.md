[![Build Status](https://travis-ci.org/dz0ny/apt-transport-github.svg?branch=master)](https://travis-ci.org/dz0ny/apt-transport-github)

# apt-transport-github

Fetch Debian packages via Github release API

!!!NOT YET READY FOR PRODUCTION!!!

# Install via public repo

```
$ add-apt-repository "deb github://dz0ny/apt-transport-github any latest"
$ apt-get update
$ apt-get install apt-transport-github
```

# Install via private repo

```
$ add-apt-repository "deb github://github_api_key@dz0ny/apt-transport-github any v0.1.4"
$ apt-get update
$ apt-get install apt-transport-github
```

# How to package
TODO(see Makefile for this project)