from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock

import psycopg
import psycopg.sql as sql
import pytest
from shapely import Polygon
from sqlalchemy import Table

from mdo_engine.utilities.database import PostGIS

pytestmark = pytest.mark.skipif(
    (
        "not (config.getoption('postgresql_path') and "
        "config.getoption('postgresql_password'))"
    ),
    reason=(
        "Arguments --postgresql-path and --postgresql-password are required "
        "for database tests"
    ),
)


@pytest.fixture(scope="module")
def postgresql_path(request):
    return Path(request.config.getoption("postgresql_path"))


@pytest.fixture(scope="module")
def readonly(
    postgresql_noproc,
    postgresql_path,
) -> Generator[PostGIS, None, None]:
    """
    Given the postgresql process fixture object returns a db connection
    :param psql_proc: postgis process fixture
    :return: psycopg2 connection
    """
    from pytest_postgresql.janitor import DatabaseJanitor

    dbname = f"{postgresql_noproc.dbname}_readonly"
    db_config = {
        "host": postgresql_noproc.host,
        "port": postgresql_noproc.port,
        "dbname": dbname,
        "user": postgresql_noproc.user,
        "pwd": postgresql_noproc.password,
    }

    db = PostGIS("psycopg")
    db.set_credentials(db_config)

    janitor = DatabaseJanitor(
        user=postgresql_noproc.user,
        host=postgresql_noproc.host,
        port=postgresql_noproc.port,
        version=postgresql_noproc.version,
        dbname=dbname,
        password=postgresql_noproc.password,
    )
    pg_load = [
        postgresql_path / "postgresql" / "admin.sql",
        postgresql_path / "postgresql" / "schema.sql",
        _load_database_tables,
    ]

    with janitor:
        for load_element in pg_load:
            janitor.load(load_element)
        db.configure()

        yield db


@pytest.fixture()
def readwrite(
    postgresql_noproc,
    postgresql_path,
) -> Generator[PostGIS, None, None]:
    """
    Given the postgresql process fixture object returns a db connection
    :param psql_proc: postgis process fixture
    :return: psycopg2 connection
    """
    from pytest_postgresql.janitor import DatabaseJanitor

    dbname = f"{postgresql_noproc.dbname}_readwrite"
    db_config = {
        "host": postgresql_noproc.host,
        "port": postgresql_noproc.port,
        "dbname": dbname,
        "user": postgresql_noproc.user,
        "pwd": postgresql_noproc.password,
    }

    db = PostGIS("psycopg")
    db.set_credentials(db_config)
    db.set_echo(True)

    janitor = DatabaseJanitor(
        user=postgresql_noproc.user,
        host=postgresql_noproc.host,
        port=postgresql_noproc.port,
        version=postgresql_noproc.version,
        dbname=dbname,
        password=postgresql_noproc.password,
    )
    pg_load = [
        postgresql_path / "postgresql" / "admin.sql",
        postgresql_path / "postgresql" / "schema.sql",
        _load_database_tables,
    ]

    ## Don't drop the database for debugging
    # janitor.init()
    # for load_element in pg_load:
    #     janitor.load(load_element)

    # db.configure()
    # yield db

    with janitor:
        for load_element in pg_load:
            janitor.load(load_element)

        db.configure()
        yield db


def _load_database_tables(**kwargs: Any) -> None:
    """Prepare the database for tests."""
    db_connection: psycopg.Connection = psycopg.connect(**kwargs)
    query = sql.SQL("""SELECT public.db_from_csv(
    '/home/postgres/export',
    'project.site',
    'project.time_series_om_tidal'
);""")
    with db_connection.cursor() as cur:
        cur.execute(query)
        db_connection.commit()


def test_postgis_configure(readonly):
    assert readonly.session is not None


def test_postgis_reflect_table(readonly):
    assert "project.site" not in readonly._meta.tables

    table = readonly.reflect_table("site", "project")

    assert isinstance(table, Table)
    assert set(table.columns.keys()) == set(
        [
            "id",
            "site_name",
            "lease_area_proj4_string",
            "site_boundary",
            "lease_boundary",
            "corridor_boundary",
            "cable_landing_location",
        ]
    )
    assert "project.site" in readonly._meta.tables


def test_postgis_execute_query(readonly):
    query_str = "SELECT site_boundary FROM project.site WHERE id = 1;"
    with readonly.exectute_query(query_str) as cursor:
        rows = cursor.fetchall()

    assert len(rows) == 1
    columns = rows[0]

    assert len(columns) == 1
    test = columns[0]

    assert isinstance(test, Polygon)


def test_postgis_execute_transaction(readwrite):
    query_str = (
        'ALTER TABLE project.site DROP COLUMN "lease_area_proj4_string";'
    )
    readwrite.execute_transaction(query_str)

    table = readwrite.reflect_table("site", "project")
    assert "lease_area_proj4_string" not in table.columns.keys()


def test_postgis_call_function(readwrite):
    readwrite.call_function("filter.sp_filter_site_time_series_om_tidal", 1)

    query_str = "SELECT * FROM filter.time_series_om_tidal LIMIT 10;"
    with readwrite.exectute_query(query_str) as cursor:
        rows = cursor.fetchall()

    assert rows


def test_postgis_safe_reflect_table(mocker, readwrite):
    assert "project.site" not in readwrite._meta.tables
    spy: MagicMock = mocker.spy(readwrite, "reflect_table")

    table = readwrite.reflect_table("site", "project")
    assert "project.site" in readwrite._meta.tables
    assert spy.call_count == 1

    test = readwrite.safe_reflect_table("site", "project")
    assert test is table
    assert spy.call_count == 1


def test_postgis_drop_columns(readwrite):
    readwrite.drop_columns(
        "site",
        ["lease_area_proj4_string"],
        schema="project",
    )

    table = readwrite.reflect_table("site", "project")
    assert "lease_area_proj4_string" not in table.columns.keys()


def test_postgis_get_table_names(readonly):
    assert "site" in readonly.get_table_names("project")


def test_postgis_get_column_names(readonly):
    assert "lease_area_proj4_string" in readonly.get_column_names(
        "site",
        "project",
    )


def test_postgis_get_db_names(readonly):
    assert "template0" in readonly.get_db_names()


def test_postgis_has_permission(readonly):
    assert readonly.has_permission("filter.time_series_om_tidal")


def test_server_execute_query(readonly):
    query_str = "SELECT site_boundary FROM project.site WHERE id = 1;"
    rows = readonly.server_execute_query(query_str)

    assert len(rows) == 1
    columns = rows[0]

    assert len(columns) == 1
    test = columns[0]

    assert isinstance(test, Polygon)
