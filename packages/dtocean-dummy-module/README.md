[![Build status](https://ci.appveyor.com/api/projects/status/github/DTOcean/dtocean-dummy-module?branch=master&svg=true)](https://ci.appveyor.com/project/DTOcean/dtocean-dummy-module)
[![codecov](https://codecov.io/gh/DTOcean/dtocean-dummy-module/branch/master/graph/badge.svg)](https://codecov.io/gh/DTOcean/dtocean-dummy-module)
[**Lintly Score**](https://lintly.com/gh/DTOcean/dtocean-dummy-module/)
[![release](https://img.shields.io/github/release/DTOcean/dtocean-dummy-module.svg)](https://github.com/DTOcean/dtocean-dummy-module/releases/latest)

## Overview

A python package to demonstrate some of the many features of Python and
introduce a typical structure for a Python package.

## Quick Start

### Installation

The DTOCEAN Python dummy module is currently only tested on Windows 32
and 64 bit systems. Your mileage may vary on other platforms.

#### Setuptools

```shell
python setup.py install
```

#### Anaconda

The demo has been packaged for use with the [Anaconda Scientific Python
Distribution](https://store.continuum.io/cshop/anaconda/).

```shell
conda config --append channels dataonlygreater
conda install dtocean-dummy-module
```

## Example Usage

The following commands are run from the
[command-line interface](http://en.wikipedia.org/wiki/Command-line_interface).

### Execution

```shell
dtocean-dummy 5
```

### Help

```shell
dtocean-dummy -h
```

## Update

### Anaconda

```shell
conda update dtocean-dummy-module
```

## Uninstallation

### Pip

```shell
pip uninstall dtocean-dummy-module
```

### Anaconda

```shell
conda remove dtocean-dummy-module
```
