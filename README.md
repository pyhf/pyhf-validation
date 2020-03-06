# pyhf Validation

Validation utilities for HistFactory workspaces

[![GitHub Project](https://img.shields.io/badge/GitHub--blue?style=social&logo=GitHub)](https://github.com/pyhf/pyhf-validation)
[![GitHub Actions Status: CI](https://github.com/pyhf/pyhf-validation/workflows/CI/CD/badge.svg)](https://github.com/pyhf/pyhf-validation/actions?query=workflow%3ACI%2FCD+branch%3Amaster)
[![Code Coverage](https://codecov.io/gh/pyhf/pyhf-validation/graph/badge.svg?branch=master)](https://codecov.io/gh/pyhf/pyhf-validation?branch=master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

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
