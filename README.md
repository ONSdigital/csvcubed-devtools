# csvcubed - devtools

> Shared test functionality & dev dependencies which are commonly required.

Part of the [csvcubed](https://github.com/GSS-Cogs/csvcubed/) project.

The *devtools* package contains common packages necessary for development of *csvcubed* such as:

* behave - for behaviour testing / BDD
* docker - to execute docker containers, used to transform and test csvcubed outputs.
* black - auto-formatter to ensure consistent code formatting/style.

It also contains shared functionality to support testing, e.g. common *behave* test steps like checking that files exist, using temporary directories when testing as well as tools to copy test files to & from docker containers.

## Installation

This package should be installed as a [dev dependency](https://python-poetry.org/docs/cli#options-3) to ensure that end-users of *csvcubed* are not required to install development tools such as docker.

## Adding a package

Dependencies are installed in the [Docker container](./Dockerfile) on a container-wide basis. If you're adding a new package, first run:

```bash
poetry add <some-package>
```

And once that has completed, if you are working inside the docker dev container, you must rebuild the container before the packages will be available for your use.