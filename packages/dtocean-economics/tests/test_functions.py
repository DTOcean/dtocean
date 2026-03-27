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

from dtocean_economics.functions import (
    costs_from_bom,
    get_combined_lcoe,
    get_discounted_values,
    get_lcoe,
    get_phase_breakdown,
    get_present_values,
)


@pytest.mark.parametrize(
    "capex, opex, expected",
    [
        (1, None, 1),
        (None, 1, 1),
        (1, 1, 2),
    ],
)
def test_get_combined_lcoe_capex(capex, opex, expected):
    result = get_combined_lcoe(capex, opex)

    assert result == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (0.0, 200031),
        (0.1, 173580.34),
        (0.2, 152801),
    ],
)
def test_get_discounted_values(bom, test_input, expected):
    costs_df = costs_from_bom(bom)
    result = get_discounted_values(costs_df, test_input)

    assert np.isclose(result.iloc[0], expected)


def test_get_lcoe():
    result = get_lcoe(np.array([1]), np.array([10]))

    assert np.isclose(result[0], 0.1)


def test_get_phase_breakdown(bom):
    result = get_phase_breakdown(bom)

    assert result is not None
    assert set(result.keys()) == set(["Test", "Other"])
    assert result["Test"] == 31.0
    assert result["Other"] == 200000.0


def test_get_phase_breakdown_none(bom):
    none_bom = bom[pd.isnull(bom["phase"])]

    result = get_phase_breakdown(none_bom)

    assert result is None


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (0.0, [0, 10, 20]),
        (0.1, [0, 9.0909, 16.5289]),
        (0.2, [0, 8.3333, 13.8888]),
    ],
)
def test_get_present_values(test_input, expected):
    value = np.array([0, 10, 20])
    year = np.array([0, 1, 2])

    result = get_present_values(value, year, test_input)

    assert np.isclose(result, expected).all()
