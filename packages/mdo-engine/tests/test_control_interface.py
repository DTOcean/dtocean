# -*- coding: utf-8 -*-
"""py.test tests on control.interface module

.. moduleauthor:: Mathew Topper <mathew.topper@tecnalia.com>
"""

import os

import pytest

import mdo_engine.test.interfaces as interfaces
from mdo_engine.control.sockets import NamedSocket
from mdo_engine.test.interfaces.sptfile import SPTInterface

from . import interface_plugins as interface_plugins


def test_get_modules_from_package():
    """Test if we can retreive the SPTInterface plugin"""

    test = NamedSocket("FileInterface")
    test.discover_interfaces(interfaces)

    assert "SPTInterface" in test._interface_classes.keys()


def test_get_all_variables():
    """Test retrieving variables from interfaces"""

    test = NamedSocket("FileInterface")
    test.discover_interfaces(interfaces)
    all_vars = test.get_all_variables()

    assert "site:wave:dir" in all_vars
    assert "masked.variable" in all_vars


def test_get_providing_interfaces():
    test_var = "site:wave:dir"

    interface = NamedSocket("FileInterface")
    interface.discover_interfaces(interfaces)
    providers = interface.get_providing_interfaces(test_var)

    assert "SPTInterface" in providers


def test_get_interface_object():
    """Test whether an interface instance can be provided"""

    test_interface = "SPTInterface"

    interface = NamedSocket("FileInterface")
    interface.discover_interfaces(interfaces)
    file_interface = interface.get_interface_object(test_interface)

    assert isinstance(file_interface, SPTInterface)


def test_get_interface_names():
    """Test retrieving name attribute of the interfaces"""

    test = NamedSocket("FileInterface")
    test.discover_interfaces(interfaces)
    names = test.get_interface_names()

    assert "Datawell SPT File" in names.keys()


def test_get_data():
    """Test if data can be retrieved from an interface"""

    test_interface = "SPTInterface"
    test_variable = "site:wave:dir"

    this_dir = os.path.dirname(__file__)
    test_path = os.path.join(this_dir, "data", "test_spectrum_30min.spt")

    interfacer = NamedSocket("FileInterface")
    interfacer.discover_interfaces(interfaces)
    file_interface = interfacer.get_interface_object(test_interface)

    # Forget to set a path
    with pytest.raises(ValueError):
        file_interface.get_data(test_variable)

    # Set a path and get the data
    file_interface.set_file_path(test_path)
    file_interface.connect()
    data = file_interface.get_data(test_variable)

    assert len(data) == 64


def test_raw_interface():
    test_interface = "WaveRaw"
    test_variable = "site:wave:Hm0"
    test_value = [4.0] * 10

    interfacer = NamedSocket("RawInterface")

    try:
        interfacer.discover_interfaces(interface_plugins)
    except ModuleNotFoundError as e:
        if "dtocean_dummy" in str(e):
            pytest.skip("dtocean-dummy-module not installed")

    providers = interfacer.get_providing_interfaces(test_variable)
    raw_interface = interfacer.get_interface_object(test_interface)

    # Forget to connect
    assert raw_interface.get_data(test_variable) is None

    # Set a path and get the data
    raw_interface.set_variables({test_variable: test_value})
    raw_interface.connect()
    data = raw_interface.get_data(test_variable)

    assert test_interface in providers
    assert len(data) == 10
    assert data[0] == 4.0


def test_wrong_interface():
    test_interface = "OtherRaw"
    test_variable = "site:wave:Hm0"
    test_value = [4.0] * 10

    interfacer = NamedSocket("RawInterface")
    try:
        interfacer.discover_interfaces(interface_plugins)
    except ModuleNotFoundError as e:
        if "dtocean_dummy" in str(e):
            pytest.skip("dtocean-dummy-module not installed")

    raw_interface = interfacer.get_interface_object(test_interface)

    # Try to get the wrong data
    with pytest.raises(KeyError):
        raw_interface.set_variables({test_variable: test_value})
