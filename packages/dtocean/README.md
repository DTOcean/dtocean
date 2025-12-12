[![dtocean actions](https://github.com/DTOcean/dtocean/actions/workflows/dtocean.yml/badge.svg?branch=next)](https://github.com/DTOcean/dtocean/actions/workflows/dtocean.yml)
[![codecov](https://img.shields.io/codecov/c/gh/DTOcean/dtocean?token=Y3GR22fUJ8&flag=dtocean)](https://app.codecov.io/gh/DTOcean/dtocean?flags%5B0%5D=dtocean)

# DTOcean

**DTOcean is an open-source tool for design and techno-economic assessment of
marine renewable energy arrays.**

DTOcean can calculate:

- Optimal ocean energy converter (OEC) positioning
- Energy export infrastructure
- Station keeping requirements based on OEC performance and site conditions
- Installation planning with weather effects
- Maintenance planning, simulating OEC downtime
- Environmental impact assessment (experimental)

And features include:

- A unique statistical approach to calculating levelized cost of energy (LCOE)
- OEC reliability influenced at component level
- Graphical user interface
- Persistent database
- Wizard based installation (for Windows)

This is a meta-package for installing the entire DTOcean suite, including
the GUI, design and assessment module and offline documentation.

## Installation

Install the DTOcean suite of packages using pip:

```console
pip install dtocean
```

## Usage

Open the DTOcean GUI from a command prompt:

```console
dtocean app
```

See the [dtocean-app](https://github.com/DTOcean/dtocean/tree/next/packages/dtocean-app)
documentation for additional options.

## Documentation

See [https://dtocean.github.io/dtocean](https://dtocean.github.io//dtocean) for
the latest documentation.

## Credits

Copyright 2016-2025 The DTOcean Developers

This version of DTOcean is maintained by Mathew Topper at [Data
Only Greater](https://www.dataonlygreater.com/) as a continuation of the
[EU FP7 DTOcean project](https://cordis.europa.eu/project/id/608597).

Also, please check out the [EU H2020 DTOceanPlus project](https://cinea.ec.europa.eu/featured-projects/dtoceanplus_en),
which expanded the scope of the DTOcean tools. The source code for DTOceanPlus is
available [here](https://gitlab.com/dtoceanplus).
