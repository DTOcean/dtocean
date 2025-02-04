# -*- coding: utf-8 -*-

#    Copyright (C) 2025 Mathew Topper
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


import pytest

from dtocean_wec.pfit_form import PowerPerformance


@pytest.fixture
def power_performance(qtbot, main_window):
    window = PowerPerformance(main_window)
    window.show()
    qtbot.addWidget(window)
    return window


def test_power_performance(power_performance):
    assert True
