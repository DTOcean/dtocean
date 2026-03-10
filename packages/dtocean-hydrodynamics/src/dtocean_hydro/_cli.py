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

import argparse
from typing import TypeAlias

from .configure import get_data

SubParsers: TypeAlias = "argparse._SubParsersAction[argparse.ArgumentParser]"


def run():
    parser = argparse.ArgumentParser(prog="dtocean-hydro")
    subparsers = parser.add_subparsers(help="sub-command help", required=True)

    _setup_init(subparsers)

    args = parser.parse_args()
    args.func(args)


def _setup_init(subparsers: SubParsers):
    parser = subparsers.add_parser("init", help="download external files")
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="overwrite files",
    )
    parser.set_defaults(func=lambda args: get_data(args.force))
