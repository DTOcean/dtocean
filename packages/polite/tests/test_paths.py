# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 15:24:33 2016

@author: Mathew Topper
"""

# pylint: disable=C0103,C0111

import os

from polite.paths import (
    EtcDirectory,
    class_dir,
    class_path,
    object_dir,
    object_path,
)


# pylint: disable=C0111,R0903,R0201
class Mock(object):
    def mock(self):
        return True


def test_EtcDirectory_win(mocker, tmp_path):
    exe_path = tmp_path / "python.exe"

    mocker.patch("polite.paths.sys.executable", new=str(exe_path))
    mocker.patch("polite.paths.system", new="win32")

    test = EtcDirectory("mock")
    expected = os.path.join(str(tmp_path), "etc", "mock")

    assert str(test) == expected


def test_EtcDirectory_linux(mocker, tmp_path):
    exe_path = tmp_path / "bin" / "python"

    mocker.patch("polite.paths.sys.executable", new=str(exe_path))
    mocker.patch("polite.paths.system", new="linux2")

    test = EtcDirectory("mock")
    expected = os.path.join(str(tmp_path), "etc", "mock")

    assert str(test) == expected


def test_object_path():
    test = Mock()

    test_path = object_path(test)

    assert os.path.normcase(test_path) == os.path.normcase(__file__)


def test_object_dir():
    test = Mock()

    test_path = object_dir(test)
    this_dir = os.path.dirname(__file__)

    assert os.path.normcase(test_path) == os.path.normcase(this_dir)


def test_class_path():
    test_path = class_path(Mock)

    assert os.path.normcase(test_path) == os.path.normcase(__file__)


def test_class_dir():
    test_path = class_dir(Mock)
    this_dir = os.path.dirname(__file__)

    assert os.path.normcase(test_path) == os.path.normcase(this_dir)
