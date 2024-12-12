# -*- coding: utf-8 -*-
"""py.test tests on control.data module

.. moduleauthor:: Mathew Topper <mathew.topper@tecnalia.com>
"""

# pylint: disable=protected-access

import os
import pickle

# import sys
import shutil
from copy import deepcopy

import pytest

from mdo_engine.boundary.data import SerialBox
from mdo_engine.control.data import (
    DataStorage,
    DataValidation,
    _check_valid_datastate,
)
from mdo_engine.entity.data import Data, DataCatalog, DataPool, DataState

# from mdo_engine.utilities.files import mkdir_p
# from polite_config.paths import user_data_dir, module_dir
from . import data_plugins as data
from . import user_plugins as user_data


def test_discover_plugins():
    super_cls = "DataDefinition"

    validation = DataValidation()

    # Discover the available classes and load the instances
    cls_map = validation._discover_plugins(user_data, super_cls)

    assert "testDefinition" in cls_map.keys()


# def test_update_data_catalog_from_definitions():
#
#    '''Test retrieving all variables from data catalog definition files'''
#
#    # Test using files in AppData
#    test_app_dir = "yaml"
#    test_file_dir = "user_data"
#    test_file_name = "test.yaml"
#
#    app_path = user_data_dir("mdo_engine", "DTOcean")
#    data_path = os.path.join(app_path, test_app_dir)
#    mkdir_p(data_path)
#    current_module = sys.modules[__name__]
#    test_yaml_file = os.path.join(module_dir(current_module),
#                                  test_file_dir,
#                                  test_file_name)
#    dst_path = os.path.join(data_path, test_file_name)
#    shutil.copyfile(test_yaml_file, dst_path)
#
#    catalog = DataCatalog()
#    validation = DataValidation()
#    catalog = validation.update_data_catalog_from_definitions(catalog,
#                                                              user_data)
#    all_vars = catalog.get_variable_identifiers()
#
#    shutil.rmtree(data_path)
#
#    assert 'my:test:variable2' in all_vars


def test_get_valid_variables():
    """Test comparing variables in the interfaces to the data catalog"""

    all_vars = ["my:test:variable", "site:wave:dir"]

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)

    valid_vars = validation.get_valid_variables(catalog, all_vars)

    assert "my:test:variable" in valid_vars


def test_create_new_datastate():
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    state = data_store.create_new_datastate("test")

    assert isinstance(state, DataState)
    assert state.get_level() == "test"


def test_create_new_data():
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = data_store.create_new_datastate("test")

    # Get the meta data from the catalog
    metadata = catalog.get_metadata("Technology:Common:DeviceType")

    data_store.create_new_data(pool, state, catalog, "Tidal", metadata)
    new_data_value = data_store.get_data_value(
        pool, state, "Technology:Common:DeviceType"
    )

    assert new_data_value == "Tidal"


def test_create_new_none_data():
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = data_store.create_new_datastate("test")

    # Get the meta data from the catalog
    metadata = catalog.get_metadata("Technology:Common:DeviceType")

    data_store.create_new_data(pool, state, catalog, None, metadata)

    with pytest.raises(ValueError):
        data_store.get_data_value(pool, state, "Technology:Common:DeviceType")

    assert len(pool) == 0


def test_remove_data_from_state():
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = data_store.create_new_datastate("test")

    # Get the meta data from the catalog
    metadata = catalog.get_metadata("Technology:Common:DeviceType")

    data_store.create_new_data(pool, state, catalog, "Tidal", metadata)
    new_data_value = data_store.get_data_value(
        pool, state, "Technology:Common:DeviceType"
    )

    assert new_data_value == "Tidal"

    data_store.remove_data_from_state(
        pool, state, "Technology:Common:DeviceType"
    )

    assert data_store.has_data(state, "Technology:Common:DeviceType") is False
    assert state.has_index("Technology:Common:DeviceType") is False
    assert len(pool) == 0


def test_remove_none_data_from_state():
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = data_store.create_new_datastate("test")

    # Get the meta data from the catalog
    metadata = catalog.get_metadata("Technology:Common:DeviceType")

    data_store.create_new_data(pool, state, catalog, None, metadata)

    assert data_store.has_data(state, "Technology:Common:DeviceType") is False
    assert state.has_index("Technology:Common:DeviceType") is True
    assert len(pool) == 0

    data_store.remove_data_from_state(
        pool, state, "Technology:Common:DeviceType"
    )

    assert data_store.has_data(state, "Technology:Common:DeviceType") is False
    assert state.has_index("Technology:Common:DeviceType") is False
    assert len(pool) == 0


