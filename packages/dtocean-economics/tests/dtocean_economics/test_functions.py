# -*- coding: utf-8 -*-

#    Copyright (C) 2017-2026 Mathew Topper
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

from dtocean_economics import (
    add_costs_to_bom,
    get_discounted_values,
    get_phase_breakdown,
    get_present_values,
)

YEAR_ONE = 6 / 5
YEAR_TWO = 36 / 25
YEAR_THREE = 216 / 125


@pytest.fixture()
def bom():
    bom_dict = {
        "phase": [None, None, None, "Test", "Test", "Test"],
        "unitary_cost": [
            100,
            YEAR_ONE * 100,
            YEAR_TWO * 100,
            1,
            YEAR_ONE,
            YEAR_TWO,
        ],
        "project_year": [0, 1, 2, 0, 1, 2],
        "quantity": [1, 1, 1, 1, 10, 20],
    }

    bom_df = pd.DataFrame(bom_dict)

    return bom_df


def test_add_costs_to_bom(bom):
    add_costs_to_bom(bom)
    assert (bom["costs"] == bom["unitary_cost"] * bom["quantity"]).all()


def test_add_costs_to_bom_discounted(bom):
    add_costs_to_bom(bom, 1 / 5)
    assert bom["discounted_costs"].sum() == 3 * 100 + 31 * 1


def test_get_discounted_values(bom):
    add_costs_to_bom(bom)
    costs_df = bom[["project_year", "costs"]]
    result = get_discounted_values(costs_df, 1 / 5)

    assert np.isclose(result.iloc[0], 331)


def test_get_phase_breakdown(bom):
    add_costs_to_bom(bom)
    result = get_phase_breakdown(bom)

    assert result is not None
    assert set(result.index.values) == set(["Test", "Other"])

    test = result.loc["Test"]
    assert isinstance(test, pd.Series)
    assert test["costs"] == 41.8

    other = result.loc["Other"]
    assert isinstance(other, pd.Series)
    assert other["costs"] == 364

    assert "unitary_cost" not in result


def test_get_phase_breakdown_none(bom):
    none_bom = bom[pd.isnull(bom["phase"])]
    add_costs_to_bom(none_bom)
    result = get_phase_breakdown(none_bom)
    assert result is None


def test_get_phase_breakdown_no_costs():
    result = get_phase_breakdown(pd.DataFrame())
    assert result is None


def test_get_present_values():
    value = np.array([1, 6 / 5, 36 / 25, 216 / 125])
    year = np.array([0, 1, 2, 3])
    dr = 1 / 5
    expected = np.array([1, 1, 1, 1])

    result = get_present_values(value, year, dr)

    assert np.isclose(result, expected).all()
