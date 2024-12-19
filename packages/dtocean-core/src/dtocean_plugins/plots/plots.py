# -*- coding: utf-8 -*-

#    Copyright (C) 2021-2024 Mathew Topper
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

from mdo_engine.boundary.interface import MetaInterface


class PlotInterface(MetaInterface):
    def __init__(self):
        super(PlotInterface, self).__init__()
        self.fig_handle = None

    @classmethod
    def declare_optional(cls):
        return None

    @classmethod
    def declare_outputs(cls):
        return None