def test_copy_datastate():
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = data_store.create_new_datastate("test")

    # Get the meta data from the catalog
    metadata = catalog.get_metadata("Technology:Common:DeviceType")

    data_store.create_new_data(pool, state, catalog, "Tidal", metadata)
    data_value = data_store.get_data_value(
        pool, state, "Technology:Common:DeviceType"
    )
    data_index = state.get_index("Technology:Common:DeviceType")

    assert data_value == "Tidal"
    assert len(pool) == 1
    assert pool._links[data_index] == 1

    new_state = data_store.copy_datastate(pool, state)
    new_data_value = data_store.get_data_value(
        pool, new_state, "Technology:Common:DeviceType"
    )

    assert isinstance(new_state, DataState)
    assert new_state is not state
    assert new_state.get_level() == "test"
    assert new_data_value == "Tidal"
    assert len(pool) == 1
    assert pool._links[data_index] == 2


def test_import_datastate_from_clone():
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = data_store.create_new_datastate("test")

    # Get the meta data from the catalog
    metadata = catalog.get_metadata("Technology:Common:DeviceType")

    data_store.create_new_data(pool, state, catalog, "Tidal", metadata)
    data_value = data_store.get_data_value(
        pool, state, "Technology:Common:DeviceType"
    )
    data_index = state.get_index("Technology:Common:DeviceType")

    assert data_value == "Tidal"
    assert len(pool) == 1
    assert pool._links[data_index] == 1

    # Clone the pool
    src_pool = deepcopy(pool)

    assert len(src_pool) == 1
    assert src_pool._links[data_index] == 1

    new_state = data_store.import_datastate(src_pool, pool, state)
    new_data_value = data_store.get_data_value(
        pool, new_state, "Technology:Common:DeviceType"
    )

    assert isinstance(new_state, DataState)
    assert new_state is not state
    assert new_state.get_level() == "test"
    assert new_data_value == "Tidal"
    assert len(pool) == 1
    assert pool._links[data_index] == 2


def test_import_datastate_from_new():
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)

    pool = DataPool()
    state = data_store.create_new_datastate("test")

    # Get the meta data from the catalog
    metadata = catalog.get_metadata("Technology:Common:DeviceType")

    data_store.create_new_data(pool, state, catalog, "Tidal", metadata)
    data_value = data_store.get_data_value(
        pool, state, "Technology:Common:DeviceType"
    )
    data_index = state.get_index("Technology:Common:DeviceType")

    assert data_value == "Tidal"
    assert len(pool) == 1
    assert pool._links[data_index] == 1

    # Create a new pool
    src_pool = DataPool()
    src_state = data_store.create_new_datastate("test2")

    # Get the meta data from the catalog
    metadata = catalog.get_metadata("Technology:Common:DeviceType")

    data_store.create_new_data(src_pool, src_state, catalog, "Wave", metadata)
    src_data_value = data_store.get_data_value(
        src_pool, src_state, "Technology:Common:DeviceType"
    )
    src_data_index = src_state.get_index("Technology:Common:DeviceType")

    assert src_data_value == "Wave"
    assert len(src_pool) == 1
    assert src_pool._links[src_data_index] == 1

    new_state = data_store.import_datastate(src_pool, pool, src_state)
    new_data_value = data_store.get_data_value(
        pool, new_state, "Technology:Common:DeviceType"
    )

    assert isinstance(new_state, DataState)
    assert new_state is not state
    assert new_state.get_level() == "test2"
    assert new_data_value == "Wave"
    assert len(pool) == 2
    assert pool._links[data_index] == 1


def test_serialise_data(tmpdir):
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = DataState("test")
    data_store.discover_structures(data)

    metadata = catalog.get_metadata("Technology:Common:DeviceType")
    data_store.create_new_data(pool, state, catalog, "Tidal", metadata)

    data_index = state.get_index("Technology:Common:DeviceType")

    data_store.serialise_data(pool, [data_index], str(tmpdir))

    data_box = pool.get(data_index)

    assert isinstance(data_box, SerialBox)

    data_path = data_box.load_dict["file_path"]

    assert os.path.isfile(data_path)


