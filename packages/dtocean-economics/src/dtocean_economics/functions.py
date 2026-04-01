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
Created on Thu Mar 05 16:16:39 2015

Functions to be used within DTOcean tool

.. moduleauthor:: Marta Silva <marta@wavec.org>
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""


def get_combined_lcoe(lcoe_capex=None, lcoe_opex=None):
    if lcoe_capex is not None and lcoe_opex is not None:
        lcoe = lcoe_capex + lcoe_opex
    elif lcoe_capex is not None:
        lcoe = lcoe_capex
    else:
        lcoe = lcoe_opex

    return lcoe
