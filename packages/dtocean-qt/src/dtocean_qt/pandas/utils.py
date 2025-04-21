from pandas import to_datetime


def fillNoneValues(column):
    """Fill all NaN/NaT values of a column with an empty string

    Args:
        column (pandas.Series): A Series object with all rows.

    Returns:
        column: Series with filled NaN values.
    """
    if column.dtype == object:
        column.fillna("", inplace=True)
    return column


def convertTimestamps(column):
    """Convert a dtype of a given column to a datetime.

    This method tries to do this by brute force.

    Args:
        column (pandas.Series): A Series object with all rows.

    Returns:
        column: Converted to datetime if no errors occured, else the
            original column will be returned.

    """
    tempColumn = column
    try:
        # try to convert the first row and a random row instead of the complete column, might be faster
        tempColumn = column.apply(to_datetime)
    except Exception:
        pass
    return tempColumn
