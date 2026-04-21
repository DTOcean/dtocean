[![dtocean-economics actions](https://github.com/DTOcean/dtocean/actions/workflows/test-dtocean-economics.yml/badge.svg?branch=main)](https://github.com/DTOcean/dtocean/actions/workflows/test-dtocean-economics.yml)
[![codecov](https://img.shields.io/codecov/c/gh/DTOcean/dtocean?token=Y3GR22fUJ8&flag=dtocean-economics)](https://app.codecov.io/gh/DTOcean/dtocean?flags%5B0%5D=dtocean-economics)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dtocean-economics)

# dtocean-economics

The DTOcean Economics Module provides functions to assess and compare the
economic performance of arrays designed by DTOcean. It generates metrics such
as the levelised cost of energy (LCOE). The module can accept multiple
operational expenditure and energy production records to generate statistical
analysis.

Part of the [DTOcean](https://github.com/DTOcean/dtocean) suite of tools.

## Installation

```sh
pip install dtocean-economics
```

## Usage

An example of calculating the LCOE from a bill of materials, and two different
operational expenditure (OPEX) and energy histories.

Create the bill of materials first (in Euro):

```python
>>> import pandas as pd

>>> bom_dict = {'phase': ["One", "One", "One", "Two", "Two", "Two"],
...             'unitary_cost': [0.0, 100000.0, 100000.0, 1, 1, 1],
...             'project_year': [0, 1, 2, 0, 1, 2],
...             'quantity': [1, 1, 1, 1, 10, 20]}
>>> bom_df = pd.DataFrame(bom_dict, columns=["phase",
...                                          "project_year",
...                                          "quantity",
...                                          "unitary_cost"])
>>> bom_df
  phase  project_year  quantity  unitary_cost
0   One             0         1           0.0
1   One             1         1      100000.0
2   One             2         1      100000.0
3   Two             0         1           1.0
4   Two             1        10           1.0
5   Two             2        20           1.0

```

Now build two independent OPEX records (in Euro):

```python
>>> opex_dict = {'project_year': [0, 1, 2, 3, 4, 5],
...              'cost 0': [0.0, 100000.0, 100000.0, 1, 1, 1],
...              'cost 1': [0.0, 100000.0, 0, 1, 1, 100000.0]}
>>> opex_df = pd.DataFrame(opex_dict, columns=["project_year",
...                                            "cost 0",
...                                            "cost 1"])
>>> opex_df
   project_year    cost 0    cost 1
0             0       0.0       0.0
1             1  100000.0  100000.0
2             2  100000.0       0.0
3             3       1.0       1.0
4             4       1.0       1.0
5             5       1.0  100000.0

```

And the related energy production records (in Wh):

```python
>>> energy_dict = {'project_year': [0, 1, 2, 3, 4, 5],
...                'energy 0': [0, 1e6, 2e6, 0, 10e6, 20e6],
...                'energy 1': [0, 1e6, 32e6, 0, 0, 20e6]}
>>> energy_df = pd.DataFrame(energy_dict, columns=["project_year",
...                                                "energy 0",
...                                                "energy 1"])
>>> energy_df
   project_year    energy 0    energy 1
0             0         0.0         0.0
1             1   1000000.0   1000000.0
2             2   2000000.0  32000000.0
3             3         0.0         0.0
4             4  10000000.0         0.0
5             5  20000000.0  20000000.0

```

Process the inputs to calculate the discounted values:

```python
>>> from dtocean_economics import add_costs_to_bom, get_discounted_values
>>> discount_rate = 1 / 5
>>> add_costs_to_bom(bom_df, discount_rate)
>>> bom_df
  phase  project_year  quantity  unitary_cost     costs  discounted_costs
0   One             0         1           0.0       0.0          0.000000
1   One             1         1      100000.0  100000.0      83333.333333
2   One             2         1      100000.0  100000.0      69444.444444
3   Two             0         1           1.0       1.0          1.000000
4   Two             1        10           1.0      10.0          8.333333
5   Two             2        20           1.0      20.0         13.888889

>>> discounted_opex = get_discounted_values(opex_df, discount_rate)
>>> discounted_opex
0    152779.240612
1    123522.151492
dtype: float64

>>> discounted_energy = get_discounted_values(energy_df, discount_rate)
>>> discounted_energy
0    1.508230e+07
1    3.109311e+07
dtype: float64

```

Now calculate the mean of the LCOE (in Euro/kWh):

```python
>>> discounted_capex = bom_df['discounted_costs'].sum()
>>> discounted_costs = discounted_opex + discounted_capex
>>> lcoe = discounted_costs / discounted_energy * 1000
>>> lcoe
0    20.260845
1     8.886958
dtype: float64

>>> float(lcoe.mean())
14.573901960338254

```

## Development

Development of dtocean-economics uses the [Poetry](https://python-poetry.org/)
dependency manager. Poetry must be installed and available on the command line.

To install:

```sh
poetry install
```

## Tests

A test suite is provided with the source code that uses [pytest](https://docs.pytest.org).

Install the testing dependencies:

```sh
poetry install --with test
```

Additional tests are available for the plugins to [dtocean-core]. Enable these
tests by installing the `test-extras` group:

```sh
poetry install --with test --with test-extras
```

Run the tests:

```sh
poetry run pytest
```

Code quality can also be audited using the [ruff](https://docs.astral.sh/ruff/)
and [pyright](https://github.com/microsoft/pyright) tools. Install the
dependencies:

```sh
poetry install --with audit
```

Run the audit:

```sh
poetry run ruff
poetry run pyright src
```

The above tests can be run across all compatible Python versions using
[tox](https://tox.wiki/) and [tox-uv](https://github.com/tox-dev/tox-uv). To
install:

```sh
poetry install --with test --with test-extras --with audit --with tox
```

To run the tests:

```sh
poetry run tox
```

## Contributing

Please see the [dtocean](https://github.com/DTOcean/dtocean) GitHub repository
for contributing guidelines.

[dtocean-core]: https://pypi.org/project/dtocean-core/

## Credits

This package was initially created as part of the [EU DTOcean project](https://cordis.europa.eu/project/id/608597) by:

- Mathew Topper at [TECNALIA](https://www.tecnalia.com)
- Marta Silva at [WavEC](https://www.wavec.org/)

It is now maintained by Mathew Topper at [Data Only Greater](https://www.dataonlygreater.com/).

## License

[GPL-3.0](https://choosealicense.com/licenses/gpl-3.0/)
