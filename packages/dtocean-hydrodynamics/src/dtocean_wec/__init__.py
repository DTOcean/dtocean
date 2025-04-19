# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Francesco Ferri
#    Copyright (C) 2017-2025 Mathew Topper
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

import argparse
import sys

from PySide6.QtWidgets import QApplication

from .main import MainWindow


def run():
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())


def gui_interface():
    """Command line interface for dtocean WEC pre-processor.

    Example:

        To get help::

            $ dtocean-wec -h

    """

    desStr = "Run the WEC pre-processor GUI."
    parser = argparse.ArgumentParser(description=desStr)
    parser.parse_args()

    run()
