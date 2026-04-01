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

from typing import Optional

import pandas as pd

from .main import main


def costs_from_bom(bom):
    costs = bom["quantity"] * bom["unitary_cost"]
    costs_dict = {"project_year": bom["project_year"].values, "costs": costs}
    return pd.DataFrame(costs_dict)


def get_discounted_values(values_df: pd.DataFrame, discount_rate):
    years = values_df["project_year"]
    values_df = values_df.set_index("project_year")

    discounted_values = []

    for _, value_series in values_df.items():
        present_values = get_present_values(value_series, years, discount_rate)
        discounted_value = present_values.sum()
        discounted_values.append(discounted_value)

    return pd.Series(discounted_values)


def get_phase_breakdown(bom):
    # Check for null phases
    null_phases = pd.isnull(bom["phase"])

    # No breakdown available
    if null_phases.all():
        return None

    # Replace any null phase values
    bom.loc[pd.isnull(bom["phase"]), "phase"] = "Other"

    phase_groups = bom.groupby("phase")

    phase_breakdown = {}

    for phase_name, phase_bom in phase_groups:
        phase_cost = get_total_cost(phase_bom)
        phase_breakdown[phase_name] = phase_cost

    return phase_breakdown


def get_present_values(value, yr, dr):
    """
    Function to calculate present value
    It should be applied to a table with costs and year cost occurs, and to
      energy output table
    Costs could be calculated with the above function.
    It can be applied in an item by item basis, or on the sum by year
    """
    return value / ((1 + dr) ** yr)


def get_total_cost(bom):
    return (bom["unitary_cost"] * bom["quantity"]).sum()


def get_metrics_table(
    opex_bom: pd.DataFrame,
    energy_record: pd.DataFrame,
) -> Optional[pd.DataFrame]:
    # Build metrics table if possible
    n_rows = None

    if not opex_bom.empty:
        n_rows = len(opex_bom.columns) - 1
    elif not energy_record.empty:
        n_rows = len(energy_record.columns) - 1
    else:
        return

    table_cols_and_conversion = [
        ("LCOE", 1e-3),  # from Euro/Wh to Euro/kWh
        ("LCOE CAPEX", 1e-3),  # from Euro/Wh to Euro/kWh
        ("LCOE OPEX", 1e-3),  # from Euro/Wh to Euro/kWh
        ("OPEX", 1),
        ("Energy", 1e-6),  # from Wh to MWh
        ("Discounted OPEX", 1),
        ("Discounted Energy", 1e-6),  # from Wh to MWh
    ]

    metrics_dict = {}

    for col_name, factor in table_cols_and_conversion:
        col_result = result[col_name]
        if col_result is not None:
            values = col_result.values * factor
        else:
            values = [None] * n_rows

        metrics_dict[col_name] = values

    return pd.DataFrame(metrics_dict)
