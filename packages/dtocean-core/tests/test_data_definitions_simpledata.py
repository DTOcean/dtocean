
# pylint: disable=protected-access

import pytest

from aneris.control.factory import InterfaceFactory
from dtocean_core.core import AutoQuery, Core
from dtocean_core.data import CoreMetaData
from dtocean_core.data.definitions import SimpleData, SimpleDataColumn


def test_SimpleData_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures
    
    assert "SimpleData" in all_objs.keys()

@pytest.mark.parametrize("tinput, ttype", [(1, "int"),
                                           ("hello", "str"),
                                           (True, "bool"),
                                           (0.5, "float")])
def test_SimpleData(tinput, ttype):
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "types": [ttype]})
    
    test = SimpleData()
    
    a = test.get_data(tinput, meta)
    b = test.get_value(a)
    
    assert b == tinput


@pytest.mark.parametrize("tinput, ttype", [(1., "int"),
                                           (True, "str"),
                                           ("False", "bool"),
                                           (2, "float")])
def test_SimpleData_get_data_coerce(tinput, ttype):
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "types": [ttype]})
    
    test = SimpleData()
    a = test.get_data(tinput, meta)
    
    assert str(type(a)) == "<type '{}'>".format(ttype)


def test_SimpleData_get_value_None():
    
    test = SimpleData()
    result = test.get_value(None)
    
    assert result is None


@pytest.mark.parametrize("tinput, ttype", [(1, "int"),
                                           (1., "float")])
def test_SimpleData_minimum_equals(tinput, ttype):
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "types": [ttype],
                         "minimum_equals": [2]})
    
    test = SimpleData()
    
    with pytest.raises(ValueError) as excinfo:
        test.get_data(tinput, meta)
    
    assert "less than minimum" in str(excinfo)


@pytest.mark.parametrize("tinput, ttype", [(1, "int"),
                                           (1., "float")])
def test_SimpleData_minimums(tinput, ttype):
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "types": [ttype],
                         "minimums": [1]})
    
    test = SimpleData()
    
    with pytest.raises(ValueError) as excinfo:
        test.get_data(tinput, meta)
    
    assert "less than or equal to minimum" in str(excinfo)


@pytest.mark.parametrize("tinput, ttype", [(1, "int"),
                                           (1., "float")])
def test_SimpleData_maximum_equals(tinput, ttype):
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "types": [ttype],
                         "maximum_equals": [0]})
    
    test = SimpleData()
    
    with pytest.raises(ValueError) as excinfo:
        test.get_data(tinput, meta)
    
    assert "greater than maximum" in str(excinfo)


@pytest.mark.parametrize("tinput, ttype", [(1, "int"),
                                           (1., "float")])
def test_SimpleData_maximums(tinput, ttype):
    
    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "types": [ttype],
                         "maximums": [1]})
    
    test = SimpleData()
    
    with pytest.raises(ValueError) as excinfo:
        test.get_data(tinput, meta)
    
    assert "greater than or equal to maximum" in str(excinfo)

@pytest.mark.parametrize("left, right", [(1, 1),
                                         ("a", "a"),
                                         (False, False),
                                         (2.1, 2.1)])
def test_SimpleData_equals(left, right):
    
    assert SimpleData.equals(left, right)


@pytest.mark.parametrize("left, right", [(1, 2),
                                         ("a", "b"),
                                         (False, True),
                                         (2.1, 2.101)])
def test_SimpleData_not_equals(left, right):
    
    assert not SimpleData.equals(left, right)


def test_SimpleDataColumn_available():
    
    new_core = Core()
    all_objs = new_core.control._store._structures
    
    assert "SimpleDataColumn" in all_objs.keys()


@pytest.mark.parametrize("tinput, ttype", [(1, "int"),
                                           ("hello", "str"),
                                           (True, "bool"),
                                           (0.5, "float")])
def test_SimpleDataColumn_auto_db(mocker, tinput, ttype):
    
    mock_list = [tinput]
    
    mocker.patch('dtocean_core.data.definitions.get_one_from_column',
                 return_value=mock_list,
                 autospec=True)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "tables": ["mock.mock", "value"],
                         "types": [ttype]})
    
    test = SimpleDataColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
    result = test.get_data(query.data.result, meta)
    
    assert result == tinput


def test_SimpleDataColumn_auto_db_empty(mocker):
    
    mock_list = None
    
    mocker.patch('dtocean_core.data.definitions.get_one_from_column',
                 return_value=mock_list,
                 autospec=True)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "tables": ["mock.mock", "value"],
                         "types": ["float"]})

    test = SimpleDataColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None


def test_SimpleDataColumn_auto_db_none(mocker):
    
    mock_list = [None]
        
    mocker.patch('dtocean_core.data.definitions.get_one_from_column',
                 return_value=mock_list,
                 autospec=True)

    meta = CoreMetaData({"identifier": "test",
                         "structure": "test",
                         "title": "test",
                         "tables": ["mock.mock", "value"]})
    
    test = SimpleDataColumn()
    
    query_factory = InterfaceFactory(AutoQuery)
    QueryCls = query_factory(meta, test)
    
    query = QueryCls()
    query.meta.result = meta
    
    query.connect()
        
    assert query.data.result is None
