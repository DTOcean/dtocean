import datetime
import os

import pandas as pd
import pytest
from shapely import Polygon, get_srid, set_srid
from shapely.geometry import Point

from dtocean_core.utils.config import init_config
from dtocean_core.utils.database import (
    bathy_records_to_strata,
    check_dict,
    convert_array,
    convert_bool,
    convert_geo,
    convert_time,
    draw_map,
    filter_map,
    get_database_config,
    get_offset_map,
    get_table_map,
    query_builder,
    revert_array,
    revert_bool,
    revert_geo,
)

this_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(this_dir, "..", "test_data")


def test_bathy_records_to_strata(test_data_path):
    df = pd.read_csv(test_data_path / "bathy_test_good.csv")
    points = []
    for x, y in zip(df["x"], df["y"]):
        point = Point(x, y)
        points.append(point.wkb_hex)

    df["utm_point"] = points
    df = df.drop("x", axis=1)
    df = df.drop("y", axis=1)

    records = df.to_records()
    raw = bathy_records_to_strata(records)

    assert raw is not None
    assert set(raw["values"].keys()) == set(["depth", "sediment"])


def test_bathy_records_to_strata_fail(test_data_path):
    df = pd.read_csv(test_data_path / "bathy_test_bad.csv")
    points = []
    for x, y in zip(df["x"], df["y"]):
        point = Point(x, y)
        points.append(point.wkb_hex)

    df["utm_point"] = points
    df = df.drop("x", axis=1)
    df = df.drop("y", axis=1)

    records = df.to_records()

    with pytest.raises(ValueError):
        bathy_records_to_strata(records)


def test_query_builder():
    result = query_builder(
        ["device", "device_shared"],
        ["id", "id"],
        ["fk_device_id"],
        [{"table#": 0, "value": 1}, {"table#": 1, "value": 2}],
        "project",
    )

    results = result.split("\n")

    assert results[1] == "FROM project.device_shared t1"
    assert results[2] == "JOIN project.device t0 ON t0.id = t1.fk_device_id"
    assert results[3] == "WHERE t0.id = 1 AND t1.id = 2;"


def test_query_builder_basic():
    result = query_builder(["device"])

    assert result == "SELECT * FROM device;"


def test_query_builder_no_schema():
    result = query_builder(
        ["device", "device_shared"],
        ["id", "id"],
        ["fk_device_id"],
        [{"table#": 0, "value": 1}, {"table#": 1, "value": 2}],
        "project",
    )

    results = result.split("\n")

    assert results[1] == "FROM project.device_shared t1"
    assert results[2] == "JOIN project.device t0 ON t0.id = t1.fk_device_id"
    assert results[3] == "WHERE t0.id = 1 AND t1.id = 2;"


def test_convert_array():
    df_dict = {"A": [[1, 2, 3, 4], None], "B": [1, 2]}
    df = pd.DataFrame(df_dict)

    result = convert_array(df, ["A"])

    assert result["A"].iloc[0] == "{1, 2, 3, 4}"
    assert result["A"].iloc[1] is None


def test_revert_array():
    df_dict = {"A": ["{1, 2, 3, 4}", None], "B": [1, 2]}
    df = pd.DataFrame(df_dict)

    result = revert_array(df, ["A"])

    assert result["A"].iloc[0] == [1, 2, 3, 4]
    assert result["A"].iloc[1] is None


def test_convert_bool():
    df_dict = {"A": [True, False, None], "B": [1, 2, 3]}
    df = pd.DataFrame(df_dict)

    result = convert_bool(df, ["A"])

    assert result["A"].iloc[0] == "yes"
    assert result["A"].iloc[1] == "no"
    assert result["A"].iloc[2] is None


def test_revert_bool():
    df_dict = {"A": ["yes", "no", None], "B": [1, 2, 3]}
    df = pd.DataFrame(df_dict)

    result = revert_bool(df, ["A"])

    assert result["A"].iloc[0] is True
    assert result["A"].iloc[1] is False
    assert result["A"].iloc[2] is None


def test_convert_geo():
    x = Point(0, 0)

    df_dict = {"A": [x, None], "B": [1, 2]}
    df = pd.DataFrame(df_dict)

    result = convert_geo(df, ["A"])

    assert result["A"].iloc[0] == "POINT (0 0)"
    assert result["A"].iloc[1] is None


