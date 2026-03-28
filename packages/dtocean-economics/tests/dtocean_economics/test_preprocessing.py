# -*- coding: utf-8 -*-

#    Copyright (C) 2017-2026  Mathew Topper
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import pandas as pd
import pytest

from dtocean_economics.preprocessing import (
    estimate_cost_per_power,
    estimate_energy,
    estimate_opex,
    make_phase_bom,
)


def test_estimate_cost_per_power():
    df = estimate_cost_per_power(100, 1e6)
    series = df.iloc[0]

    assert len(df) == 1
    assert series["phase"] is None
    assert series["project_year"] == 0
    assert series["quantity"] == 1
    assert series["unitary_cost"] == 100 * 1e6


def test_estimate_cost_per_power_phase():
    df = estimate_cost_per_power(100, 1e6, "Devices")
    series = df.iloc[0]

    assert len(df) == 1
    assert series["phase"] == "Devices"


def test_estimate_energy():
    df = estimate_energy(2, 1e6, 0.95)
    year_one = df.loc[df["project_year"] == 0]
    other_years = df.loc[df["project_year"] != 0]

    assert (year_one["energy"] == 0.0).all()
    assert (other_years["energy"] == 0.95 * 1e6).all()


def test_estimate_opex_rated_power():
    df = estimate_opex(2, 100, 1e3)
    year_one = df.loc[df["project_year"] == 0]
    other_years = df.loc[df["project_year"] != 0]

    assert (year_one["costs"] == 0.0).all()
    assert (other_years["costs"] == 100 * 1e3).all()


def test_estimate_opex_mttf():
    df = estimate_opex(
        2, annual_repair_cost_estimate=1e3, annual_array_mttf_estimate=8766
    )

    year_one = df.loc[df["project_year"] == 0]
    other_years = df.loc[df["project_year"] != 0]

    assert (year_one["costs"] == 0.0).all()
    assert (other_years["costs"] == 1e3).all()


def test_estimate_opex_combined():
    df = estimate_opex(2, 100, 1e3, 1e3, 8766)

    year_one = df.loc[df["project_year"] == 0]
    other_years = df.loc[df["project_year"] != 0]

    assert (year_one["costs"] == 0.0).all()
    assert (other_years["costs"] == 100 * 1e3 + 1e3).all()


def test_make_phase_bom():
    df = make_phase_bom([0, 1, 2], [10, 20, 30], [0, 1, 2])

    assert (pd.isnull(df["phase"])).all()
    assert np.isclose(df["quantity"], [0, 1, 2]).all()
    assert np.isclose(df["unitary_cost"], [10, 20, 30]).all()
    assert np.isclose(df["project_year"], [0, 1, 2]).all()


def test_make_phase_bom_phase():
    df = make_phase_bom([0, 1, 2], [10, 20, 30], [0, 1, 2], "Test")

    assert (df["phase"] == "Test").all()


def test_make_phase_bom_phase_fail():
    with pytest.raises(ValueError):
        make_phase_bom([0, 1, 2], [10, 20, 30], [0, 1])
