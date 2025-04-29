[![dtocean-qt actions](https://github.com/DTOcean/dtocean/actions/workflows/dtocean-qt.yml/badge.svg?branch=next)](https://github.com/DTOcean/dtocean/actions/workflows/dtocean-qt.yml)
[![codecov](https://img.shields.io/codecov/c/gh/DTOcean/dtocean?token=Y3GR22fUJ8&flag=dtocean-qt)](https://app.codecov.io/gh/DTOcean/dtocean?flags%5B0%5D=dtocean-qt)

# dtocean-qt

PySide6 (Qt for Python) utilities for use within the DTOcean software suite.
Currently, only widgets and models for pandas (the data analysis / manipulation
library for Python) are available.

## Installation

Installation and development of dtocean-qt uses the
[Poetry](https://python-poetry.org/) dependency manager. Poetry must be
installed and available on the command line.

To install:

```sh
$ poetry install
```

## Tests

A test suite is provided with the source code that uses [pytest](https://docs.pytest.org).

Install the testing dependencies:

```sh
$ poetry install --with test
```

Run the tests:

```sh
$ poetry run pytest
```

## Usage

An example of a basic PySide6 widget for a pandas DataFrame. Begin by importing
the required functions and classes:

```python
>>> import pandas
>>> import numpy
>>> import sys
>>> from PySide6 import QtWidgets
>>> from dtocean_qt.pandas.excepthook import excepthook
>>> from dtocean_qt.pandas.models.DataFrameModel import DataFrameModel
>>> from dtocean_qt.pandas.views.DataTableView import DataTableWidget
>>> from dtocean_qt.pandas.views._ui import icons_rc

```

Redirect exceptions:

```python
>>> sys.excepthook = excepthook

```

Now set up a new empty DataFrame model:

```python
>>> model = DataFrameModel()
>>> model.freeze_first = True

```

Setup an application and create a data table widget:

```python
>>> app = QtWidgets.QApplication([])
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
>>> df
    A   B           C      D
0  10  20   Peter Pan   True
1  11  21   Cpt. Hook   True
2  12  22  Tinkerbell  False

```

Convert the column to the `numpy.int8` data type to test the delegates in the
table. `int8` is limited to -128-127:

```python
>>> df['A'] = df['A'].astype(numpy.int8)
>>> df['B'] = df['B'].astype(numpy.float16)
>>> df
    A     B           C      D
0  10  20.0   Peter Pan   True
1  11  21.0   Cpt. Hook   True
2  12  22.0  Tinkerbell  False

```

Fill the model with data:

```python
>>> model.setDataFrame(df)

```

Finally, start the app:

```python
>>> widget.show()
>>> app.exec() # doctest: +SKIP
```

You can find other examples in the *examples* folder of the source.

```sh
cd examples
python TestApp.py
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to
discuss what you would like to change. Please make sure to update tests as
appropriate.

## Credits

This package is a fork of the [pandas-qt](
https://github.com/datalyze-solutions/pandas-qt) project by Matthias Ludwig at
Datalyze Solutions. It was adapted for use in the [EU DTOcean project](
https://www.dtoceanplus.eu/About-DTOceanPlus/History) by Mathew Topper at
[TECNALIA](https://www.tecnalia.com).

It is now maintained by Mathew Topper at [Data Only Greater](
https://www.dataonlygreater.com/).

## License

[MIT](https://choosealicense.com/licenses/mit/)