def test_serialise_data_warns(tmpdir, monkeypatch):
    def mockerror(a, b):
        raise Exception

    monkeypatch.setattr(
        "mdo_engine.boundary.data.Structure.save_value", mockerror
    )

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = DataState("test")
    data_store.discover_structures(data)

    metadata = catalog.get_metadata("Technology:Common:DeviceType")
    data_store.create_new_data(pool, state, catalog, "Tidal", metadata)

    data_index = state.get_index("Technology:Common:DeviceType")

    data_store.serialise_data(pool, [data_index], str(tmpdir))

    still_data = pool.get(data_index)

    assert isinstance(still_data, Data)


def test_serialise_data_exception(tmpdir, monkeypatch):
    def mockerror(a, b):
        raise Exception

    monkeypatch.setattr(
        "mdo_engine.boundary.data.Structure.save_value", mockerror
    )

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = DataState("test")
    data_store.discover_structures(data)

    metadata = catalog.get_metadata("Technology:Common:DeviceType")
    data_store.create_new_data(pool, state, catalog, "Tidal", metadata)

    data_index = state.get_index("Technology:Common:DeviceType")

    with pytest.raises(Exception):
        data_store.serialise_data(
            pool, [data_index], str(tmpdir), warn_save=False
        )


def test_deserialise_data(tmpdir):
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = DataState("test")
    data_store.discover_structures(data)

    metadata = catalog.get_metadata("Technology:Common:DeviceType")
    data_store.create_new_data(pool, state, catalog, "Tidal", metadata)

    data_index = state.get_index("Technology:Common:DeviceType")
    new_data = pool.get(data_index)

    data_store.serialise_data(pool, [data_index], str(tmpdir))

    data_store.deserialise_data(catalog, pool, [data_index])
    new_data = pool.get(data_index)

    assert isinstance(new_data, Data)
    assert new_data._data == "Tidal"


def test_serialise_data_root(tmpdir):
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = DataState("test")
    data_store.discover_structures(data)

    metadata = catalog.get_metadata("Technology:Common:DeviceType")
    data_store.create_new_data(pool, state, catalog, "Tidal", metadata)

    data_index = state.get_index("Technology:Common:DeviceType")

    data_store.serialise_data(
        pool, [data_index], str(tmpdir), root_dir=str(tmpdir)
    )

    data_box = pool.get(data_index)

    assert isinstance(data_box, SerialBox)

    data_path = os.path.join(str(tmpdir), data_box.load_dict["file_path"])

    assert os.path.isfile(data_path)


def test_deserialise_data_root(tmpdir):
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = DataState("test")
    data_store.discover_structures(data)

    metadata = catalog.get_metadata("Technology:Common:DeviceType")
    data_store.create_new_data(pool, state, catalog, "Tidal", metadata)

    data_index = state.get_index("Technology:Common:DeviceType")
    new_data = pool.get(data_index)

    data_store.serialise_data(
        pool, [data_index], str(tmpdir), root_dir=str(tmpdir)
    )

    data_store.deserialise_data(
        catalog, pool, [data_index], root_dir=str(tmpdir)
    )
    new_data = pool.get(data_index)

    assert isinstance(new_data, Data)
    assert new_data._data == "Tidal"


def test_serialise_pool(tmpdir):
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = DataState("test")
    data_store.discover_structures(data)

    metadata = catalog.get_metadata("Technology:Common:DeviceType")
    data_store.create_new_data(pool, state, catalog, "Tidal", metadata)

    data_index = state.get_index("Technology:Common:DeviceType")

    data_store.serialise_pool(pool, str(tmpdir))

    data_box = pool.get(data_index)

    assert isinstance(data_box, SerialBox)

    data_path = data_box.load_dict["file_path"]

    assert os.path.isfile(data_path)


def test_deserialise_pool(tmpdir):
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = DataState("test")
    data_store.discover_structures(data)

    metadata = catalog.get_metadata("Technology:Common:DeviceType")
    data_store.create_new_data(pool, state, catalog, "Tidal", metadata)

    data_index = state.get_index("Technology:Common:DeviceType")
    new_data = pool.get(data_index)

    data_store.serialise_pool(pool, str(tmpdir))

    data_store.deserialise_pool(catalog, pool)
    new_data = pool.get(data_index)

    assert isinstance(new_data, Data)
    assert new_data._data == "Tidal"


