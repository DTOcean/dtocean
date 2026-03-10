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

from PySide6.QtWidgets import QApplication


def is_high_dpi(dpi_freshold=100.0) -> bool:
    qapp = QApplication.instance() or QApplication()

    if not isinstance(qapp, QApplication):
        return False

    for screen in qapp.screens():
        if screen.logicalDotsPerInch() > dpi_freshold:
            return True

    return False
