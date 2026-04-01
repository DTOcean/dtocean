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
    costs_from_bom,
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
            "project.lcoe_mode_opex",
            "project.lcoe_mode_energy",
            "project.lcoe_mode",
            "project.lcoe_interval_lower",
            "project.lcoe_interval_upper",
            "project.lcoe_mean",
            "project.capex_total",
            "project.capex_without_externalities",
            "project.discounted_capex",
            "project.lifetime_opex_mean",
            "project.lifetime_opex_mode",
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
            "lcoe_mode_opex": "project.lcoe_mode_opex",
            "lcoe_mode_energy": "project.lcoe_mode_energy",
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
        )

        discounted_capex = result["Discounted CAPEX"]
        assert discounted_capex is not None

        self.data.capex_total = result["CAPEX"]
        self.data.discounted_capex = discounted_capex
        self.data.capex_breakdown = result["CAPEX breakdown"]
        self.data.capex_no_externalities = _get_capex_no_externalities(
            self.data.externalities_capex, self.data.capex_total
        )

        metrics_table = _get_metrics_table(result, opex_bom, energy_record)
        if metrics_table is None:
            return

        self.data.economics_metrics = metrics_table

        # Do univariate stats on discounted metrics and optionally LCOE
        args_table = {"Discounted Energy": "discounted_energy"}

        if result["Discounted OPEX"] is None:
            args_table["LCOE"] = "lcoe"
        else:
            args_table["Discounted OPEX"] = "discounted_opex"
            args_table["OPEX"] = "lifetime_opex"

        for key, arg_root in args_table.items():
            if result[key] is None:
                continue

            data = metrics_table[key].values
            assert isinstance(data, np.ndarray)
            arg_stats = _get_metric_stats(data, arg_root)

            for k, v in arg_stats:
                self.data[k] = v

        self.data.lifetime_cost_mean = _get_lifetime_cost(
            result["CAPEX"], self.data.lifetime_opex_mean
        )
        self.data.lifetime_cost_mode = _get_lifetime_cost(
            result["CAPEX"], self.data.lifetime_opex_mode
        )
        self.data.discounted_lifetime_cost_mean = _get_lifetime_cost(
            discounted_capex, self.data.discounted_opex_mean
        )
        self.data.discounted_lifetime_cost_mode = _get_lifetime_cost(
            discounted_capex, self.data.discounted_opex_mode
        )

        if (
            metrics_table["Discounted Energy"].isnull().any()
            or metrics_table["Discounted OPEX"].isnull().any()
        ):
            return

        energy = result["Discounted Energy"]
        opex = result["Discounted OPEX"]

        if len(metrics_table["Discounted Energy"]) < 3:
            lcoe_basic = _get_lcoe_basic(discounted_capex, opex, energy)

        lcoe_metrics = _get_lcoe(metrics_table, discounted_capex)
        if lcoe_metrics is None:
            return

        self.data.lcoe_mean = lcoe_metrics["lcoe_mean"]


def _get_outputs(
    capex_bom: pd.DataFrame,
    opex_bom: pd.DataFrame,
    energy_record: pd.DataFrame,
    discount_rate: float,
):
    outputs: dict[str, Any] = {
        "capex_breakdown": None,
        "capex_total": None,
        "discounted_capex": None,
        "economics_metrics": None,
    }

    discounted_capex = None
    discounted_opex = None
    lcoe_capex = None
    lcoe_opex = None
    lcoe_total = None

    if not capex_bom.empty:
        costs_df = costs_from_bom(capex_bom)
        discounted_capex = get_discounted_values(
            costs_df,
            discount_rate,
        )

        outputs["capex_total"] = get_total_cost(capex_bom)
        outputs["capex_breakdown"] = get_phase_breakdown(capex_bom)
        outputs["discounted_capex"] = discounted_capex.iloc[0]

    if not opex_bom.empty:
        opex_by_year = opex_bom.set_index("project_year")
        opex_total = opex_by_year.sum()
        discounted_opex = get_discounted_values(opex_bom, discount_rate)

    if not energy_record.empty:
        energy_by_year = energy_record.set_index("project_year")
        energy_total = energy_by_year.sum()
        discounted_energy = get_discounted_values(energy_record, discount_rate)

        if discounted_capex is not None:
            lcoe_capex = discounted_capex / discounted_energy
            lcoe_total = lcoe_capex

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
        return

    outputs["economics_metrics"] = metrics_table

    lcoe_metrics = _get_lcoe(metrics_table, discounted_capex)
    if lcoe_metrics is None:
        return

    self.data.lcoe_mean = lcoe_metrics["lcoe_mean"]
    discounted_opex_base = lcoe_metrics["discounted_opex_base"]
    discounted_energy_base = lcoe_metrics["discounted_energy_base"]

    if "lcoe_mode" in lcoe_metrics:
        self.data.lcoe_mode = lcoe_metrics["lcoe_mode"]
        self.data.lcoe_mode_opex = lcoe_metrics["lcoe_mode_opex"]
        self.data.lcoe_mode_energy = lcoe_metrics["lcoe_mode_energy"]
        self.data.lcoe_pdf = lcoe_metrics["lcoe_pdf"]

    if "confidence_density" in lcoe_metrics:
        self.data.confidence_density = lcoe_metrics["confidence_density"]
        self.data.lcoe_lower = lcoe_metrics["lcoe_lower"]
        self.data.lcoe_upper = lcoe_metrics["lcoe_upper"]

    # Calculate values using most likely OPEX / Energy combination

    # CAPEX vs OPEX Breakdown and OPEX Breakdown if externalities
    breakdown = {
        "Discounted CAPEX": discounted_capex,
        "Discounted OPEX": discounted_opex_base,
    }

    self.data.cost_breakdown = breakdown

    if self.data.externalities_opex is None:
        discounted_maintenance = discounted_opex_base
    else:
        opex_breakdown = _get_opex_breakdown(
            opex_bom,
            self.data.externalities_opex,
            discounted_opex_base,
            self.data.discount_rate,
        )
        self.data.opex_breakdown = opex_breakdown
        discounted_maintenance = opex_breakdown["Maintenance"]
        discounted_external = opex_breakdown["Externalities"]

    # LCOE Breakdowns in cent/kWh

    if self.data.capex_breakdown is not None:
        capex_lcoe_breakdown = {}

        for k, v in self.data.capex_breakdown.iteritems():
            capex_lcoe_breakdown[k] = round(v / discounted_energy_base, 2)

        self.data.capex_lcoe_breakdown = capex_lcoe_breakdown

    lcoe_maintenance = round(discounted_maintenance / discounted_energy_base, 2)

    if self.data.externalities_opex is None:
        lcoe_external = 0

    else:
        lcoe_external = round(discounted_external / discounted_energy_base, 2)

        self.data.opex_lcoe_breakdown = {
            "Maintenance": lcoe_maintenance,
            "Externalities": lcoe_external,
        }

    total_capex = sum(capex_lcoe_breakdown.values())
    total_opex = lcoe_maintenance + lcoe_external

    self.data.lcoe_breakdown = {"CAPEX": total_capex, "OPEX": total_opex}

    return


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
        ("LCOE", lcoe_total, 1e-3),  # from Euro/Wh to Euro/kWh
        ("LCOE CAPEX", lcoe_capex, 1e-3),  # from Euro/Wh to Euro/kWh
        ("LCOE OPEX", lcoe_opex, 1e-3),  # from Euro/Wh to Euro/kWh
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