def test_deserialise_pool_warn_missing(tmpdir):
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = DataState("test")
    data_store.discover_structures(data)

    metadata = catalog.get_metadata("Technology:Common:DeviceType")
    data_store.create_new_data(pool, state, catalog, "Tidal", metadata)
    data_store.serialise_pool(pool, str(tmpdir))

    # Redefine the data stor
    catalog = DataCatalog()
    validation = DataValidation()
    validation.update_data_catalog_from_definitions(catalog, user_data)
    data_store = DataStorage(data)

    with pytest.raises(ValueError):
        data_store.deserialise_pool(catalog, pool)

    data_store.deserialise_pool(catalog, pool, warn_missing=True)

    assert True


def test_deserialise_pool_warn_unpickle(tmpdir, mocker):
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = DataState("test")
    data_store.discover_structures(data)

    metadata = catalog.get_metadata("Technology:Common:DeviceType")
    data_store.create_new_data(pool, state, catalog, "Tidal", metadata)

    data_store.serialise_pool(pool, str(tmpdir))

    another_mock = mocker.Mock()
    another_mock.load_data = mocker.Mock(side_effect=TypeError("Boom!"))
    get_structure = mocker.patch.object(data_store, "get_structure")
    get_structure.return_value = another_mock

    with pytest.raises(Exception):
        data_store.deserialise_pool(catalog, pool)

    data_store.deserialise_pool(catalog, pool, warn_unpickle=True)

    assert True


def test_serialise_pool_root(tmpdir):
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = DataState("test")
    data_store.discover_structures(data)

    metadata = catalog.get_metadata("Technology:Common:DeviceType")
    data_store.create_new_data(pool, state, catalog, "Tidal", metadata)

    data_index = state.get_index("Technology:Common:DeviceType")

    data_store.serialise_pool(pool, str(tmpdir), root_dir=str(tmpdir))

    data_box = pool.get(data_index)

    assert isinstance(data_box, SerialBox)

    data_path = os.path.join(str(tmpdir), data_box.load_dict["file_path"])

    assert os.path.isfile(data_path)


def test_deserialise_pool_root(tmpdir):
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = DataState("test")
    data_store.discover_structures(data)

    metadata = catalog.get_metadata("Technology:Common:DeviceType")
    data_store.create_new_data(pool, state, catalog, "Tidal", metadata)

    data_index = state.get_index("Technology:Common:DeviceType")
    new_data = pool.get(data_index)

    data_store.serialise_pool(pool, str(tmpdir), root_dir=str(tmpdir))

    data_store.deserialise_pool(catalog, pool, root_dir=str(tmpdir))
    new_data = pool.get(data_index)

    assert isinstance(new_data, Data)
    assert new_data._data == "Tidal"


def test_save_pool(tmpdir):
    "Try pickling a DataPool"

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = DataState("test")
    data_store.discover_structures(data)

    metadata = catalog.get_metadata("Technology:Common:DeviceType")
    data_store.create_new_data(pool, state, catalog, "Tidal", metadata)

    data_index = state.get_index("Technology:Common:DeviceType")

    data_store.serialise_pool(pool, str(tmpdir))

    data_box = pool.get(data_index)

    assert isinstance(data_box, SerialBox)

    test_path = os.path.join(str(tmpdir), "pool.pkl")
    pickle.dump(pool, open(test_path, "wb"), -1)

    assert os.path.isfile(test_path)


def test_load_pool(tmpdir):
    "Try unpickling a DataPool"

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = DataState("test")
    data_store.discover_structures(data)

    metadata = catalog.get_metadata("Technology:Common:DeviceType")
    data_store.create_new_data(pool, state, catalog, "Tidal", metadata)

    data_index = state.get_index("Technology:Common:DeviceType")
    new_data = pool.get(data_index)

    data_store.serialise_pool(pool, str(tmpdir))

    test_path = os.path.join(str(tmpdir), "pool.pkl")
    pickle.dump(pool, open(test_path, "wb"), -1)

    assert os.path.isfile(test_path)

    loaded_pool = pickle.load(open(test_path, "rb"))

    data_store.deserialise_pool(catalog, loaded_pool)
    new_data = loaded_pool.get(data_index)

    assert isinstance(new_data, Data)
    assert new_data._data == "Tidal"


