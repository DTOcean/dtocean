# -*- coding: utf-8 -*-

#    Copyright (C) 2025-2026 Mathew Topper
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

from dtocean_hydro.configure import get_data
from dtocean_wec import run


def init(args):
    print("+ Fetching data files...")
    get_data(args.force)


def subcommand(subparser):
    description = "Subcommands for the dtocean-hydrodynamics module"
    parser = subparser.add_parser(
        "hydrodynamics",
        description=description,
        help="dtocean-hydrodynamics commands",
    )
    sp = parser.add_subparsers(required=True)
    _setup_wec(sp)


def _setup_wec(subparser):
    """Command line interface for dtocean WEC pre-processor.

    Example:

        To get help::

            dtocean hydrodynamics wec -h

    """

    desStr = "Run the WEC pre-processor GUI."
    parser = subparser.add_parser("wec", description=desStr, help=desStr)
    parser.set_defaults(func=lambda _: run())
