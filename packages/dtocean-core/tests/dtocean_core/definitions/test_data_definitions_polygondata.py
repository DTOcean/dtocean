import matplotlib.pyplot as plt
import pytest
import shapefile
from geoalchemy2.elements import WKTElement
from mdo_engine.control.factory import InterfaceFactory
from shapely.geometry import Polygon

from dtocean_core.core import (
    AutoFileInput,
    AutoFileOutput,
    AutoPlot,
    AutoQuery,
    Core,
)
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import (
    PointData,
    PolygonData,
    PolygonDataColumn,
)


def test_PolygonData_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "PolygonData" in all_objs.keys()


def test_PolygonData():
    meta = CoreMetaData(
        {"identifier": "test", "structure": "test", "title": "test"}
    )

    raw = [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]

    test = PolygonData()
    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert b is not None
    assert b.exterior.coords[0][0] == 0.0
    assert b.exterior.coords[1][1] == 1.0

    raw = [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (2.0, 2.0, 2.0)]

    a = test.get_data(raw, meta)
    b = test.get_value(a)

    assert b is not None
    assert b.exterior.has_z
    assert b.exterior.coords[0][0] == 0.0
    assert b.exterior.coords[1][1] == 1.0
    assert b.exterior.coords[2][2] == 2.0  # type: ignore

    raw = [(0.0, 0.0, 0.0, 0.0), (1.0, 1.0, 1.0, 1.0), (2.0, 2.0, 2.0, 2.0)]

    with pytest.raises(ValueError):
        test.get_data(raw, meta)


def test_get_None():
    test = PolygonData()
    result = test.get_value(None)

    assert result is None


@pytest.mark.parametrize(
    "left, right",
    [
        (
            [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)],
            [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)],
        ),
        (
            [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (2.0, 2.0, 2.0)],
            [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (2.0, 2.0, 2.0)],
        ),
    ],
)
def test_PolygonData_equals(left, right):
    left_poly = Polygon(left)
    right_poly = Polygon(right)

    assert PolygonData.equals(left_poly, right_poly)


@pytest.mark.parametrize(
    "left, right",
    [
        (
            [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)],
            [(0.0, 0.0), (1.0, 0.0), (2.0, 2.0)],
        ),
        (
            [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (2.0, 2.0, 2.0)],
            [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (2.0, 0.0, 2.0)],
        ),
    ],
)
def test_PolygonData_not_equals(left, right):
    left_poly = Polygon(left)
    right_poly = Polygon(right)

    assert not PolygonData.equals(left_poly, right_poly)


@pytest.mark.parametrize("fext", [".csv", ".shp", ".xls", ".xlsx"])
def test_PolygonData_auto_file(tmpdir, fext):
    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_str = str(test_path)

    raws = [
        [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)],
        [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (2.0, 2.0, 2.0)],
    ]

    ztests = [False, True]

    for raw, ztest in zip(raws, ztests):
        meta = CoreMetaData(
            {"identifier": "test", "structure": "test", "title": "test"}
        )

        test = PolygonData()

        fout_factory = InterfaceFactory(AutoFileOutput)
        FOutCls = fout_factory(meta, test)

        fout = FOutCls()
        fout._path = test_path_str
        fout.data.result = test.get_data(raw, meta)

        fout.connect()

        assert len(tmpdir.listdir()) == 1

        fin_factory = InterfaceFactory(AutoFileInput)
        FInCls = fin_factory(meta, test)

        fin = FInCls()
        fin._path = test_path_str

        fin.connect()
        result = test.get_data(fin.data.result, meta)

        assert result.exterior.coords[0][0] == 0.0
        assert result.exterior.coords[1][1] == 1.0
        assert result.has_z == ztest


def test_PolygonData_auto_file_wrong_shape_type(tmpdir):
    test_path = tmpdir.mkdir("sub").join("test.shp")
    test_path_str = str(test_path)

    raw = (0.0, 0.0)

    meta = CoreMetaData(
        {"identifier": "test", "structure": "test", "title": "test"}
    )

    src_shape = PointData()

    fout_factory = InterfaceFactory(AutoFileOutput)
    FOutCls = fout_factory(meta, src_shape)

    fout = FOutCls()
    fout._path = test_path_str
    fout.data.result = src_shape.get_data(raw, meta)

    fout.connect()

    assert len(tmpdir.listdir()) == 1

    test = PolygonData()

    fin_factory = InterfaceFactory(AutoFileInput)
    FInCls = fin_factory(meta, test)

    fin = FInCls()
    fin._path = test_path_str

    with pytest.raises(ValueError) as excinfo:
        fin.connect()

    assert "imported shapefile must have" in str(excinfo)


