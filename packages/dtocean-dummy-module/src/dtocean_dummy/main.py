# -*- coding: utf-8 -*-
"""This module contains the main class of the demonstration package called
Spreadsheet.

.. module:: main
   :platform: Windows
   :synopsis: Main computational code for dtocean-dummy

.. moduleauthor:: Mathew Topper <mathew.topper@tecnalia.com>
"""

# Built in modules
import logging
import os

# External module import
import numpy as np
import pandas as pd

# Set up logging
module_logger = logging.getLogger(__name__)


class Spreadsheet(object):
    """Create spreadsheets of random numbers and write to file.

    Args:
      low (float, optional): Minimum value of random numbers (inclusive).
        Defaults to 0.
      high (float, optional): Maximum value of random numbers (exclusive).
        Defaults to 1.

    Attributes:
      table (pandas.DataFrame): Pandas dataframe containing spreadsheet data.
      low (float): Minimum value of random numbers (inclusive).
      high (float): Maximum value of random numbers (exclusive).
    """

    # Valid formats
    _valid_formats = set(["csv", "xls"])

    def __init__(self, low=0.0, high=1.0):
        self.table = None
        self.low = low
        self.high = high

    def make_table(self, rows):
        """Create a numpy array of random numbers and insert into a pandas
        table.

        Args:
            rows (int): Number of rows for the spreadsheet.

        """

        # Create a numpy array of random numbers
        array = self._get_random_array(rows)

        # Populate the table attribute using the array
        self._array_2_df(array)

        # Add the cumulative sum to the table
        self._add_cumsum()

    def write_csv(self, csv_path, **kwargs):
        """Write the spreadsheet table to a csv file.

        Args:
            csv_path (str): Path to the csv file.
            **kwargs: Keyword arguments for pandas.to_csv method.

        Note:
            This method will convert the file extension of the given path
            to ".csv" regardless of the input.

        """

        if self.table is None:
            raise RuntimeError("Table not yet created")

        # Split off the file extension and force it to "*.csv"
        root, _ = os.path.splitext(csv_path)
        csv_path = "{}.csv".format(root)

        self.table.to_csv(csv_path, index=False, **kwargs)

        # Log the action
        log_msg = "CSV file written to: {}".format(csv_path)
        module_logger.info(log_msg)

    def write_xls(self, xls_path, **kwargs):
        """Write the spreadsheet table to an excel file.

        Args:
            xls_path (str): Path to the excel file.
            **kwargs: Keyword arguments for pandas.to_excel method.

        Note:
            This method will convert the file extension of the given path
            to ".xls" regardless of the input.

        """
        if self.table is None:
            raise RuntimeError("Table not yet created")

        # Split off the file extension and force it to "*.csv"
        root, _ = os.path.splitext(xls_path)
        xls_path = "{}.xlsx".format(root)

        self.table.to_excel(xls_path, index=False, **kwargs)

        # Log the action
        log_msg = "Excel file written to: {}".format(xls_path)
        module_logger.info(log_msg)

    def _get_random_array(self, size):
        """Make a numpy array of random numbers, drawn from a uniform
        distribution, subject to the low high attributes of the class.

        Note:
            This is a "private" method. It is not expected that the user would
            call this themselves, but it will be utilised by other functions.

        Args:
            size (int): Number of random numbers to make

        Returns:
            numpy.array: A numpy array of random numbers.

        """

        # Use numpy.random.uniform to generate the numbers
        return np.random.uniform(self.low, self.high, size)

    def _array_2_df(self, array, col_name="Random"):
        """Convert a numpy array to a pandas dataframe and set the
        Spreadsheet.table attribute.

        Args:
            array (numpy.array): Numpy array to convert to pandas DataFrame.
            col_name (str, optional): Column name for the array. Defaults to
              "Random".

        """

        # Make a dictionary of the inputs to pandas
        array_dict = {col_name: array}

        # Create the pandas dataframe
        self.table = pd.DataFrame(array_dict)

    def _add_cumsum(self, col_name="Cumulative"):
        """Add the cumulative sum of the first column to the table attribute.

        Args:
            col_name (str, optional): Column name for the sum. Defaults to
              "Cumulative".

        """
        if self.table is None:
            raise RuntimeError("Table not yet created")

        # Get the first column
        first_col = self.table.iloc[:, 0]

        self.table[col_name] = first_col.cumsum()

    def __call__(self, rows, out_path=None, out_fmt="csv"):
        """Create a table of the given number of rows and either print
        to stdout or create a file.

        Note:
            This is the special __call__ method. It runs when the object is
            executed directly, i.e.::

                >>> sheet = Spreadsheet
                >>> sheet(5)


        Args:
            rows (int): Number of rows for the spreadsheet.
            out_path (str, optional): Path to output file.
            out_fmt (str, optional): Output file type. Defaults to "csv".

        """

        # Make the table
        self.make_table(rows)

        # If no out_path is given just print the table
        if out_path is None:
            print(self.table)
            return

        # Check the validity of the output format
        if out_fmt not in self._valid_formats:
            fmt_list = " ,".join(self._valid_formats)
            errStr = (
                "{} is not a valid file format. Must be one of " "{}."
            ).format(out_fmt, fmt_list)
            raise ValueError(errStr)

        # Get the write method by string
        method_str = "write_{}".format(out_fmt)
        write_method = getattr(self, method_str)

        # Write the file
        write_method(out_path)
