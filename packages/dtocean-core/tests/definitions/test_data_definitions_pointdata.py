import pytest

import shapefile
import matplotlib.pyplot as plt
from geoalchemy2.elements import WKTElement
from shapely.geometry import Point

from mdo_engine.control.factory import InterfaceFactory
from dtocean_core.core import (AutoFileInput,
                               AutoFileOutput,
                               AutoPlot,
                               AutoQuery,
                               Core)
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import PointData, PointDataColumn, PointList


def test_PointData_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "PointData" in all_objs.keys()


def test_PointData():

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    test = PointData()
    
    raw = (0, 1)
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert b.x == 0
    assert b.y == 1
            
    raw = (0, 1, -1)
    a = test.get_data(raw, meta)
    b = test.get_value(a)
    
    assert b.x == 0
    assert b.y == 1 
    assert b.z == -1
            
    raw = (0, 1, -1, 1)
    
    with pytest.raises(ValueError):
        test.get_data(raw, meta)


def test_get_None():
    
    test = PointData()
    result = test.get_value(None)
    
    assert result is None


@pytest.mark.parametrize("left, right", [([0, 1], [0, 1]),
                                         ([0, 1, 1], [0, 1, 1])])
def test_PointData_equals(left, right):
    
    left_point = Point(*left)
    right_point = Point(*right)
    
    assert PointData.equals(left_point, right_point)


@pytest.mark.parametrize("left, right", [([0, 1], [0, 2]),
                                         ([0, 1, 1], [1, 1, 1])])
def test_PointData_not_equals(left, right):
    
    left_point = Point(*left)
    right_point = Point(*right)
    
    assert not PointData.equals(left_point, right_point)


@pytest.mark.parametrize("fext", [".csv", ".shp", ".xls", ".xlsx"])
def test_PointData_auto_file(tmpdir, fext):
    
    test_path = tmpdir.mkdir("sub").join("test{}".format(fext))
    test_path_str = str(test_path)
    
    raws = [(0, 1), (0, 1, -1)]
    ztests = [False, True]
    
    for raw, ztest in zip(raws, ztests):
        
        meta = CoreMetaData({"identifier": "test",
                             "structure": "test",
                             "title": "test"})
        
        test = PointData()
        
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
        
        assert result.x == 0
        assert result.y == 1
        assert result.has_z == ztest


def test_PointData_auto_file_wrong_shape_type(tmpdir):
    
    test_path = tmpdir.mkdir("sub").join("test.shp")
    test_path_str = str(test_path)
    
    raw = [(0., 0.),
           (1., 1.),
           (2., 2.)]
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    src_shape = PointList()
    
    fout_factory = InterfaceFactory(AutoFileOutput)
    FOutCls = fout_factory(meta, src_shape)
    
    fout = FOutCls()
    fout._path = test_path_str
    fout.data.result = src_shape.get_data(raw, meta)
    
    fout.connect()
    
    assert len(tmpdir.listdir()) == 1
    
    test = PointData()
    
    fin_factory = InterfaceFactory(AutoFileInput)
    FInCls = fin_factory(meta, test)
    
    fin = FInCls()
    fin._path = test_path_str
    
    with pytest.raises(ValueError) as excinfo:
        fin.connect()
    
    assert "imported shapefile must have" in str(excinfo)


def test_PointData_auto_file_too_many_shapes(tmpdir):
    
    test_path = tmpdir.mkdir("sub").join("test.shp")
    test_path_str = str(test_path)
    
    with shapefile.Writer(test_path_str) as shp:
        shp.field('name', 'C')
        shp.point(0, 0)
        shp.record('point1')
        shp.point(1, 1)
        shp.record('point2')
    
    assert len(tmpdir.listdir()) == 1
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test"})
    
    test = PointData()
    
    fin_factory = InterfaceFactory(AutoFileInput)
    FInCls = fin_factory(meta, test)
    
    fin = FInCls()
    fin._path = test_path_str
    
    with pytest.raises(ValueError) as excinfo:
        fin.connect()
    
    assert "Only one shape may be defined" in str(excinfo)


def test_PointData_auto_plot(tmpdir):
        
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "labels": ["ex", "why"],
                         "units": ["m", "s"]})
    
    raw = (0, 1)
    
    test = PointData()
    
    fout_factory = InterfaceFactory(AutoPlot)
    PlotCls = fout_factory(meta, test)
    
    plot = PlotCls()
    plot.data.result = test.get_data(raw, meta)
    plot.meta.result = meta

    plot.connect()
    
    assert len(plt.get_fignums()) == 1
    plt.close("all")


def test_PointDataColumn_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures

    assert "PointDataColumn" in all_objs.keys()
    

def test_PointDataColumn_auto_db(mocker):
    
    raws = [WKTElement("POINT (0 1)"), WKTElement("POINT (0 1 -1)")]
    
    for raw in raws:

        mock_list = [raw]
        
        mocker.patch('dtocean_core.data.definitions.get_one_from_column',
                     return_value=mock_list,
                     autospec=True)
    
        meta = CoreMetaData({"identifier": "test",
                             "structure": "test",
                             "title": "test",
                             "tables": ["mock.mock", "position"]})
        
        test = PointDataColumn()
        
        query_factory = InterfaceFactory(AutoQuery)
        QueryCls = query_factory(meta, test)
        
        query = QueryCls()
        query.meta.result = meta
        
        query.connect()
        result = test.get_data(query.data.result, meta)
            
        assert result.x == 0
        assert result.y == 1


def test_PointDataColumn_auto_db_empty(mocker):
    
    mock_list = None
        
    mocker.patch('dtocean_core.data.definitions.get_one_from_column',
                 return_value=mock_list,
                 autospec=True)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "tables": ["mock.mock", "position"]})

    test = PointDataColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None


def test_PointDataColumn_auto_db_none(mocker):
    
    mock_list = [None]
        
    mocker.patch('dtocean_core.data.definitions.get_one_from_column',
                 return_value=mock_list,
                 autospec=True)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "tables": ["mock.mock", "position"]})
    
    test = PointDataColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None

