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

from dtocean_economics import main


def test_main(bom, opex_costs, energy_record):
    result = main(bom, opex_costs, energy_record)

    for value in result.values():
        assert value is not None


def test_main_no_capex(bom, opex_costs, energy_record):
    capex_empty = bom.drop(bom.index)
    result = main(capex_empty, opex_costs, energy_record)

    assert result["CAPEX breakdown"] is None
    assert result["CAPEX"] is None
    assert result["Discounted CAPEX"] is None
    assert result["LCOE CAPEX"] is None


def test_main_no_opex(bom, energy_record):
    opex_empty = bom.drop(bom.index)

    result = main(bom, opex_empty, energy_record)

    assert result["OPEX"] is None
    assert result["Discounted OPEX"] is None
    assert result["LCOE OPEX"] is None


def test_main_no_energy(bom, opex_costs, energy_record):
    energy_empty = energy_record.drop(energy_record.index)
    result = main(bom, opex_costs, energy_empty)

    assert result["Energy"] is None
    assert result["Discounted Energy"] is None
    assert result["LCOE CAPEX"] is None
    assert result["LCOE OPEX"] is None
    assert result["LCOE"] is None
