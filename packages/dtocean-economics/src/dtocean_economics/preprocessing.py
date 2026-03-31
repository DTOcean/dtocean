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

"""
.. moduleauthor:: Marta Silva <marta@wavec.org>
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import pandas as pd


def estimate_cost_per_power(total_rated_power, unit_cost, phase=None):
    cost = total_rated_power * unit_cost
    cost_bom = make_phase_bom([1], [cost], [0], phase)

    return cost_bom


def estimate_energy(lifetime, year_energy, network_efficiency=None):
    if network_efficiency is not None:
        net_coeff = network_efficiency
    else:
        net_coeff = 1.0

    energy = [0] + [year_energy * net_coeff] * lifetime
    energy_year = range(lifetime + 1)

    raw_energy = {"energy": energy, "project_year": energy_year}

    energy_record = pd.DataFrame(raw_energy)

    return energy_record


def estimate_opex(
    lifetime,
    total_rated_power=None,
    opex_estimate=None,
    annual_repair_cost_estimate=None,
    annual_array_mttf_estimate=None,
):
    # Note, units of mttf is hours

    # Collect opex costs
    annual_costs = 0.0

    if total_rated_power is not None and opex_estimate is not None:
        annual_costs += total_rated_power * opex_estimate

    if (
        annual_repair_cost_estimate is not None
        and annual_array_mttf_estimate is not None
    ):
        year_mttf = annual_array_mttf_estimate / 24.0 / 365.25
        failure_cost = annual_repair_cost_estimate / year_mttf

        annual_costs += failure_cost

    opex_unit_cost = [0.0] + [annual_costs] * lifetime
    opex_year = range(lifetime + 1)

    raw_costs = {"costs": opex_unit_cost, "project_year": opex_year}

    opex_bom = pd.DataFrame(raw_costs)

    return opex_bom


def make_phase_bom(quantities, costs, years, phase=None):
    if not (len(quantities) == len(costs) == len(years)):
        errStr = (
            "Number of quantities, unit costs and project years must be "
            "equal"
        )
        raise ValueError(errStr)

    phase_years = [phase] * len(years)

    raw_costs = {
        "phase": phase_years,
        "quantity": quantities,
        "unitary_cost": costs,
        "project_year": years,
    }

    phase_bom = pd.DataFrame(raw_costs)

    return phase_bom
