# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 15:24:33 2016

@author: Mathew Topper
"""

# pylint: disable=C0103,C0111

import glob

from polite_config.paths import DirectoryMap


def test_DirectoryMap_copy_all(tmp_path):
    # Make a source directory with some files
    src_tmp_path = tmp_path / "test_src"
    src_tmp_path.mkdir()

    config1 = src_tmp_path / "config.txt"
    config1.write_text("content")

    config2 = src_tmp_path / "config.yaml"
    config2.write_text("content")

    # Make a target directory
    dst_tmp_path = tmp_path / "test_dst"

    test_dirmap = DirectoryMap(dst_tmp_path, src_tmp_path)

    # Test the method in vanilla mode
    test_dirmap.copy_all()

    assert len(list(dst_tmp_path.iterdir())) == 2


def test_DirectoryMap_copy_all_new(tmp_path):
    # Make a source directory with some files
    src_tmp_path = tmp_path / "test_src"
    src_tmp_path.mkdir()

    config1 = src_tmp_path / "config.txt"
    config1.write_text("content")

    config2 = src_tmp_path / "config.yaml"
    config2.write_text("content")

    # Make a target directory
    dst_tmp_path = tmp_path / "test_dst"

    test_dirmap = DirectoryMap(dst_tmp_path, src_tmp_path)

    # Test the method is creating .new files
    test_dirmap.copy_all()
    test_dirmap.copy_all()

    assert len(list(dst_tmp_path.iterdir())) == 4
    assert len(glob.glob("*.new", root_dir=str(dst_tmp_path))) == 2


def test_DirectoryMap_copy_all_overwrite(tmp_path):
    # Make a source directory with some files
    src_tmp_path = tmp_path / "test_src"
    src_tmp_path.mkdir()

    config1 = src_tmp_path / "config.txt"
    config1.write_text("content")

    config2 = src_tmp_path / "config.yaml"
    config2.write_text("content")

    # Make a target directory
    dst_tmp_path = tmp_path / "test_dst"
    dst_tmp_path.mkdir()

    # Make a dst file to be overwritten
    config3 = dst_tmp_path / "config.yaml"
    config3.write_text("deleteme")

    test_dirmap = DirectoryMap(dst_tmp_path, src_tmp_path)

    # Test the method can overwrite existing files
    test_dirmap.copy_all(overwrite=True)

    assert len(list(dst_tmp_path.iterdir())) == 2
    assert config3.read_text() == "content"


def test_DirectoryMap_safe_copy_all(tmp_path):
    # Make a source directory with some files
    src_tmp_path = tmp_path / "test_src"
    src_tmp_path.mkdir()

    config1 = src_tmp_path / "config.txt"
    config1.write_text("content")

    config2 = src_tmp_path / "config.yaml"
    config2.write_text("content")

    # Make a target directory
    dst_tmp_path = tmp_path / "test_dst"
    dst_tmp_path.mkdir()

    # Make a dst file not to be overwritten
    config3 = dst_tmp_path / "config.yaml"
    config3.write_text("deleteme")

    test_dirmap = DirectoryMap(dst_tmp_path, src_tmp_path)

    # Test the method will ovoid overwrite existing files
    test_dirmap.safe_copy_all()

    assert len(list(dst_tmp_path.iterdir())) == 2
    assert config3.read_text() == "deleteme"
