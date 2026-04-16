# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2026 Mathew Topper
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

"""
This module contains the package interface to the dtocean economics functions.

Note:
  The function decorators (such as "@classmethod", etc) must not be removed.

.. module:: economics
   :platform: Windows
   :synopsis: Aneris interface for dtocean_core package

.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

from typing import Any, Optional

import numpy as np
import pandas as pd

from dtocean_economics import (
    add_costs_to_bom,
    get_discounted_values,
    get_phase_breakdown,
    get_total_cost,
)
from dtocean_economics.preprocessing import (
    estimate_cost_per_power,
    estimate_energy,
    estimate_opex,
    make_phase_bom,
)
from dtocean_economics.stats import (
    BiVariateKDE,
    UniVariateKDE,
    pdf_confidence_densities,
    pdf_contour_coords,
)
from dtocean_plugins.themes.base import ThemeInterface


class EconomicInterface(ThemeInterface):
    """Interface to the economics thematic functions."""

    def __init__(self):
        super(EconomicInterface, self).__init__()

    @classmethod
    def get_name(cls):
        """A class method for the common name of the interface.

        Returns:
          str: A unique string
        """

        return "Economics"

    @classmethod
    def declare_weight(cls):
        return 1

    @classmethod
    def declare_inputs(cls):
        """A class method to declare all the variables required as inputs by
        this interface.

        Returns:
          list: List of inputs identifiers

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the data descriptions. For example::

              inputs = ["My:first:variable",
                        "My:second:variable",
                       ]
        """

        input_list = [
            "device.system_cost",
            "project.lifetime",
            "project.discount_rate",
            "project.number_of_devices",
            "project.electrical_economics_data",
            "project.moorings_foundations_economics_data",
            "project.installation_economics_data",
            "project.capex_oandm",
            "project.opex_per_year",
            "project.energy_per_year",
            "project.electrical_network_efficiency",
            "project.externalities_capex",
            "project.externalities_opex",
            "project.electrical_cost_estimate",
            "project.moorings_cost_estimate",
            "project.installation_cost_estimate",
            "project.opex_estimate",
            "project.annual_repair_cost_estimate",
            "project.annual_array_mttf_estimate",
            "project.electrical_network_efficiency",
            "project.annual_energy",
            "project.estimate_energy_record",
        ]

        return input_list

    @classmethod
    def declare_outputs(cls):
        """A class method to declare all the output variables provided by
        this interface.

        Returns:
          list: List of output identifiers

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the data descriptions. For example::

              outputs = ["My:first:variable",
                         "My:third:variable",
                        ]
        """

        output_list = [
            "project.economics_metrics",
            "project.lcoe_mode",
            "project.lcoe_interval_lower",
            "project.lcoe_interval_upper",
            "project.lcoe_mean",
            "project.capex_total",
            "project.capex_without_externalities",
            "project.discounted_capex",
            "project.lifetime_opex_mean",
            "project.lifetime_opex_mode",
            "project.lifetime_opex_interval_lower",
            "project.lifetime_opex_interval_upper",
            "project.discounted_opex_mode",
            "project.discounted_opex_mean",
            "project.discounted_opex_interval_lower",
            "project.discounted_opex_interval_upper",
            "project.lifetime_cost_mean",
            "project.lifetime_cost_mode",
            "project.discounted_lifetime_cost_mean",
            "project.discounted_lifetime_cost_mode",
            "project.discounted_energy_mode",
            "project.discounted_energy_mean",
            "project.discounted_energy_interval_lower",
            "project.discounted_energy_interval_upper",
            "project.lcoe_breakdown",
            "project.capex_lcoe_breakdown",
            "project.opex_lcoe_breakdown",
            "project.cost_breakdown",
            "project.capex_breakdown",
            "project.opex_breakdown",
            "project.confidence_density",
            "project.lcoe_pdf",
        ]

        return output_list

    @classmethod
    def declare_optional(cls):
        """A class method to declare all the variables which should be flagged
        as optional.

        Returns:
          list: List of optional variable identifiers

        Note:
          Currently only inputs marked as optional have any logical effect.
          However, this may change in future releases hence the general
          approach.

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the declare_inputs output. For example::

              optional = ["My:first:variable",
                         ]
        """

        optional = [
            "device.system_cost",
            "project.number_of_devices",
            "project.electrical_network_efficiency",
            "project.electrical_economics_data",
            "project.moorings_foundations_economics_data",
            "project.installation_economics_data",
            "project.opex_per_year",
            "project.energy_per_year",
            "project.capex_oandm",
            "project.lifetime",
            "project.discount_rate",
            "project.externalities_capex",
            "project.externalities_opex",
            "project.electrical_cost_estimate",
            "project.moorings_cost_estimate",
            "project.installation_cost_estimate",
            "project.opex_estimate",
            "project.annual_repair_cost_estimate",
            "project.annual_array_mttf_estimate",
            "project.annual_energy",
            "project.estimate_energy_record",
        ]

        return optional

    @classmethod
    def declare_id_map(cls):
        """Declare the mapping for variable identifiers in the data description
        to local names for use in the interface. This helps isolate changes in
        the data description or interface from effecting the other.

        Returns:
          dict: Mapping of local to data description variable identifiers

        Example:
          The returned value must be a dictionary containing all the inputs and
          outputs from the data description and a local alias string. For
          example::

              id_map = {"var1": "My:first:variable",
                        "var2": "My:second:variable",
                        "var3": "My:third:variable"
                       }

        """

        id_map = {
            "device_cost": "device.system_cost",
            "annual_energy": "project.annual_energy",
            "n_devices": "project.number_of_devices",
            "discount_rate": "project.discount_rate",
            "electrical_bom": "project.electrical_economics_data",
            "moorings_bom": "project.moorings_foundations_economics_data",
            "installation_bom": "project.installation_economics_data",
            "capex_oandm": "project.capex_oandm",
            "opex_per_year": "project.opex_per_year",
            "energy_per_year": "project.energy_per_year",
            "lifetime_opex_mean": "project.lifetime_opex_mean",
            "lifetime_opex_mode": "project.lifetime_opex_mode",
            "lifetime_opex_lower": "project.lifetime_opex_interval_lower",
            "lifetime_opex_upper": "project.lifetime_opex_interval_upper",
            "network_efficiency": "project.electrical_network_efficiency",
            "externalities_capex": "project.externalities_capex",
            "externalities_opex": "project.externalities_opex",
            "lifetime": "project.lifetime",
            "electrical_estimate": "project.electrical_cost_estimate",
            "moorings_estimate": "project.moorings_cost_estimate",
            "install_estimate": "project.installation_cost_estimate",
            "opex_estimate": "project.opex_estimate",
            "annual_repair_cost_estimate": "project.annual_repair_cost_estimate",
            "annual_array_mttf_estimate": "project.annual_array_mttf_estimate",
            "estimate_energy_record": "project.estimate_energy_record",
            "economics_metrics": "project.economics_metrics",
            "lcoe_mean": "project.lcoe_mean",
            "lcoe_mode": "project.lcoe_mode",
            "lcoe_lower": "project.lcoe_interval_lower",
            "lcoe_upper": "project.lcoe_interval_upper",
            "discounted_opex_mean": "project.discounted_opex_mean",
            "discounted_opex_mode": "project.discounted_opex_mode",
            "discounted_opex_lower": "project.discounted_opex_interval_lower",
            "discounted_opex_upper": "project.discounted_opex_interval_upper",
            "discounted_energy_mean": "project.discounted_energy_mean",
            "discounted_energy_mode": "project.discounted_energy_mode",
            "discounted_energy_lower": "project.discounted_energy_interval_lower",
            "discounted_energy_upper": "project.discounted_energy_interval_upper",
            "capex_total": "project.capex_total",
            "capex_no_externalities": "project.capex_without_externalities",
            "discounted_capex": "project.discounted_capex",
            "lifetime_cost_mean": "project.lifetime_cost_mean",
            "lifetime_cost_mode": "project.lifetime_cost_mode",
            "discounted_lifetime_cost_mean": "project.discounted_lifetime_cost_mean",
            "discounted_lifetime_cost_mode": "project.discounted_lifetime_cost_mode",
            "cost_breakdown": "project.cost_breakdown",
            "capex_breakdown": "project.capex_breakdown",
            "capex_lcoe_breakdown": "project.capex_lcoe_breakdown",
            "opex_breakdown": "project.opex_breakdown",
            "opex_lcoe_breakdown": "project.opex_lcoe_breakdown",
            "lcoe_breakdown": "project.lcoe_breakdown",
            "confidence_density": "project.confidence_density",
            "lcoe_pdf": "project.lcoe_pdf",
        }

        return id_map

    def connect(self, debug_entry=False):
        """The connect method is used to execute the external program and
        populate the interface data store with values.

        Note:
          Collecting data from the interface for use in the external program
          can be accessed using self.data.my_input_variable. To put new values
          into the interface once the program has run we set
          self.data.my_output_variable = value

        """

        bom_cols = ["phase", "quantity", "unitary_cost", "project_year"]

        # CAPEX Dataframes
        device_bom = pd.DataFrame(columns=bom_cols)
        electrical_bom = pd.DataFrame(columns=bom_cols)
        moorings_bom = pd.DataFrame(columns=bom_cols)
        installation_bom = pd.DataFrame(columns=bom_cols)
        capex_oandm_bom = pd.DataFrame(columns=bom_cols)
        externalities_bom = pd.DataFrame(columns=bom_cols)

        opex_bom = pd.DataFrame()
        energy_record = pd.DataFrame()

        # Prepare costs
        if (
            self.data.n_devices is not None
            and self.data.device_cost is not None
        ):
            quantities = [self.data.n_devices]
            costs = [self.data.device_cost]
            years = [0]

            device_bom = make_phase_bom(quantities, costs, years, "Devices")

        # Patch double counting of umbilical
        if (
            self.data.electrical_bom is not None
            and self.data.moorings_bom is not None
        ):
            # Remove matching identifiers from electrical bom
            unique = list(set(self.data.moorings_bom["Key Identifier"]))

            matching = self.data.electrical_bom["Key Identifier"].isin(unique)
            self.data.electrical_bom = self.data.electrical_bom[~matching]

        if self.data.electrical_bom is not None:
            electrical_bom = self.data.electrical_bom.drop(
                "Key Identifier", axis=1
            )

            name_map = {
                "Quantity": "quantity",
                "Cost": "unitary_cost",
                "Year": "project_year",
            }

            electrical_bom = electrical_bom.rename(columns=name_map)
            electrical_bom["phase"] = "Electrical Sub-Systems"

        elif self.data.electrical_estimate is not None:
            electrical_bom = estimate_cost_per_power(
                1, self.data.electrical_estimate, "Electrical Sub-Systems"
            )

        if self.data.moorings_bom is not None:
            moorings_bom = self.data.moorings_bom.drop("Key Identifier", axis=1)

            name_map = {
                "Quantity": "quantity",
                "Cost": "unitary_cost",
                "Year": "project_year",
            }

            moorings_bom = moorings_bom.rename(columns=name_map)
            moorings_bom["phase"] = "Mooring and Foundations"

        elif self.data.moorings_estimate is not None:
            moorings_bom = estimate_cost_per_power(
                1, self.data.moorings_estimate, "Mooring and Foundations"
            )

        if self.data.installation_bom is not None:
            installation_bom = self.data.installation_bom.drop(
                "Key Identifier", axis=1
            )

            name_map = {
                "Quantity": "quantity",
                "Cost": "unitary_cost",
                "Year": "project_year",
            }

            installation_bom = installation_bom.rename(columns=name_map)
            installation_bom["phase"] = "Installation"

        elif self.data.install_estimate is not None:
            installation_bom = estimate_cost_per_power(
                1, self.data.install_estimate, "Installation"
            )

        if self.data.capex_oandm is not None:
            quantities = [1]
            costs = [self.data.capex_oandm]
            years = [0]

            capex_oandm_bom = make_phase_bom(
                quantities, costs, years, "Condition Monitoring"
            )

        if self.data.externalities_capex is not None:
            quantities = [1]
            costs = [self.data.externalities_capex]
            years = [0]

            externalities_bom = make_phase_bom(
                quantities, costs, years, "Externalities"
            )

        # Combine the capex dataframes
        capex_bom = pd.concat(
            [
                device_bom,
                electrical_bom,
                moorings_bom,
                installation_bom,
                capex_oandm_bom,
                externalities_bom,
            ],
            ignore_index=True,
            sort=False,
        )
        capex_bom = capex_bom.convert_dtypes()

        if self.data.opex_per_year is not None:
            opex_bom = self.data.opex_per_year.copy()
            opex_bom.index.name = "project_year"
            opex_bom = opex_bom.reset_index()

        elif self.data.lifetime is not None and (
            self.data.opex_estimate is not None
            or (
                self.data.annual_repair_cost_estimate is not None
                and self.data.annual_array_mttf_estimate is not None
            )
        ):
            opex_bom = estimate_opex(
                self.data.lifetime,
                1,
                self.data.opex_estimate,
                self.data.annual_repair_cost_estimate,
                self.data.annual_array_mttf_estimate,
            )

        # Add OPEX externalities
        if not opex_bom.empty and self.data.externalities_opex is not None:
            opex_bom = opex_bom.set_index("project_year")
            opex_bom += self.data.externalities_opex
            opex_bom = opex_bom.reset_index()

        # Prepare energy
        if self.data.network_efficiency is not None:
            net_coeff = self.data.network_efficiency
        else:
            net_coeff = 1

        # Convert energy to Wh
        MWh_to_Wh = 1e6

        if self.data.energy_per_year is not None:  #
            energy_record = self.data.energy_per_year.copy() * MWh_to_Wh
            energy_record = energy_record * net_coeff
            energy_record.index.name = "project_year"
            energy_record = energy_record.reset_index()

        elif (
            self.data.estimate_energy_record
            and self.data.lifetime is not None
            and self.data.annual_energy is not None
        ):
            annual_energy = self.data.annual_energy * MWh_to_Wh
            energy_record = estimate_energy(
                self.data.lifetime,
                annual_energy,
                net_coeff,
            )

        if debug_entry:
            return

        outputs = _get_outputs(
            capex_bom,
            opex_bom,
            energy_record,
            self.data.discount_rate,
            self.data.externalities_capex,
            self.data.externalities_opex,
        )

        for k, v in outputs.items():
            self.data[k] = v


def _get_outputs(
    capex_bom: pd.DataFrame,
    opex_bom: pd.DataFrame,
    energy_record: pd.DataFrame,
    discount_rate: float,
    externalities_capex: Optional[float],
    externalities_opex: Optional[float],
) -> dict[str, Any]:
    series = [opex_bom, energy_record]
    series_lengths = [len(x) for x in series if not x.empty]
    if len(set(series_lengths)) != 1:
        msg = "opex bom and energy record must be the same length if not empty"
        raise ValueError(msg)

    outputs: dict[str, Any] = {
        "capex_breakdown": None,
        "capex_total": None,
        "discounted_capex": None,
        "capex_no_externalities": None,
        "economics_metrics": None,
        "lifetime_opex_mean": None,
        "lifetime_opex_mode": None,
        "lifetime_opex_lower": None,
        "lifetime_opex_upper": None,
        "discounted_opex_mean": None,
        "discounted_opex_mode": None,
        "discounted_opex_lower": None,
        "discounted_opex_upper": None,
        "discounted_energy_mean": None,
        "discounted_energy_mode": None,
        "discounted_energy_lower": None,
        "discounted_energy_upper": None,
        "lcoe_mean": None,
        "lcoe_mode": None,
        "lcoe_lower": None,
        "lcoe_upper": None,
        "lcoe_pdf": None,
        "confidence_density": None,
        "lifetime_cost_mean": None,
        "lifetime_cost_mode": None,
        "discounted_lifetime_cost_mean": None,
        "discounted_lifetime_cost_mode": None,
        "cost_breakdown": None,
        "opex_breakdown": None,
        "capex_lcoe_breakdown": None,
        "opex_lcoe_breakdown": None,
        "lcoe_breakdown": None,
    }

    capex_total = 0
    discounted_capex_total = 0
    phase_breakdown = None
    discounted_capex = None
    discounted_opex = None
    lcoe_capex = None
    lcoe_opex = None
    lcoe_total = None

    if not capex_bom.empty:
        add_costs_to_bom(capex_bom, discount_rate)
        costs_df = capex_bom[["project_year", "costs"]]

        discounted_capex = get_discounted_values(
            costs_df,
            discount_rate,
        )

        discounted_capex_total = discounted_capex.iloc[0]
        capex_total = get_total_cost(capex_bom)
        phase_breakdown = get_phase_breakdown(capex_bom)
        assert phase_breakdown is not None
        capex_breakdown = {k: v["costs"] for k, v in phase_breakdown.iterrows()}

        outputs["capex_total"] = capex_total
        outputs["capex_breakdown"] = capex_breakdown
        outputs["discounted_capex"] = discounted_capex_total

        if externalities_capex is not None:
            outputs["capex_no_externalities"] = (
                capex_total - externalities_capex
            )

    if not opex_bom.empty:
        opex_by_year = opex_bom.set_index("project_year")
        opex_total = opex_by_year.sum()
        discounted_opex = get_discounted_values(opex_bom, discount_rate)

    if not energy_record.empty:
        energy_by_year = energy_record.set_index("project_year")
        energy_total = energy_by_year.sum()
        discounted_energy = get_discounted_values(energy_record, discount_rate)

        if discounted_capex is not None:
            lcoe_capex = discounted_capex_total / discounted_energy
            lcoe_total = lcoe_capex.copy()

        if discounted_opex is not None:
            lcoe_opex = discounted_opex / discounted_energy
            if lcoe_total is None:
                lcoe_total = lcoe_opex
            else:
                lcoe_total += lcoe_opex

    metrics_table = _get_metrics_table(
        opex_total,
        discounted_opex,
        energy_total,
        discounted_energy,
        lcoe_capex,
        lcoe_opex,
        lcoe_total,
    )

    if metrics_table is None:
        return outputs

    outputs["economics_metrics"] = metrics_table
    outputs.update(
        _get_outputs_stats(
            metrics_table,
            opex_total,
            discounted_opex,
            discounted_energy,
            lcoe_total,
            discounted_capex_total,
        )
    )

    # Calculate total costs
    if not capex_bom.empty or outputs["lifetime_opex_mean"] is not None:
        lifetime_cost_mean = capex_total

        if outputs["lifetime_opex_mean"] is not None:
            lifetime_cost_mean += outputs["lifetime_opex_mean"]

        outputs["lifetime_cost_mean"] = lifetime_cost_mean

    if not capex_bom.empty and outputs["lifetime_opex_mode"] is not None:
        lifetime_cost_mode = capex_total

        if outputs["lifetime_opex_mode"] is not None:
            lifetime_cost_mode += outputs["lifetime_opex_mode"]

        outputs["lifetime_cost_mode"] = lifetime_cost_mode

    if not capex_bom.empty or outputs["discounted_opex_mean"] is not None:
        lifetime_discounted_cost_mean = discounted_capex_total

        if outputs["discounted_opex_mean"] is not None:
            lifetime_discounted_cost_mean += outputs["discounted_opex_mean"]

        outputs["discounted_lifetime_cost_mean"] = lifetime_discounted_cost_mean

    if not capex_bom.empty and outputs["discounted_opex_mode"] is not None:
        lifetime_discounted_cost_mode = discounted_capex_total

        if outputs["discounted_opex_mode"] is not None:
            lifetime_discounted_cost_mode += outputs["discounted_opex_mode"]

        outputs["discounted_lifetime_cost_mode"] = lifetime_discounted_cost_mode

    # Calculate values using most likely OPEX / Energy combination
    if outputs["discounted_opex_mode"] is not None:
        discounted_opex_base = outputs["discounted_opex_mode"]
    else:
        discounted_opex_base = outputs["discounted_opex_mean"]

    assert discounted_opex_base is not None

    if outputs["discounted_energy_mode"] is not None:
        discounted_energy_base = outputs["discounted_energy_mode"]
    else:
        discounted_energy_base = outputs["discounted_energy_mean"]

    assert discounted_energy_base is not None
    discounted_energy_base = discounted_energy_base * 1e6  # MW to W

    # CAPEX vs OPEX Breakdown and OPEX Breakdown if externalities
    breakdown = {
        "Discounted CAPEX": discounted_capex_total,
        "Discounted OPEX": discounted_opex_base,
    }

    outputs["cost_breakdown"] = breakdown

    if externalities_opex is None:
        discounted_maintenance = discounted_opex_base
    else:
        opex_breakdown = _get_opex_breakdown(
            opex_bom,
            externalities_opex,
            discounted_opex_base,
            discount_rate,
        )
        outputs["opex_breakdown"] = opex_breakdown
        discounted_maintenance = opex_breakdown["Maintenance"]
        discounted_external = opex_breakdown["Externalities"]

    # LCOE Breakdowns in cent/kWh (i.e. Euro/Wh * 1e5)
    factor = 1e5

    if phase_breakdown is not None:
        capex_lcoe_breakdown = {
            k: round(factor * v["discounted_costs"] / discounted_energy_base, 2)
            for k, v in phase_breakdown.iterrows()
        }
        outputs["capex_lcoe_breakdown"] = capex_lcoe_breakdown

    lcoe_maintenance = round(
        factor * discounted_maintenance / discounted_energy_base, 2
    )

    if externalities_opex is None:
        lcoe_external = 0
    else:
        lcoe_external = round(
            factor * discounted_external / discounted_energy_base, 2
        )
        outputs["opex_lcoe_breakdown"] = {
            "Maintenance": lcoe_maintenance,
            "Externalities": lcoe_external,
        }

    total_capex = sum(capex_lcoe_breakdown.values())
    total_opex = lcoe_maintenance + lcoe_external

    outputs["lcoe_breakdown"] = {"CAPEX": total_capex, "OPEX": total_opex}

    return outputs


def _get_metrics_table(
    opex_total: Optional[pd.Series],
    discounted_opex: Optional[pd.Series],
    energy_total: Optional[pd.Series],
    discounted_energy: Optional[pd.Series],
    lcoe_capex: Optional[pd.Series],
    lcoe_opex: Optional[pd.Series],
    lcoe_total: Optional[pd.Series],
) -> Optional[pd.DataFrame]:
    table_cols_and_conversion = [
        ("LCOE", lcoe_total, 1e3),  # from Euro/Wh to Euro/kWh
        ("LCOE CAPEX", lcoe_capex, 1e3),  # from Euro/Wh to Euro/kWh
        ("LCOE OPEX", lcoe_opex, 1e3),  # from Euro/Wh to Euro/kWh
        ("OPEX", opex_total, 1),
        ("Energy", energy_total, 1e-6),  # from Wh to MWh
        ("Discounted OPEX", discounted_opex, 1),
        ("Discounted Energy", discounted_energy, 1e-6),  # from Wh to MWh
    ]
    missing_cols = []
    metrics_dict = {}

    for col_name, col_result, factor in table_cols_and_conversion:
        if col_result is None:
            missing_cols.append(col_name)
            continue

        metrics_dict[col_name] = col_result.values * factor

    metrics = pd.DataFrame(metrics_dict)
    if len(metrics) is None:
        return

    # Set columns with missing data
    for col_name in missing_cols:
        metrics[missing_cols] = np.nan

    return metrics


def _get_outputs_stats(
    metrics_table,
    opex_total,
    discounted_opex,
    discounted_energy,
    lcoe_total,
    discounted_capex_total,
):
    outputs: dict[str, Any] = {
        "lifetime_opex_mean": None,
        "lifetime_opex_mode": None,
        "lifetime_opex_lower": None,
        "lifetime_opex_upper": None,
        "discounted_opex_mean": None,
        "discounted_opex_mode": None,
        "discounted_opex_lower": None,
        "discounted_opex_upper": None,
        "discounted_energy_mean": None,
        "discounted_energy_mode": None,
        "discounted_energy_lower": None,
        "discounted_energy_upper": None,
        "lcoe_mean": None,
        "lcoe_mode": None,
        "lcoe_lower": None,
        "lcoe_upper": None,
        "lcoe_pdf": None,
        "confidence_density": None,
    }

    if len(metrics_table) < 3:
        if opex_total is not None:
            outputs["lifetime_opex_mean"] = opex_total.mean()

        if discounted_opex is not None:
            outputs["discounted_opex_mean"] = discounted_opex.mean()

        if discounted_energy is not None:
            # From W to MW
            outputs["discounted_energy_mean"] = discounted_energy.mean() / 1e6

        if lcoe_total is not None:
            # From Euro/Wh to Euro/kWh
            outputs["lcoe_mean"] = lcoe_total.mean() * 1000

        return outputs

    if opex_total is not None:
        try:
            distribution = UniVariateKDE(opex_total)
            outputs["lifetime_opex_mean"] = distribution.mean()
            outputs["lifetime_opex_mode"] = distribution.mode()

            intervals = distribution.confidence_interval(95)

            if intervals is not None:
                outputs["lifetime_opex_lower"] = intervals[0]
                outputs["lifetime_opex_upper"] = intervals[1]

        except np.linalg.LinAlgError:
            outputs["lifetime_opex_mean"] = opex_total.mean()

    if discounted_opex is not None and discounted_energy is not None:
        try:
            distribution = BiVariateKDE(discounted_opex, discounted_energy)

            mean_coords = distribution.mean()
            opex_mean = mean_coords[0]
            energy_mean = mean_coords[1]
            lcoe_mean = (discounted_capex_total + opex_mean) / energy_mean

            outputs["lcoe_mean"] = lcoe_mean * 1000  # Euro/Wh to Euro/kWh
            outputs["discounted_opex_mean"] = opex_mean
            outputs["discounted_energy_mean"] = energy_mean / 1e6  # W to MW

            mode_coords = distribution.mode()
            opex_mode = mode_coords[0]
            energy_mode = mode_coords[1]
            lcoe_mode = (discounted_capex_total + opex_mode) / energy_mode

            outputs["lcoe_mode"] = lcoe_mode * 1000  # Euro/Wh to Euro/kWh
            outputs["discounted_opex_mode"] = opex_mode
            outputs["discounted_energy_mode"] = energy_mode / 1e6  # W to MW

            xx, yy, pdf = distribution.pdf()
            clevels = pdf_confidence_densities(pdf)

            # LCOE distribution
            outputs["lcoe_pdf"] = {"values": pdf, "coords": [xx, yy]}

            if clevels:
                outputs["confidence_density"] = clevels[0]
                cx, cy = pdf_contour_coords(xx, yy, pdf, clevels[0])

                outputs["discounted_opex_lower"] = min(cx)
                outputs["discounted_energy_lower"] = min(cy) / 1e6  # W to MW
                outputs["discounted_opex_upper"] = max(cx)
                outputs["discounted_energy_upper"] = max(cy) / 1e6  # W to MW

                lcoes = [
                    (discounted_capex_total + discounted_opex)
                    / discounted_energy
                    for discounted_opex, discounted_energy in zip(cx, cy)
                ]

                # Euro/Wh to Euro/kWh
                outputs["lcoe_lower"] = min(lcoes) * 1000
                outputs["lcoe_upper"] = max(lcoes) * 1000

        except np.linalg.LinAlgError:
            _get_discounted_opex_stats(outputs, discounted_opex)
            _get_discounted_energy_stats(outputs, discounted_energy)

            assert lcoe_total is not None

            # Euro/Wh to Euro/kWh
            try:
                distribution = UniVariateKDE(lcoe_total)
                outputs["lcoe_mean"] = distribution.mean() * 1000
                outputs["lcoe_mode"] = distribution.mode() * 1000

                intervals = distribution.confidence_interval(95)

                if intervals is not None:
                    outputs["lcoe_lower"] = intervals[0] * 1000
                    outputs["lcoe_upper"] = intervals[1] * 1000

            except np.linalg.LinAlgError:
                outputs["lcoe_mean"] = lcoe_total.mean() * 1000

        return outputs

    if discounted_opex is not None:
        _get_discounted_opex_stats(outputs, discounted_opex)

    if discounted_energy is not None:
        _get_discounted_energy_stats(outputs, discounted_energy)

    return outputs


def _get_discounted_opex_stats(outputs: dict[str, Any], discounted_opex):
    try:
        distribution = UniVariateKDE(discounted_opex)
        outputs["discounted_opex_mean"] = distribution.mean()
        outputs["discounted_opex_mode"] = distribution.mode()

        intervals = distribution.confidence_interval(95)

        if intervals is not None:
            outputs["discounted_opex_lower"] = intervals[0]
            outputs["discounted_opex_upper"] = intervals[1]

    except np.linalg.LinAlgError:
        outputs["discounted_opex_mean"] = discounted_opex.mean()


def _get_discounted_energy_stats(outputs: dict[str, Any], discounted_energy):
    # W to MW
    try:
        distribution = UniVariateKDE(discounted_energy)
        outputs["discounted_energy_mean"] = distribution.mean() / 1e6
        outputs["discounted_energy_mode"] = distribution.mode() / 1e6

        intervals = distribution.confidence_interval(95)

        if intervals is not None:
            outputs["discounted_energy_lower"] = intervals[0] / 1e6
            outputs["discounted_energy_upper"] = intervals[1] / 1e6

    except np.linalg.LinAlgError:
        outputs["discounted_energy_mean"] = discounted_energy.mean() / 1e6


def _get_opex_breakdown(
    opex_bom,
    externalities_opex,
    discounted_opex_base,
    discount_rate,
):
    years = range(len(opex_bom))

    discounted_externals = [
        externalities_opex / (1 + discount_rate) ** i for i in years
    ]
    discounted_external = np.array(discounted_externals).sum()
    discounted_maintenance = discounted_opex_base - discounted_external

    return {
        "Maintenance": discounted_maintenance,
        "Externalities": discounted_external,
    }
