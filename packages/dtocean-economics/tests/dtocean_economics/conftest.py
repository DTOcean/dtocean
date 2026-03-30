# -*- coding: utf-8 -*-
"""
Created on Tue Aug 08 12:36:48 2017

@author: mtopper
"""

import pandas as pd
import pytest

YEAR_ONE = 6 / 5
YEAR_TWO = 36 / 25
YEAR_THREE = 216 / 125


@pytest.fixture(scope="module")
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


@pytest.fixture(scope="module")
def energy_record():
    energy_dict = {
        "project_year": [0, 1, 2, 3],
        "energy 0": [1, YEAR_ONE, YEAR_TWO, YEAR_THREE],
        "energy 1": [10, YEAR_ONE * 10, YEAR_TWO * 10, YEAR_THREE * 10],
    }

    energy_df = pd.DataFrame(energy_dict)

    return energy_df


@pytest.fixture(scope="module")
def opex_costs():
    opex_dict = {
        "project_year": [0, 1, 2, 3],
        "cost 0": [1, YEAR_ONE, YEAR_TWO, YEAR_THREE],
        "cost 1": [10, YEAR_ONE * 10, YEAR_TWO * 10, YEAR_THREE * 10],
    }

    opex_df = pd.DataFrame(opex_dict)

    return opex_df
