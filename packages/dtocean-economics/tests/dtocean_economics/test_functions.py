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


def test_get_discounted_values(bom):
    costs_df = costs_from_bom(bom)
    result = get_discounted_values(costs_df, 1 / 5)

    assert np.isclose(result.iloc[0], 331)


def test_get_lcoe():
    result = get_lcoe(np.array([1]), np.array([10]))
    assert np.isclose(result[0], 0.1)


def test_get_phase_breakdown(bom):
    result = get_phase_breakdown(bom)
    print(result)

    assert result is not None
    assert set(result.keys()) == set(["Test", "Other"])
    assert result["Test"] == 41.8
    assert result["Other"] == 364


def test_get_phase_breakdown_none(bom):
    none_bom = bom[pd.isnull(bom["phase"])]

    result = get_phase_breakdown(none_bom)

    assert result is None


def test_get_present_values():
    value = np.array([1, 6 / 5, 36 / 25, 216 / 125])
    year = np.array([0, 1, 2, 3])
    dr = 1 / 5
    expected = np.array([1, 1, 1, 1])

    result = get_present_values(value, year, dr)

    assert np.isclose(result, expected).all()