def test_convert_geo_SRID():
    x = set_srid(Point(0, 0), 1)

    df_dict = {"A": [x, None], "B": [1, 2]}
    df = pd.DataFrame(df_dict)
    result = convert_geo(df, ["A"])

    assert result["A"].iloc[0] == "SRID=1;POINT (0 0)"
    assert result["A"].iloc[1] is None


def test_revert_geo():
    df_dict = {"A": ["POINT (0 0)", None], "B": [1, 2]}
    df = pd.DataFrame(df_dict)

    result = revert_geo(df, ["A"])

    assert result["A"].iloc[0] == Point(0, 0)
    assert result["A"].iloc[1] is None


def test_revert_geo_SRID():
    df_dict = {
        "A": [
            "SRID=4326;POLYGON ((-124.15 40.75, -124.375 40.75, "
            "-124.375 40.925, -124.15 40.925, -124.15 40.75))",
            None,
        ],
        "B": [1, 2],
    }
    df = pd.DataFrame(df_dict)
    result = revert_geo(df, ["A"])

    polygon = Polygon(
        (
            (-124.15, 40.75),
            (-124.375, 40.75),
            (-124.375, 40.925),
            (-124.15, 40.925),
            (-124.15, 40.75),
        )
    )
    assert result["A"].iloc[0] == polygon
    assert get_srid(result["A"].iloc[0]) == 4326
    assert result["A"].iloc[1] is None


def test_convert_time():
    x = datetime.datetime(2018, 1, 1, 12, 31, 5)

    df_dict = {"A": [x, None], "B": [1, 2]}
    df = pd.DataFrame(df_dict)
    df2 = df.astype(object)
    df2 = df2.where(df2.notnull(), None)

    result = convert_time(df2, ["A"])

    assert result["A"].iloc[0] == "12:31:05"
    assert result["A"].iloc[1] is None


def test_check_dict():
    table_dict = {"table": "test"}
    result = check_dict(table_dict)

    expected_keys = [
        "array",
        "autokey",
        "bool",
        "children",
        "date",
        "dummy",
        "fkeys",
        "geo",
        "join",
        "pkey",
        "schema",
        "stripf",
        "table",
        "time",
    ]
    assert set(result.keys()) == set(expected_keys)

    autokey = result.pop("autokey")
    dummy = result.pop("dummy")
    pkey = result.pop("pkey")
    stripf = result.pop("stripf")
    table = result.pop("table")

    assert (autokey or dummy or stripf) is False
    assert pkey == "id"
    assert table == "test"
    assert set(result.values()) == set([None])


def test_check_dict_no_table_key():
    with pytest.raises(KeyError):
        check_dict({})


def test_get_offset_map():
    df = pd.DataFrame(
        {
            "id": {0: 1, 1: 2, 2: 3, 3: 4, 4: 5},
        }
    )
    test = get_offset_map(df, "id", 10)
    assert test == {1: 10, 2: 11, 3: 12, 4: 13, 5: 14}


def test_get_table_map():
    result = get_table_map()
    assert isinstance(result, list)


def test_filter_map():
    table_list = get_table_map()
    result = filter_map(table_list, "device")

    assert result is not None
    assert result["table"] == "device"


def test_filter_map_parent():
    table_list = get_table_map()
    result = filter_map(table_list, "device_shared")

    assert result is not None
    assert result["table"] == "device"


def test_filter_map_two_parents():
    table_list = get_table_map()
    result = filter_map(table_list, "sub_systems_access")

    assert result is not None
    assert result["table"] == "device"


def test_draw_map():
    table_list = get_table_map()
    result = draw_map(table_list)

    assert result


def test_get_user_database_config_empty(mocker, tmp_path):
    # Make a source directory without files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.utils.database.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    useryaml, config = get_database_config()

    assert not os.path.isfile(useryaml.get_config_path())
    assert isinstance(config, dict)


def test_get_user_database_config(mocker, tmp_path):
    # Make a source directory with some files
    config_tmpdir = tmp_path / "config"
    config_tmpdir.mkdir()

    mocker.patch(
        "dtocean_core.utils.config.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    mocker.patch(
        "dtocean_core.utils.database.UserDataPath",
        return_value=config_tmpdir,
        autospec=True,
    )

    init_config(database=True)
    useryaml, config = get_database_config()

    assert os.path.isfile(useryaml.get_config_path())
    assert isinstance(config, dict)
