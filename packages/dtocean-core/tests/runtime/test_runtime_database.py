from datetime import datetime, time
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg
import psycopg.sql as sql
import pytest
from pandas.testing import assert_frame_equal
from pytest_postgresql.janitor import DatabaseJanitor
from shapely import from_wkt
from sqlalchemy.engine import Engine

from dtocean_core.utils.database import (
    database_from_files,
    database_to_files,
    get_database,
    get_database_version,
)

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


def _load_database(**kwargs: Any) -> None:
    """Prepare the database for tests."""
    db_connection: psycopg.Connection = psycopg.connect(**kwargs)
    query = sql.SQL("""COMMENT ON DATABASE {} IS '{{\"version\": \"1.2.3\"}}';

SELECT public.db_from_csv(
    '/home/postgres/export',
    'project.site',
    'project.time_series_om_tidal',
    'reference.component_type',
    'reference.component',
    'reference.ports',
    'reference.component_discrete',
    'reference.component_collection_point'
);""").format(sql.Identifier(kwargs["dbname"]))
    with db_connection.cursor() as cur:
        cur.execute(query)
        db_connection.commit()


@pytest.fixture(scope="module")
def postgresql_path(request):
    return Path(request.config.getoption("postgresql_path"))


def test_get_database_bad_version(postgresql_noproc, postgresql_path):
    """
    Given the postgresql process fixture object returns a db connection
    :param psql_proc: postgres process fixture
    :return: psycopg2 connection
    """
    janitor = DatabaseJanitor(
        user=postgresql_noproc.user,
        host=postgresql_noproc.host,
        port=postgresql_noproc.port,
        version=postgresql_noproc.version,
        dbname=postgresql_noproc.dbname,
        password=postgresql_noproc.password,
    )
    pg_load = [
        postgresql_path / "postgresql" / "admin.sql",
        postgresql_path / "postgresql" / "schema.sql",
        _load_database,
    ]

    with janitor:
        for load_element in pg_load:
            janitor.load(load_element)
        db_config = {
            "host": postgresql_noproc.host,
            "port": postgresql_noproc.port,
            "dbname": postgresql_noproc.dbname,
            "user": postgresql_noproc.user,
            "pwd": postgresql_noproc.password,
        }
        with pytest.raises(RuntimeError) as exc_info:
            get_database(
                db_config,
                echo=True,
                timeout=60,
                min_version="1.2.4",
            )

    assert "less than the required" in str(exc_info)


@pytest.fixture(scope="module")
def static(postgresql_noproc, postgresql_path):
    """
    Given the postgresql process fixture object returns a db connection
    :param psql_proc: postgres process fixture
    :return: psycopg2 connection
    """
    dbname = f"{postgresql_noproc.dbname}_static"

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
        _load_database,
    ]

    with janitor:
        for load_element in pg_load:
            janitor.load(load_element)
        db_config = {
            "host": postgresql_noproc.host,
            "port": postgresql_noproc.port,
            "dbname": dbname,
            "user": postgresql_noproc.user,
            "pwd": postgresql_noproc.password,
        }
        database = get_database(db_config, timeout=60)
        yield database


def test_connect_local_static(static):
    assert isinstance(static._engine, Engine)


def test_get_database_version(static):
    version = get_database_version(static)
    assert version == "1.2.3"


@pytest.fixture(scope="module")
def component_map():
    return [
        {"table": "component_type", "schema": "reference"},
        {
            "table": "other",
            "dummy": True,
            "schema": "reference",
            "children": [
                {
                    "table": "ports",
                    "bool": ["jacking_capability"],
                    "geo": ["point_location"],
                },
                {
                    "table": "component",
                    "children": [
                        {
                            "table": "component_discrete",
                            "join": "fk_component_id",
                            "children": [
                                {
                                    "table": "component_collection_point",
                                    "join": "fk_component_discrete_id",
                                    "fkeys": {
                                        "fk_component_type_id": "reference.component_type"
                                    },
                                    "array": [
                                        "foundation_locations",
                                        "centre_of_gravity",
                                    ],
                                },
                            ],
                        },
                    ],
                },
            ],
        },
    ]


@pytest.fixture(scope="module")
def component_dump_path_static(tmp_path_factory, static, component_map):
    tmp_path = tmp_path_factory.mktemp("component_dump")
    database_to_files(tmp_path, component_map, static, prefer_csv=True)
    return tmp_path


