# coding: utf-8

# Usage:
# > activate _pytablewriter
# > cd E:\Programming\Sphinx\git\dtocean.github.io\data
# > python tidal_example_inputs_table.py > tidal_example_inputs_table.rst

import pytablewriter
from pytablewriter import Align

if __name__ == "__main__":
    writer = pytablewriter.RstGridTableWriter()
    writer.from_csv("tidal_example_inputs_table.csv")
    writer.align_list = [None, None, Align.RIGHT]
    writer.write_table()
