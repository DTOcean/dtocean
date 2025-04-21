[![appveyor](https://ci.appveyor.com/api/projects/status/github/DTOcean/dtocean-qt?branch=master&svg=true)](https://ci.appveyor.com/project/DTOcean/dtocean-qt)
[![codecov](https://codecov.io/gh/DTOcean/dtocean-qt/branch/master/graph/badge.svg)](https://codecov.io/gh/DTOcean/dtocean-qt)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/7349c8189d9d4466a46cb8dffd94d418)](https://www.codacy.com/gh/DTOcean/dtocean-qt/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=DTOcean/dtocean-qt&amp;utm_campaign=Badge_Grade)
[![release](https://img.shields.io/github/release/DTOcean/dtocean-qt.svg)](https://github.com/DTOcean/dtocean-qt/releases/latest)

# dtocean-qt

Utilities to use pandas (the data analysis / manipulation library for Python)
with Qt within the DTOcean software suite. This package is a dependency of 
[dtocean-app](https://github.com/DTOcean/dtocean-app).

\* For python 2.7 only.

## Installation

Installation and development of dtocean-qt uses the [Anaconda 
Distribution](https://www.anaconda.com/distribution/) (Python 2.7)

### Conda Package

To install:

```
$ conda install -c dataonlygreater dtocean-qt
```

### Source Code

Conda can be used to install dependencies into a dedicated environment from
the source code root directory:

```
$ conda create -n _dtocean_qt python=2.7 pip pyyaml
```

Activate the environment, then copy the `.condrc` file to store installation  
channels:

```
$ conda activate _dtocean_qt
$ copy .condarc %CONDA_PREFIX%
```

Install dtocean-qt and its dependencies using conda and pip:

```
$ conda install --file requirements-conda-dev.txt
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
$ conda activate _dtocean_qt
```

Install packages required for testing to the environment (one time only):

```
$ conda install -y -c conda-forge "pytest<4" pytest-qt
```

Run the tests:

``` 
$ py.test tests
```

### Uninstall

To uninstall the conda package:

```
$ conda remove dtocean-qt
```

To uninstall the source code and its conda environment:

```
$ conda remove --name _dtocean_qt --all
```

## Usage

An example of a basic PyQt4 widget for a pandas DataFrame.

Import the required modules. Redirect exceptions and use `QtGui` from the 
`compat` module to take care if correct sip version, etc:

```python
>>> import pandas
>>> import numpy
>>> import sys
>>> from dtocean_qt.excepthook import excepthook
>>> sys.excepthook = excepthook

>>> from dtocean_qt.compat import QtGui
>>> from dtocean_qt.models.DataFrameModel import DataFrameModel
>>> from dtocean_qt.views.DataTableView import DataTableWidget
>>> from dtocean_qt.views._ui import icons_rc
```

Now set up a new empty DataFrame model:

```python
>>> model = DataFrameModel()
>>> model.freeze_first = True
```

Setup an application and create a data table widget:

```python
>>> app = QtGui.QApplication([])
>>> widget = DataTableWidget()
>>> widget.resize(800, 600)
>>> widget.hideVerticalHeader(True)
```

Assign the created model to the widget:

```python
>>> widget.setViewModel(model)
```

Now create some test data:

```python
>>> data = {
...    'A': [10, 11, 12], 
...    'B': [20, 21, 22], 
...    'C': ['Peter Pan', 'Cpt. Hook', 'Tinkerbell'],
...    'D': [True, True, False]}
>>> df = pandas.DataFrame(data)
```

Convert the column to the `numpy.int8` data type to test the delegates in the
table. `int8` is limited to -128-127:

```python
>>> df['A'] = df['A'].astype(numpy.int8)
>>> df['B'] = df['B'].astype(numpy.float16)
```

Fill the model with data:

```python
>>> model.setDataFrame(df)
```

Finally, start the app:

```python
>>> widget.show(); app.exec_()
```

You can find other examples in the *examples* folder of the source.

```
$ cd examples
$ python TestApp.py
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to
discuss what you would like to change.

See [this blog post](
https://www.dataonlygreater.com/latest/professional/2017/03/09/dtocean-development-change-management/)
for information regarding development of the DTOcean ecosystem.

Please make sure to update tests as appropriate.

## Credits

This package is a fork of the (now superseded) [pandas-qt](
https://github.com/datalyze-solutions/pandas-qt) project by Matthias Ludwig at 
Datalyze Solutions. It was adapted for use in the [EU DTOcean project](
https://www.dtoceanplus.eu/About-DTOceanPlus/History) by Mathew Topper at 
[TECNALIA](https://www.tecnalia.com).

It is now maintained by Mathew Topper at [Data Only Greater](
https://www.dataonlygreater.com/).

## License

[MIT](https://choosealicense.com/licenses/mit/)
