# -*- coding: utf-8 -*-

#    Copyright (C) 2016  Marta Silva, Mathew Topper
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


def add_costs_to_bom(bom, discount_rate=None):
    costs = bom["quantity"] * bom["unitary_cost"]
    bom["costs"] = costs

    if discount_rate is None:
        return

    present_values = get_present_values(
        costs.to_numpy(),
        bom["project_year"].to_numpy(),
        discount_rate,
    )

    bom["discounted_costs"] = present_values


def get_discounted_values(values_df: pd.DataFrame, discount_rate: float):
    years = values_df["project_year"]
    values_df = values_df.set_index("project_year")
    discounted_values = []

    for _, value_series in values_df.items():
        present_values = get_present_values(
            value_series.to_numpy(),
            years.to_numpy(),
            discount_rate,
        )
        discounted_value = present_values.sum()
        discounted_values.append(discounted_value)

    return pd.Series(discounted_values)


def get_phase_breakdown(bom: pd.DataFrame):
    if "costs" not in bom.keys():
        return

    # Check for null phases
    null_phases = pd.isnull(bom["phase"])

    # No breakdown available
    if null_phases.all():
        return

    # Replace any null phase values
    bom.loc[pd.isnull(bom["phase"]), "phase"] = "Other"
    phase_groups = bom.groupby("phase")

    phase_breakdown = phase_groups.sum()
    if "unitary_costs" in phase_breakdown:
        phase_breakdown.drop("unitary_costs", axis=1, inplace=True)

    return phase_breakdown


def get_present_values(value: np.ndarray, yr: np.ndarray, dr: float):
    """
    Function to calculate present value
    It should be applied to a table with costs and year cost occurs, and to
      energy output table
    Costs could be calculated with the above function.
    It can be applied in an item by item basis, or on the sum by year
    """
    return value / ((1 + dr) ** yr)
