[![appveyor](https://ci.appveyor.com/api/projects/status/github/DTOcean/dtocean-app?branch=master&svg=true)](https://ci.appveyor.com/project/DTOcean/dtocean-app)
[![codecov](https://codecov.io/gh/DTOcean/dtocean-app/branch/master/graph/badge.svg)](https://codecov.io/gh/DTOcean/dtocean-app)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/6466fab3dad14f0ea984ce2468bc0428)](https://www.codacy.com/gh/DTOcean/dtocean-app/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=DTOcean/dtocean-app&amp;utm_campaign=Badge_Grade)
[![release](https://img.shields.io/github/release/DTOcean/dtocean-app.svg)](https://github.com/DTOcean/dtocean-app/releases/latest)

**For the DTOcean wizard based installer please see the [dtocean](
https://github.com/DTOcean/dtocean) repository.**

# DTOcean Graphical Application

This repository contains the main graphical application of the DTOcean software 
tools. The code contained in this package is a Qt4 GUI view of the underlying 
model, provided by the [dtocean-core](https://github.com/DTOcean/dtocean-core) 
package. Related dtocean-* modules and themes are installed separately. 

Developers of DTOcean modules may wish to install this module, following the 
installation instructions below, and the source code of any other DTOcean 
module they wish to develop. In this way, the impact of changes can be observed 
in a graphical environment. 

\* For python 2.7 only.

## Documentation

See [dtocean.github.io](https://dtocean.github.io/) for the latest
documentation.

## Installation

Installation and development of dtocean-app uses the [Anaconda Distribution](
https://www.anaconda.com/distribution/) (Python 2.7)

### DTOcean Modules

Since version 2.0.0, dtocean-app is not dependent on installation of
dtocean design or assessment modules. This means a user could choose to use
dtocean-app for working with just one module, if desired.

Installation instructions for each desired module should be followed, although 
it is recommended to start by installing this module, or [dtocean-core](
https://github.com/DTOcean/dtocean-core), first if installing from source.

### Conda Package

It is recommended to install DTOcean into a dedicated conda environment, 
which can be configured to the needs of the system. To create an environment 
and configure it:

```
$ conda create -n _dtocean_app python=2.7
$ conda activate _dtocean_app
```

Download the [`.condarc`](
https://raw.githubusercontent.com/DTOcean/dtocean-app/master/.condarc) file 
for dtocean-app, save it and copy it to the root of the environment:

```
$ copy .condarc %CONDA_PREFIX%
```

Note that in PowerShell the copy command would be:

```
$ copy .condarc $env:CONDA_PREFIX
```


To install dtocean-app into the environment:

```
$ conda install dtocean-app=2.1.1
```

DTOcean modules for use with the GUI must be installed separately (See the 
README.md file of each module for installation instructions). For example:

```
$ conda install dtocean-electrical
```

To deactivate the conda environment:

```
$ conda deactivate
```

### Source Code

Conda can be used to install dependencies into a dedicated environment from
the source code root directory:

```
$ conda create -n _dtocean_app python=2.7 pip pyyaml
```

Activate the environment, then copy the `.condrc` file to store installation  
channels and pin critical packages to ensure stable installation of multiple 
DTOcean modules:

```
$ conda activate _dtocean_app
$ copy .condarc %CONDA_PREFIX%
```

Note that in PowerShell the copy command would be:

```
$ copy .condarc $env:CONDA_PREFIX
```

Install [polite](https://github.com/DTOcean/polite), [aneris](
https://github.com/DTOcean/aneris), [dtocean-core](
https://github.com/DTOcean/dtocean-core) and [dtocean-qt](
https://github.com/DTOcean/dtocean-qt) into the environment. For example, if 
installing them from source:

```
$ cd \\path\\to\\polite
$ conda install --file requirements-conda-dev.txt
$ pip install -e .

$ cd \\path\\to\\aneris
$ conda install --file requirements-conda-dev.txt
$ pip install -e .

$ cd \\path\\to\\dtocean-core
$ conda install --file requirements-conda-dev.txt
$ python setup.py bootstrap
$ pip install -e

$ cd \\path\\to\\dtocean-qt
$ conda install --file requirements-conda-dev.txt
$ pip install -e
``` 

Don't worry if some packages are marked for downgrade. It is safe to select
"y" each time you are asked by conda.

**Install any other required DTOcean packages at this point**. For instance,
to install all the design and assessment modules using conda packages:

```
$ conda install dtocean-hydrodynamics ^
                dtocean-electrical ^
                dtocean-moorings ^
                dtocean-installation ^
                dtocean-maintenance ^
                dtocean-economics ^
                dtocean-reliability ^
                dtocean-environment
```

Notes:

 * The above command will overwrite the source installed version of polite.
   To avoid this, install all required DTOcean packages from source, or
   uninstall the conda version of polite (`conda remove polite`) and reinstall 
   from source using pip.
 * Should you wish to develop any of the DTOcean modules, you should install 
   them from source, rather than using conda.
 * If using dtocean-hydrodynamics, you must also install the latest version of 
   the hydrodynamic data package (`dtocean-hydrodynamic-data-*.exe`). This can 
   be downloaded from the dtocean-hydrodynamics' [Releases](
   https://github.com/DTOcean/dtocean-hydrodynamics/releases) page. See the 
   [dtocean-hydrodynamics](https://github.com/DTOcean/dtocean-hydrodynamics) 
   repository for further information.
 * Inputs can be read from the DTOcean database, if installed. See the 
   [dtocean-database](https://github.com/DTOcean/dtocean-database) repository 
   for installation instructions.

Install the dtocean-app dependencies using conda:

```
$ cd \\path\\to\\dtocean-app
$ conda install --file requirements-conda-dev.txt
```

A "bootstrapping" stage is required to convert the QtDesigner files (located 
in the `designer` directory) to Python code:

```
$ python setup.py bootstrap
``` 

Finally, install dtocean-app using pip:

```
$ pip install -e .
```

To deactivate the conda environment:

```
$ conda deactivate
```

### Tests

A test suite is provided with the source code that uses [pytest](
https://docs.pytest.org).

If not already active, activate the conda environment set up in the [Source 
Code](#source-code) section:

```
$ conda activate _dtocean_app
```

Install pytest to the environment (one time only):

```
$ conda install -y mock "pytest>=3.6,<4" pytest-cov pytest-mock pytest-qt
```

Run the tests:

``` 
$ python -m pytest -v tests
```

Note, some tests require dtocean-hydrodynamics and dtocean-electrical to be 
installed and will be skipped if the modules are not found.

### Uninstall

To uninstall the conda package:

```
$ conda remove dtocean-app
```

To uninstall the source code and its conda environment:

```
$ conda remove --name _dtocean_app --all
```

## Usage

### Graphical Interface

The graphical interface is started from a [cmd](
https://en.wikipedia.org/wiki/Cmd.exe) window. Activate the conda environment 
first:

```
$ conda activate _dtocean_app
```

To start the GUI normally:

```
$ dtocean-app
```

To send all output to the cmd window (useful when crashes occur before logging 
is started) use "debug mode":

```
$ dtocean-app --debug
```

See the "Getting Started 1: Example Project" chapter of the [DTOcean 
documentation](https://dtocean.github.io/) for an example project.

### Command Line Tools

A utility is provided to copy user modifiable configuration files to the users 
"AppData" directory (on Windows). For instance the logging configuration can be 
modified once these files have been copied. To get help: 

```
$ dtocean-app-config -h
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to
discuss what you would like to change.

See [this blog post](
https://www.dataonlygreater.com/latest/professional/2017/03/09/dtocean-development-change-management/)
for information regarding development of the DTOcean ecosystem.

Please make sure to update tests as appropriate.

## Credits

This package was initially created as part of the [EU DTOcean project](
https://www.dtoceanplus.eu/About-DTOceanPlus/History) by:

*   Mathew Topper at [TECNALIA](https://www.tecnalia.com)
*   Vincenzo Nava at [TECNALIA](https://www.tecnalia.com)
*   Rui Duarte at [France Energies Marines](https://www.france-energies-marines.org/)

It is now maintained by Mathew Topper at [Data Only Greater](
https://www.dataonlygreater.com/).

## Licenses

### Software

[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)

### Icons

The icons used with the graphical interface are source directly or derived from
the following open source icon sets:

*   Crystal Clear ([LPGL-2.1](https://choosealicense.com/licenses/lgpl-2.1/))
*   GNOME ([GPL-2.0](https://choosealicense.com/licenses/gpl-2.0/))
*   ScreenRuler Tango ([GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/))