def test_load_pool_root(tmpdir):
    "Try unpickling a DataPool using a root directory"

    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()
    state = DataState("test")
    data_store.discover_structures(data)

    metadata = catalog.get_metadata("Technology:Common:DeviceType")
    data_store.create_new_data(pool, state, catalog, "Tidal", metadata)

    data_index = state.get_index("Technology:Common:DeviceType")
    new_data = pool.get(data_index)

    data_store.serialise_pool(pool, str(tmpdir), root_dir=str(tmpdir))

    test_path = os.path.join(str(tmpdir), "pool.pkl")
    pickle.dump(pool, open(test_path, "wb"), -1)

    assert os.path.isfile(test_path)

    new_root = os.path.join(str(tmpdir), "test")
    #    os.makedirs(new_root)
    move_path = os.path.join(str(tmpdir), "test", "pool.pkl")
    shutil.copytree(str(tmpdir), new_root)

    loaded_pool = pickle.load(open(move_path, "rb"))

    data_store.deserialise_pool(catalog, loaded_pool, root_dir=new_root)
    new_data = loaded_pool.get(data_index)

    assert isinstance(new_data, Data)
    assert new_data._data == "Tidal"


def test_create_pool_subset():
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)
    pool = DataPool()

    # Get the meta data from the catalog
    metadata = catalog.get_metadata("my:test:variable")

    # Create and store the first state
    state1 = data_store.create_new_datastate("state1")
    data_store.create_new_data(pool, state1, catalog, ["apples"], metadata)

    # Create and store the second state
    state2 = data_store.create_new_datastate("state2")
    data_store.create_new_data(
        pool, state2, catalog, ["apples", "pears"], metadata
    )

    assert len(pool) == 2

    # Create a subset based on the second state
    new_pool, new_state = data_store.create_pool_subset(pool, state2)

    assert id(new_pool) != id(pool)
    assert len(new_pool) == 1

    orig_data_index = state2.get_index("my:test:variable")
    orig_data_obj = pool.get(orig_data_index)

    new_data_index = new_state.get_index("my:test:variable")
    new_data_obj = new_pool.get(new_data_index)

    assert id(orig_data_obj._data) != id(new_data_obj._data)

    orig_data_value = data_store.get_data_value(
        pool, state2, "my:test:variable"
    )

    new_data_value = data_store.get_data_value(
        new_pool, new_state, "my:test:variable"
    )

    assert len(orig_data_value) == 2
    assert orig_data_value == new_data_value

    assert id(state2) != id(new_state)
    assert set(state2.get_identifiers()) == set(new_state.get_identifiers())


def test_copy_datastate_meta():
    data_store = DataStorage(data)

    # Create and store the first state
    state = data_store.create_new_datastate("state1")
    state.mask()

    test = data_store._copy_datastate_meta(state)

    assert isinstance(test, DataState)
    assert test is not state
    assert test.get_level() == "state1"
    assert test.ismasked()


def test_copy_datastate_meta_new_level():
    data_store = DataStorage(data)

    # Create and store the first state
    state = data_store.create_new_datastate("state1")

    test = data_store._copy_datastate_meta(state, level="state2")

    assert isinstance(test, DataState)
    assert test is not state
    assert test.get_level() == "state2"
    assert not test.ismasked()


def test_get_data_obj_and_get_value():
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)

    # Get the meta data from the catalog
    metadata = catalog.get_metadata("Technology:Common:DeviceType")

    data_obj = data_store._get_data_obj(metadata, "Tidal")
    value = data_store._get_value(data_obj)

    assert isinstance(data_obj, Data)
    assert value == "Tidal"


def test_check_valid_datastate():
    data_store = DataStorage(data)

    # Create and store the first state
    state = data_store.create_new_datastate("state1")

    _check_valid_datastate(state)

    assert True


def test_check_valid_datastate_error():
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=data.MyMetaData)
    validation.update_data_catalog_from_definitions(catalog, data)
    data_store = DataStorage(data)

    # Get the meta data from the catalog
    metadata = catalog.get_metadata("Technology:Common:DeviceType")

    data_obj = data_store._get_data_obj(metadata, "Tidal")

    with pytest.raises(ValueError):
        _check_valid_datastate(data_obj)
