# coding: utf-8

# Usage:
# > activate _pytablewriter
# > cd E:\Programming\Sphinx\git\dtocean.github.io\data
# > python data_widget_table_table.py > data_widget_table_table.rst

import pytablewriter
from pytablewriter import Align

if __name__ == "__main__":
    writer = pytablewriter.RstGridTableWriter()
    writer.from_csv("data_widget_table_table.csv")
    writer.write_table()