def test_PolygonData_auto_file_too_many_shapes(tmpdir):
    test_path = tmpdir.mkdir("sub").join("test.shp")
    test_path_str = str(test_path)

    with shapefile.Writer(test_path_str) as shp:
        shp.field("name", "C")
        shp.poly([[(0.0, 0.0), (1.0, 1.0)]])
        shp.record("polygon1")
        shp.poly([[(2.0, 2.0), (3.0, 3.0)]])
        shp.record("polygon2")

    assert len(tmpdir.listdir()) == 1

    meta = CoreMetaData(
        {"identifier": "test", "structure": "test", "title": "test"}
    )

    test = PolygonData()

    fin_factory = InterfaceFactory(AutoFileInput)
    FInCls = fin_factory(meta, test)

    fin = FInCls()
    fin._path = test_path_str

    with pytest.raises(ValueError) as excinfo:
        fin.connect()

    assert "Only one shape may be defined" in str(excinfo)


def test_PolygonData_auto_file_too_many_parts(tmpdir):
    test_path = tmpdir.mkdir("sub").join("test.shp")
    test_path_str = str(test_path)

    with shapefile.Writer(test_path_str) as shp:
        shp.field("name", "C")
        shp.poly(
            [
                [
                    [113, 24],
                    [112, 32],
                    [117, 36],
                    [122, 37],
                    [118, 20],
                ],  # poly 1
                [[116, 29], [116, 26], [119, 29], [119, 32]],  # hole 1
                [[15, 2], [17, 6], [22, 7]],  # poly 2
            ]
        )
        shp.record("polygon1")

    assert len(tmpdir.listdir()) == 1

    meta = CoreMetaData(
        {"identifier": "test", "structure": "test", "title": "test"}
    )

    test = PolygonData()

    fin_factory = InterfaceFactory(AutoFileInput)
    FInCls = fin_factory(meta, test)

    fin = FInCls()
    fin._path = test_path_str

    with pytest.raises(ValueError) as excinfo:
        fin.connect()

    assert "Only polygons with exterior coordinates" in str(excinfo)


def test_PolygonData_auto_plot(tmpdir):
    meta = CoreMetaData(
        {"identifier": "test", "structure": "test", "title": "test"}
    )

    raw = [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (2.0, 2.0, 2.0)]

    test = PolygonData()

    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)

    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()

    assert len(plt.get_fignums()) == 1
    plt.close("all")


def test_PolygonDataColumn_available():
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "PolygonDataColumn" in all_objs.keys()


def test_PolygonDataColumn_auto_db(mocker):
    raws = [
        WKTElement("POLYGON ((0 0, 1 0, 1 1, 0 0))"),
        WKTElement("POLYGON ((0 0 0, 1 0 0, 1 1 0, 0 0 0))"),
    ]

    for raw in raws:
        mock_list = [raw]

        mocker.patch(
            "dtocean_core.data.definitions.get_one_from_column",
            return_value=mock_list,
        )

        meta = CoreMetaData(
            {
                "identifier": "test",
                "structure": "test",
                "title": "test",
                "tables": ["mock.mock", "position"],
            }
        )

        test = PolygonDataColumn()

        query_factory = InterfaceFactory(AutoQuery)
        QueryCls = query_factory(meta, test)

        query = QueryCls()
        query.meta.result = meta

        query.connect()
        result = test.get_data(query.data.result, meta)

        assert result.exterior.coords[0][0] == 0.0
        assert result.exterior.coords[1][0] == 1.0


def test_PolygonDataColumn_auto_db_empty(mocker):
    mock_list = None

    mocker.patch(
        "dtocean_core.data.definitions.get_one_from_column",
        return_value=mock_list,
        autospec=True,
    )

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "tables": ["mock.mock", "position"],
        }
    )

    test = PolygonDataColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None


def test_PolygonDataColumn_auto_db_none(mocker):
    mock_list = [None]

    mocker.patch(
        "dtocean_core.data.definitions.get_one_from_column",
        return_value=mock_list,
        autospec=True,
    )

    meta = CoreMetaData(
        {
            "identifier": "test",
            "structure": "test",
            "title": "test",
            "tables": ["mock.mock", "position"],
        }
    )

    test = PolygonDataColumn()

    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)

    query = QueryCls()
    query.meta.result = meta

    query.connect()

    assert query.data.result is None
