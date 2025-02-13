# -*- coding: utf-8 -*-
"""py.test tests on main.py

.. moduleauthor:: Mathew Topper <damm_horse@yahoo.co.uk>
"""

import os

import pytest

import dtocean_dummy


# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def sheet():
    """Share a Spreadsheet object"""
    return dtocean_dummy.Spreadsheet()


def test_array_size(sheet):
    """Test that the random array size is as requested."""

    assert len(sheet._get_random_array(10)) == 10


def test_array_low(sheet):
    """Test that the minimum of the array is greater than or equal to
    Spreadsheet.low."""

    assert min(sheet._get_random_array(10)) >= sheet.low


def test_array_high(sheet):
    """Test that the maximum of the array is less than Spreadsheet.high."""

    assert max(sheet._get_random_array(10)) < sheet.high


def test_table_length():
    sheet = dtocean_dummy.Spreadsheet()
    array = sheet._get_random_array(10)
    sheet._array_2_df(array)

    assert sheet.table is not None
    assert len(sheet.table) == 10


def test_table_cumsum_length():
    """Check that the length of the cumulative sum is OK"""

    sheet = dtocean_dummy.Spreadsheet()
    array = sheet._get_random_array(10)
    sheet._array_2_df(array)
    sheet._add_cumsum()

    assert sheet.table is not None
    cumsum = sheet.table["Cumulative"]

    assert len(cumsum) == 10


def test_table_cumsum_total():
    """Check that the cumulative sum in the pandas table is OK"""

    sheet = dtocean_dummy.Spreadsheet()
    array = sheet._get_random_array(10)
    sheet._array_2_df(array)
    sheet._add_cumsum()

    assert sheet.table is not None
    cumsum = sheet.table["Cumulative"]

    assert cumsum.iloc[-1] == sum(array)


def test_create_csv(tmpdir):
    """Test if csv file is written"""

    locd = tmpdir.mkdir("sub")
    p = locd.join("test.csv")

    sheet = dtocean_dummy.Spreadsheet()
    sheet.make_table(10)
    sheet.write_csv(str(p))

    assert len(locd.listdir()) == 1
    assert os.path.basename(str(locd.listdir()[0])) == "test.csv"


def test_create_xls(tmpdir):
    """Test if excel file is written"""

    locd = tmpdir.mkdir("sub")
    p = locd.join("test.xls")

    sheet = dtocean_dummy.Spreadsheet()
    sheet.make_table(10)
    sheet.write_xls(str(p))

    assert len(locd.listdir()) == 1
    assert os.path.basename(str(locd.listdir()[0])) == "test.xlsx"


def test_spreadsheet_call(tmpdir):
    """Test if Spreadsheet.call works for all file types"""

    locd = tmpdir.mkdir("sub")
    dirp = str(locd)

    sheet = dtocean_dummy.Spreadsheet()

    # Check the error for a bad file type
    filep = os.path.join(dirp, "test.docx")

    with pytest.raises(ValueError):
        sheet(10, filep, out_fmt="docx")

    for ftype in sheet._valid_formats:
        filep = os.path.join(dirp, "test.{}".format(ftype))

        sheet(10, filep, out_fmt=ftype)

    assert len(locd.listdir()) == len(sheet._valid_formats)


@pytest.mark.xfail
def test_fail(tmpdir):
    """Generate a test failure"""

    assert 0 == 1
