# -*- coding: utf-8 -*-
"""py.test tests on control.interface module

.. moduleauthor:: Mathew Topper <mathew.topper@tecnalia.com>
"""

from mdo_engine.boundary.interface import (
    AutoInterface,
    FileInterface,
    RawInterface,
)
from mdo_engine.control.data import DataStorage, DataValidation
from mdo_engine.control.factory import InterfaceFactory
from mdo_engine.control.sockets import NamedSocket
from mdo_engine.entity.data import DataCatalog, MetaData

from . import auto_plugins as auto_plugins
from .auto_plugins.definitions import AutoSimple


class AutoMeta(MetaData):
    def __init__(self, props_dict):
        self._auto = None
        super(AutoMeta, self).__init__(props_dict)

        return

    @property
    def auto(self):
        return self._auto


class AutoTest(AutoInterface, FileInterface):
    def __init__(self):
        super(AutoTest, self).__init__()
        self._two = 2.0

        return

    @classmethod
    def get_connect_name(cls):
        return "auto_connect"

    @classmethod
    def get_method_names(cls):
        return ["get_valid_extensions"]


class AutoRaw(AutoInterface, RawInterface):
    def __init__(self):
        AutoInterface.__init__(self)
        RawInterface.__init__(self)

        return

    @classmethod
    def get_connect_name(cls):
        return None


# def test_make_auto_interface():
#
#    TestCls = make_auto_interface(AutoInterface,
#                                  "Not:Real:Variable",
#                                  auto_connect,
#                                  2)
#
#    assert issubclass(TestCls, AutoInterface)
#    assert TestCls.get_name() == "Not:Real:Variable Auto Interface"
#    assert TestCls.declare_inputs() ==  None
#    assert TestCls.declare_outputs() == ["Not:Real:Variable"]
#    assert TestCls.declare_id_map() == {"result": "Not:Real:Variable"}
#
#    with pytest.raises(NotImplementedError):
#
#        test = TestCls()
#        test.connect()


def test_make_auto_test():
    make_auto_interface = InterfaceFactory(AutoTest)

    meta = AutoMeta(
        {"identifier": "Not:Real:Variable", "structure": None, "auto": 2}
    )

    test_simple = AutoSimple()

    TestCls = make_auto_interface(meta, test_simple)

    assert issubclass(TestCls, AutoInterface)
    assert TestCls.get_name() == "Not:Real:Variable AutoTest Interface"
    assert TestCls.declare_inputs() == ["Not:Real:Variable"]
    assert TestCls.declare_optional() == ["Not:Real:Variable"]
    assert TestCls.declare_outputs() == ["Not:Real:Variable"]
    assert TestCls.declare_id_map() == {"result": "Not:Real:Variable"}
    assert TestCls.get_valid_extensions() == [".spt"]

    test = TestCls()
    test.put_meta("Not:Real:Variable", meta)
    test.connect()

    assert test.data.result == 4


def test_make_auto_raw():
    make_auto_interface = InterfaceFactory(AutoRaw)

    meta = AutoMeta(
        {"identifier": "Not:Real:Variable", "structure": None, "auto": 2}
    )

    test_simple = AutoSimple()

    TestCls = make_auto_interface(meta, test_simple)

    assert issubclass(TestCls, AutoInterface)
    assert TestCls.get_name() == "Not:Real:Variable AutoRaw Interface"
    assert TestCls.declare_inputs() is None
    assert TestCls.declare_optional() is None
    assert TestCls.declare_outputs() == ["Not:Real:Variable"]
    assert TestCls.declare_id_map() == {"result": "Not:Real:Variable"}

    test = TestCls()

    assert test


def test_build_auto():
    catalog = DataCatalog()
    validation = DataValidation(meta_cls=auto_plugins.AutoMetaData)

    validation.update_data_catalog_from_definitions(catalog, auto_plugins)
    all_vars = catalog.get_variable_identifiers()

    assert "my:auto:variable" in all_vars
    assert (
        catalog._metadata_variable_map["my:auto:variable"].structure
        == "AutoSimple"
    )

    data_store = DataStorage(auto_plugins)

    metadata = catalog._metadata_variable_map["my:auto:variable"]
    data_form = metadata.structure
    data_obj = data_store._structures[data_form]

    assert isinstance(data_obj, AutoSimple)

    print(metadata.auto)

    make_auto_interface = InterfaceFactory(AutoTest)

    TestCls = make_auto_interface(metadata, data_obj)

    assert issubclass(TestCls, AutoInterface)
    assert TestCls.get_name() == "{} AutoTest Interface".format(
        metadata.identifier
    )
    assert TestCls.declare_inputs() == [metadata.identifier]
    assert TestCls.declare_optional() == [metadata.identifier]
    assert TestCls.declare_outputs() == [metadata.identifier]
    assert TestCls.declare_id_map() == {"result": metadata.identifier}

    test = TestCls()
    test.put_meta("my:auto:variable", metadata)
    test.connect()

    assert test.data.result == 4

    interfacer = NamedSocket("AutoInterface")
    interfacer.add_interface(TestCls)
    all_vars = interfacer.get_all_variables()

    assert "my:auto:variable" in all_vars

    providing = interfacer.get_providing_interfaces("my:auto:variable")

    assert providing[0] == TestCls.__name__