def test_component_dump_tree(component_dump_path_static: Path):
    dump_tree = [
        (root, dirs, files)
        for root, dirs, files in component_dump_path_static.walk()
    ]

    assert dump_tree[0][1] == ["other"]
    assert dump_tree[0][2] == ["component_type.csv"]

    assert dump_tree[1][0] == component_dump_path_static / "other"
    assert dump_tree[1][1] == ["component"]
    assert set(dump_tree[1][2]) == set(["component.csv", "ports.csv"])

    assert dump_tree[2][0] == component_dump_path_static / "other" / "component"
    assert dump_tree[2][1] == ["component_discrete"]
    assert dump_tree[2][2] == ["component_discrete.csv"]

    assert (
        dump_tree[3][0]
        == component_dump_path_static
        / "other"
        / "component"
        / "component_discrete"
    )
    assert not dump_tree[3][1]
    assert dump_tree[3][2] == ["component_collection_point.csv"]


@pytest.fixture(scope="module")
def ports_table_static(component_dump_path_static: Path):
    ports_path = component_dump_path_static / "other" / "ports.csv"
    return pd.read_csv(ports_path)


def test_dump_bool(ports_table_static: pd.DataFrame):
    assert set(ports_table_static["jacking_capability"].unique()) == set(
        ["yes", "no"]
    )


def test_dump_geometry(ports_table_static: pd.DataFrame):
    geo_srid_str = ports_table_static["point_location"].iat[0]
    assert isinstance(geo_srid_str, str)

    srid_srt, geo_str = geo_srid_str.split(";")
    assert from_wkt(geo_str)

    if srid_srt is not None:
        assert srid_srt[:5] == "SRID="
        assert int(srid_srt[5:])


def test_dump_array(component_dump_path_static: Path):
    collection_point_path = (
        component_dump_path_static
        / "other"
        / "component"
        / "component_discrete"
        / "component_collection_point.csv"
    )
    assert collection_point_path.is_file()

    collection_point_table = pd.read_csv(collection_point_path)
    foundation_location_str = collection_point_table[
        "foundation_locations"
    ].iat[0]

    assert isinstance(foundation_location_str, str)

    brackets = str.maketrans("{}", "[]")
    foundation_location = eval(foundation_location_str.translate(brackets))

    assert isinstance(foundation_location, list)
    if foundation_location:
        assert isinstance(foundation_location[0], list)


@pytest.fixture(scope="module")
def site_map():
    return [
        {
            "table": "site",
            "autokey": True,
            "geo": [
                "site_boundary",
                "lease_boundary",
                "corridor_boundary",
                "cable_landing_location",
            ],
            "schema": "project",
            "children": [
                {
                    "table": "time_series_om_tidal",
                    "join": "fk_site_id",
                    "time": ["measure_time"],
                    "date": ["measure_date"],
                    "stripf": True,
                },
            ],
        },
    ]


@pytest.fixture(scope="module")
def site_dump_path_static(tmp_path_factory, static, site_map):
    tmp_path = tmp_path_factory.mktemp("site_dump")
    database_to_files(tmp_path, site_map, static, prefer_csv=True)
    return tmp_path


@pytest.fixture
def expected_site_dirs(site_dump_path_static: Path):
    site_path = site_dump_path_static / "site.csv"
    assert site_path.is_file()

    site_table = pd.read_csv(site_path)
    site_dirs = [f"site{id}" for id in site_table["id"].values]

    return site_dirs


def test_site_dump_tree(
    site_dump_path_static: Path,
    expected_site_dirs: list[str],
):
    dump_tree = [
        (root, dirs, files)
        for root, dirs, files in site_dump_path_static.walk()
    ]

    assert len(dump_tree) == 1 + len(expected_site_dirs)
    assert set(dump_tree[0][1]) == set(expected_site_dirs)
    assert dump_tree[0][2] == ["site.csv"]

    for site_tree in dump_tree[1:]:
        assert not site_tree[1]
        assert site_tree[2] == ["time_series_om_tidal.csv"]


def test_dump_datetime(
    site_dump_path_static: Path,
    expected_site_dirs: list[str],
):
    if len(expected_site_dirs) < 1:
        pytest.skip("No sites defined in database")

    time_series_energy_wave_path = (
        site_dump_path_static / "site1" / "time_series_om_tidal.csv"
    )
    assert time_series_energy_wave_path.is_file()

    time_series_energy_wave_table = pd.read_csv(time_series_energy_wave_path)

    def is_date(x: datetime) -> bool:
        return x.time() == time(0, 0)

    measure_date = pd.to_datetime(time_series_energy_wave_table["measure_date"])
    check_dates = measure_date.apply(is_date)
    assert check_dates.all()

    def is_time(x: str) -> bool:
        try:
            time.fromisoformat(x)
            return True
        except Exception:
            return False

    measure_time = time_series_energy_wave_table["measure_time"]
    check_times = measure_time.apply(is_time)
    assert check_times.all()


