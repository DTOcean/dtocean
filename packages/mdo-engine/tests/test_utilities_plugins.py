# -*- coding: utf-8 -*-
"""py.test tests on utilities.plugins module

.. moduleauthor:: Mathew Topper <mathew.topper@tecnalia.com>
"""

import os
import pathlib
import sys

import pytest
from polite_config.paths import module_path

from mdo_engine.utilities.plugins import (
    get_class_attr,
    get_class_descriptions_from_module,
    get_module_names_from_package,
    get_module_names_from_paths,
    get_subclass_names_from_module,
)


def test_get_module_names_from_package():
    """Test the modules in the package are as expected"""

    # this is the package we are inspecting -- 'logging' from stdlib
    import logging

    names = get_module_names_from_package(logging)

    assert names == ["logging.config", "logging.handlers"]


def test_get_module_names_from_paths():
    """Test if we can retrieve the root package name from the source code"""

    # Get this module path and then the directory above it.
    this_mod = sys.modules[__name__]
    mod_path = module_path(this_mod)
    root_dir = pathlib.Path(mod_path).parents[1]
    names = get_module_names_from_paths([root_dir])

    # Get the expected names by looking for py files in the root_dir
    expected = []

    for check_file in os.listdir(root_dir):
        if check_file.endswith(".py"):
            name, _ = os.path.splitext(check_file)
            expected.append(name)

    assert set(names) >= set(expected)


def test_get_class_descriptions_from_module():
    """Test if the SeriesData class can be recovered"""
    mods = get_class_descriptions_from_module(
        "mdo_engine.test.data.definitions"
    )
    assert "SeriesData" in mods


def test_get_subclass_names_from_module():
    """Test if the the SeriesData class is a subclass of the Data class."""
    data_sub_mods = get_subclass_names_from_module(
        "mdo_engine.test.data.definitions", "AnotherStructure"
    )
    assert "AnotherStructure" not in data_sub_mods
    assert "AnotherStructureSubClass" in data_sub_mods


def test_get_class_attr_warn(monkeypatch):
    def mockerror(path):
        raise ImportError

    monkeypatch.setattr("importlib.import_module", mockerror)

    result = get_class_attr("test", "notamodule", True)

    assert result is None


def test_get_class_attr_exception(monkeypatch):
    def mockerror(path):
        raise ImportError

    monkeypatch.setattr("importlib.import_module", mockerror)

    with pytest.raises(Exception):
        get_class_attr("test", "notamodule")
