# -*- coding: utf-8 -*-
"""py.test tests on control.data module

.. moduleauthor:: Mathew Topper <mathew.topper@tecnalia.com>
"""

import pytest
import pandas as pd
from sqlalchemy.orm import create_session
from sqlalchemy.engine import Engine

from mdo_engine.utilities.database import SQLite

from .create_db import add_ships

@pytest.fixture(scope="module")
def database():

    add_ships()

    database = SQLite()
    database.set_dbname("test.db")
    database.configure()

    return database

def test_connect(database):

    assert isinstance(database._engine, Engine)

def test_get_table_names(database):

    tnames = database.get_table_names()

    assert "ships" in tnames

def test_reflection(database):

    test_table="ships"

    testtable = database.reflect_table(test_table)

    assert "tonnage" in testtable.columns

def test_read_sql(database):

    test_table="ships"

    ship_table = pd.read_sql(test_table, database._engine)

    assert "length" in ship_table.columns
