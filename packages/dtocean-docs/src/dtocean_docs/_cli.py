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

import argparse

from dtocean_docs import open_docs


def run():
    description = "Open the offline DTOcean docs in a browser"
    parser = argparse.ArgumentParser(
        prog="dtocean-docs",
        description=description,
    )
    parser.set_defaults(func=lambda _: open_docs())

    args = parser.parse_args()
    args.func(args)
