# coding: utf-8

# Usage:
# > activate _pytablewriter
# > cd E:\Programming\Sphinx\git\dtocean.github.io\data
# > python input_indicator_table.py > input_indicator_table.rst

import pytablewriter
from pytablewriter import Align

if __name__ == "__main__":
    writer = pytablewriter.RstGridTableWriter()
    writer.from_csv("input_indicator_table.csv")
    writer.align_list = [Align.CENTER, None, None]
    writer.write_table()
