# -*- coding: utf-8 -*-
"""
Created on Wed May 31 17:45:28 2017

@author: mtopper
"""

import pytest

from aneris.boundary.interface import FileInterface
from aneris.control.sockets import NamedSocket

import aneris.test.interfaces as interfaces


def test_FileInterface():
    
    test_interface = 'SPTInterface'
    
    interface = NamedSocket("FileInterface")
    interface.discover_interfaces(interfaces)
    file_interface = interface.get_interface_object(test_interface)
    
    assert isinstance(file_interface, FileInterface)
    

def test_FileInterface_check_path(tmpdir):
    
    test_interface = 'SPTInterface'
    test_path = tmpdir.mkdir("sub").join("test.spt")
    test_path.ensure(file=True)
    test_path_str = str(test_path)
    
    interface = NamedSocket("FileInterface")
    interface.discover_interfaces(interfaces)
    file_interface = interface.get_interface_object(test_interface)
    
    file_interface.set_file_path(test_path_str)
    file_interface.check_path()
    
    assert True
    

def test_FileInterface_check_path_fail_ext(tmpdir):
    
    test_interface = 'SPTInterface'
    test_path = tmpdir.mkdir("sub").join("test.csv")
    test_path.ensure(file=True)
    test_path_str = str(test_path)
    
    interface = NamedSocket("FileInterface")
    interface.discover_interfaces(interfaces)
    file_interface = interface.get_interface_object(test_interface)
    
    file_interface.set_file_path(test_path_str)
    
    with pytest.raises(IOError) as excinfo:
        file_interface.check_path()

    assert 'File extension' in str(excinfo.value)
        
        
def test_FileInterface_check_path_fail_missing(tmpdir):
    
    test_interface = 'SPTInterface'
    test_path = tmpdir.mkdir("sub").join("test.spt")
    test_path_str = str(test_path)
    
    interface = NamedSocket("FileInterface")
    interface.discover_interfaces(interfaces)
    file_interface = interface.get_interface_object(test_interface)
    
    file_interface.set_file_path(test_path_str)
    
    with pytest.raises(IOError) as excinfo:
        file_interface.check_path(check_exists=True)

    assert 'No file or directory exists for path' in str(excinfo.value)
    
    
    