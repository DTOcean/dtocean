from pathlib import Path

import pandas as pd
import pytest
from shapely import from_wkt
from sqlalchemy.engine import Engine

from dtocean_core.menu import DataMenu
from dtocean_core.utils.database import (
    database_to_files,
    get_database,
    get_database_config,
)


# Test for a database connection
def _is_port_open(dbname):
    data_menu = DataMenu()
    return data_menu.check_database(dbname)


local_port_open = _is_port_open("local")
pytestmark = pytest.mark.skipif(
    not local_port_open,
    reason="Can't connect to DB",
)


# Using a py.test fixture to reduce boilerplate and test times.
@pytest.fixture(scope="module")
def local():
    _, db_config = get_database_config()
    database = get_database(db_config["local"], echo=True, timeout=60)
    return database


def test_connect_local(local):
    assert isinstance(local._engine, Engine)


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
def component_dump_path_static(tmp_path_factory, local, component_map):
    tmp_path = tmp_path_factory.mktemp("component_dump")
    database_to_files(tmp_path, component_map, local, prefer_csv=True)
    return tmp_path


@pytest.fixture()
def component_dump_path(tmp_path, local, component_map):
    database_to_files(tmp_path, component_map, local, prefer_csv=True)
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
    assert dump_tree[1][2] == ["component.csv", "ports.csv"]

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


# def test_stored_proceedure(database):
#
#    result = database.call_stored_proceedure(
#                                        "beta.sp_get_farm_by_site_id",
#                                        [1]
#                                        )
#    assert len(result[0]) == 52