def _get_metric_stats(data: np.ndarray, arg_root: str):
    mean = None
    mode = None
    lower = None
    upper = None

    # Catch one or two data points
    if len(data) == 1:
        mean = data[0]

    elif len(data) == 2:
        assert isinstance(data, np.ndarray)
        mean = data.mean()

    else:
        assert isinstance(data, np.ndarray)

        try:
            distribution = UniVariateKDE(data)
            mean = distribution.mean()
            mode = distribution.mode()

            intervals = distribution.confidence_interval(95)

            if intervals is not None:
                lower = intervals[0]
                upper = intervals[1]

        except np.linalg.LinAlgError:
            mean = data.mean()

    arg_mean = "{}_mean".format(arg_root)
    arg_mode = "{}_mode".format(arg_root)
    arg_lower = "{}_lower".format(arg_root)
    arg_upper = "{}_upper".format(arg_root)

    return {
        arg_mean: mean,
        arg_mode: mode,
        arg_lower: lower,
        arg_upper: upper,
    }


def _get_lcoe_basic(capex, opex, energy):
    mean_lcoe = (capex / 1000.0 + np.mean(opex)) / np.mean(energy)

    result = {}
    result["lcoe_mean"] = mean_lcoe
    result["discounted_opex_base"] = np.mean(opex) * 1000.0
    result["discounted_energy_base"] = np.mean(energy) * 10.0

    return result


def _get_lcoe_kde(capex, opex, energy):
    result = {}

    try:
        distribution = BiVariateKDE(opex, energy)
    except np.linalg.LinAlgError:
        return

    mean_coords = distribution.mean()
    result["lcoe_mean"] = (capex / 1000.0 + mean_coords[0]) / mean_coords[1]

    mode_coords = distribution.mode()
    result["lcoe_mode"] = (capex / 1000.0 + mode_coords[0]) / mode_coords[1]

    result["lcoe_mode_opex"] = mode_coords[0] * 1000
    result["lcoe_mode_energy"] = mode_coords[1]

    xx, yy, pdf = distribution.pdf()
    clevels = pdf_confidence_densities(pdf)

    if clevels:
        cx, cy = pdf_contour_coords(xx, yy, pdf, clevels[0])

        lcoes = []

        for discounted_opex, discounted_energy in zip(cx, cy):
            lcoe = (capex / 1000.0 + discounted_opex) / discounted_energy
            lcoes.append(lcoe)

        result["confidence_density"] = clevels[0]
        result["lcoe_lower"] = min(lcoes)
        result["lcoe_upper"] = max(lcoes)

    # LCOE distribution
    result["lcoe_pdf"] = {"values": pdf, "coords": [xx, yy]}
    result["discounted_opex_base"] = mode_coords[0] * 1000.0
    result["discounted_energy_base"] = mode_coords[1] * 10.0

    return result


def _get_opex_breakdown(
    opex_bom,
    externalities_opex,
    discounted_opex_base,
    discount_rate,
):
    years = range(1, len(opex_bom) + 1)

    discounted_externals = [
        externalities_opex / (1 + discount_rate) ** i for i in years
    ]

    discounted_external = np.array(discounted_externals).sum()
    discounted_maintenance = discounted_opex_base - discounted_external

    return {
        "Maintenance": discounted_maintenance,
        "Externalities": discounted_external,
    }


def _get_capex_no_externalities(externalities_capex, capex_total):
    if externalities_capex is None:
        return
    return capex_total - externalities_capex


def _get_lifetime_cost(capex, lifetime_opex):
    lifetime_cost = capex

    if lifetime_opex is not None:
        if lifetime_cost is None:
            lifetime_cost = 0
        lifetime_cost += lifetime_opex

    return lifetime_cost