@pytest.fixture
def empty(postgresql_noproc, postgresql_path):
    """
    Given the postgresql process fixture object returns a db connection
    :param psql_proc: postgres process fixture
    :return: psycopg2 connection
    """
    dbname = f"{postgresql_noproc.dbname}_empty"

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
    ]

    with janitor:
        for load_element in pg_load:
            janitor.load(load_element)
        db_config = {
            "host": postgresql_noproc.host,
            "port": postgresql_noproc.port,
            "dbname": dbname,
            "user": postgresql_noproc.user,
            "pwd": postgresql_noproc.password,
        }
        database = get_database(db_config, timeout=60)
        yield database


def test_connect_local(empty):
    assert isinstance(empty._engine, Engine)


@pytest.fixture(scope="module")
def combined_map(component_map, site_map):
    return component_map + site_map


@pytest.fixture(scope="module")
def combined_dump_path_static(tmp_path_factory, static, combined_map):
    tmp_path = tmp_path_factory.mktemp("combined_dump")
    database_to_files(tmp_path, combined_map, static, prefer_csv=True)
    return tmp_path


@pytest.mark.parametrize(
    "table",
    [
        "reference.ports",
        "reference.component_collection_point",
        "project.time_series_om_tidal",
    ],
)
def test_round_trip_convert(
    combined_dump_path_static,
    combined_map,
    static,
    empty,
    table,
):
    schema, table_name = table.split(".")
    before = pd.read_sql_table(table_name, static._engine, schema=schema)

    database_from_files(combined_dump_path_static, combined_map, empty)
    after = pd.read_sql_table(table_name, empty._engine, schema=schema)
    assert_frame_equal(before, after)


def test_id_renumbering(
    tmp_path,
    static,
    empty,
    site_map,
    expected_site_dirs,
):
    if len(expected_site_dirs) < 2:
        pytest.skip("A minimum of two defined sites are required for this test")

    before = pd.read_sql_table(
        "time_series_om_tidal",
        static._engine,
        schema="project",
    )

    database_to_files(tmp_path, site_map, static, prefer_csv=True)

    time_series_energy_wave_path = (
        tmp_path / "site2" / "time_series_om_tidal.csv"
    )
    assert time_series_energy_wave_path.is_file()

    time_series_energy_wave_table = pd.read_csv(time_series_energy_wave_path)
    time_series_energy_wave_table["id"] = (
        time_series_energy_wave_table.index.values
    )
    time_series_energy_wave_table.to_csv(
        time_series_energy_wave_path,
        index=False,
    )

    database_from_files(tmp_path, site_map, empty)
    after = pd.read_sql_table(
        "time_series_om_tidal",
        empty._engine,
        schema="project",
    )

    assert_frame_equal(before, after)


def test_fkey_renumbering(
    tmp_path,
    static,
    empty,
    component_map,
):
    before = pd.read_sql_table(
        "component_collection_point",
        static._engine,
        schema="reference",
    )

    database_to_files(tmp_path, component_map, static, prefer_csv=True)

    # Add a delta to the component_discrete table IDs
    component_discrete_path = (
        tmp_path / "other" / "component" / "component_discrete.csv"
    )
    assert component_discrete_path.is_file()

    component_discrete_table = pd.read_csv(component_discrete_path)
    component_discrete_table["id"] = component_discrete_table["id"] + 10
    component_discrete_table.to_csv(
        component_discrete_path,
        index=False,
    )

    # Add a matching delta to the component_discrete foreign key
    component_collection_point_path = (
        tmp_path
        / "other"
        / "component"
        / "component_discrete"
        / "component_collection_point.csv"
    )
    assert component_collection_point_path.is_file()

    component_collection_point_table = pd.read_csv(
        component_collection_point_path
    )
    component_collection_point_table["fk_component_discrete_id"] = (
        component_collection_point_table["fk_component_discrete_id"] + 10
    )
    component_collection_point_table.to_csv(
        component_collection_point_path,
        index=False,
    )

    database_from_files(tmp_path, component_map, empty)
    after = pd.read_sql_table(
        "component_collection_point",
        empty._engine,
        schema="reference",
    )

    assert_frame_equal(before, after)
