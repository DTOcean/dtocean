# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 15:24:33 2016

@author: Mathew Topper
"""

#pylint: disable=C0103,C0111

import os
import pytest

from polite.paths import (Directory, 
                          UserDataDirectory,
                          SiteDataDirectory,
                          EtcDirectory,
                          object_path,
                          object_dir,
                          class_path,
                          class_dir)

#pylint: disable=C0111,R0903,R0201
class Mock(object):
    def mock(self):
        return True


def test_makedir(tmpdir):
    
    # Make a local directory
    locd = tmpdir.mkdir("test")
    locp = locd.join("test")
    
    test = Directory(str(locp))
    test.makedir()
    
    assert os.path.isdir(str(locp))


def test_UserDataDirectory():
    
    test = UserDataDirectory("test", "test")
    path = test.get_path()
    
    assert isinstance(path, str)


def test_SiteDataDirectory():
    test = SiteDataDirectory("test", "test")
    path = test.get_path()
    
    assert isinstance(path, str)


def test_EtcDirectory_win(mocker, tmp_path):
    
    exe_path = tmp_path / "python.exe"
    
    mocker.patch('polite.paths.sys.executable',
                 new=str(exe_path))
    mocker.patch('polite.paths.system',
                 new='win32')
    
    test = EtcDirectory("mock")
    expected = os.path.join(str(tmp_path), "etc", "mock")
    
    assert test.get_path() == expected


def test_EtcDirectory_linux(mocker, tmp_path):
    
    exe_path = tmp_path / "bin" / "python"
    
    mocker.patch('polite.paths.sys.executable',
                 new=str(exe_path))
    mocker.patch('polite.paths.system',
                 new='linux2')
    
    test = EtcDirectory("mock")
    expected = os.path.join(str(tmp_path), "etc", "mock")
    
    assert test.get_path() == expected


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


def test_Directory_list_files(tmpdir):
    
    # Make a source directory with some files
    src_tmpdir = tmpdir.mkdir("test_src")
    
    config1 = src_tmpdir.join("config.txt")
    config1.write("content")
    
    config2 = src_tmpdir.join("config.yaml")
    config2.write("content")
    
    src_dir = Directory(str(src_tmpdir))
    
    dir_files = src_dir.list_files()
    
    assert set(dir_files) == set(["config.txt", "config.yaml"])


def test_Directory_list_files_missing(tmpdir):
    
    # Make a source directory path, which does not exist
    src_tmpdir = os.path.join(str(tmpdir), "missing")
    src_dir = Directory(str(src_tmpdir))
    
    with pytest.raises(IOError):
        src_dir.list_files()


def test_Directory_str():
    
    path = os.path.join("some", "path", "with", "..", "in")
    test = Directory(path)
    
    assert str(test) != path
    assert str(test) == os.path.join("some", "path", "in")
