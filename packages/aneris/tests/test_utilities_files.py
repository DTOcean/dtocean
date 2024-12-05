# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 17:28:04 2015

@author: Mathew Topper
"""

import os

from aneris.utilities.files import mkdir_p, xl_to_dds, xl_to_data_yaml

dir_path = os.path.dirname(__file__)


def test_mkdir_p(tmpdir):
    
    test_dir_name = "test"
    test_path = os.path.join(str(tmpdir), test_dir_name)
    mkdir_p(test_path)
    
    assert os.path.isdir(test_path)


def test_xl_to_dds():
    
    test_xl_path = os.path.join(dir_path, "data", "test_dds.xlsx")
    
    dds = xl_to_dds(test_xl_path,
                    ignore_column="Comments")
    
    assert len(dds) > 0
    assert dds[0]['identifier'] == 'constants.gravity'


def test_xl_to_data_yaml(tmpdir):
    
    test_yaml_name = "test_dds.yaml"
    test_yaml_path = os.path.join(str(tmpdir), test_yaml_name)
    
    test_xl_path = os.path.join(dir_path, "data", "test_dds.xlsx")
    
    xl_to_data_yaml(test_xl_path,
                    test_yaml_path)
    
    assert os.path.isfile(test_yaml_path)
