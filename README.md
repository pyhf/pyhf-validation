# pyhf Validation

Validation utilities for HistFactory workspaces

[![GitHub Project](https://img.shields.io/badge/GitHub--blue?style=social&logo=GitHub)](https://github.com/pyhf/pyhf-validation)
[![GitHub Actions Status: CI](https://github.com/pyhf/pyhf-validation/workflows/CI/CD/badge.svg)](https://github.com/pyhf/pyhf-validation/actions?query=workflow%3ACI%2FCD+branch%3Amain)
[![Code Coverage](https://codecov.io/gh/pyhf/pyhf-validation/graph/badge.svg?branch=main)](https://codecov.io/gh/pyhf/pyhf-validation?branch=main)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/pyhf/pyhf-validation/main.svg)](https://results.pre-commit.ci/latest/github/pyhf/pyhf-validation/main)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/pyhf/pyhf-validation.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/pyhf/pyhf-validation/latest/files/)
[![CodeFactor](https://www.codefactor.io/repository/github/pyhf/pyhf-validation/badge)](https://www.codefactor.io/repository/github/pyhf/pyhf-validation)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![Docker Pulls](https://img.shields.io/docker/pulls/pyhf/pyhf-validation)](https://hub.docker.com/r/pyhf/pyhf-validation)
[![Docker Image Size (tag)](https://img.shields.io/docker/image-size/pyhf/pyhf-validation/latest)](https://hub.docker.com/r/pyhf/pyhf-validation/tags?name=latest)

## Installation

To install `pyhf-validation` from GitHub (PyPI coming soon) run
```bash
python -m pip install "git+https://github.com/pyhf/pyhf-validation.git#egg=hfval"
```

## Developing

To develop, we suggest using [virtual environments](https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments) together with `pip`.
Once the environment is activated, clone the repo from GitHub and install all necessary packages for development

```
python -m pip install --ignore-installed --upgrade -e .[complete]
```

Then setup the Git pre-commit hook for [Black](https://github.com/psf/black)  by running

```
pre-commit install
```

## Authors

Please check the [contribution statistics for a list of contributors](https://github.com/pyhf/pyhf-validation/graphs/contributors)
