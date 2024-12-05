# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 15:24:33 2016

@author: Mathew Topper
"""

#pylint: disable=C0103,C0111

import glob

from polite.paths import Directory, DirectoryMap


def test_DirectoryMap_copy_all(tmpdir):

    # Make a source directory with some files
    src_tmpdir = tmpdir.mkdir("test_src")

    config1 = src_tmpdir.join("config.txt")
    config1.write("content")

    config2 = src_tmpdir.join("config.yaml")
    config2.write("content")

    src_dir = Directory(str(src_tmpdir))

    # Make a target directory
    dst_tmpdir = tmpdir.mkdir("test_dst")
    dst_dir = Directory(str(dst_tmpdir))

    test_dirmap = DirectoryMap(dst_dir, src_dir)

    # Test the method in vanilla mode
    test_dirmap.copy_all()

    assert len(dst_tmpdir.listdir()) == 2


def test_DirectoryMap_copy_all_new(tmpdir):

    # Make a source directory with some files
    src_tmpdir = tmpdir.mkdir("test_src")

    config1 = src_tmpdir.join("config.txt")
    config1.write("content")

    config2 = src_tmpdir.join("config.yaml")
    config2.write("content")

    src_dir = Directory(str(src_tmpdir))

    # Make a target directory
    dst_tmpdir = tmpdir.mkdir("test_dst")
    dst_dir = Directory(str(dst_tmpdir))

    test_dirmap = DirectoryMap(dst_dir, src_dir)

    # Test the method is creating .new files
    test_dirmap.copy_all()
    test_dirmap.copy_all()

    assert len(dst_tmpdir.listdir()) == 4
    assert len(glob.glob("*.new", root_dir=str(dst_tmpdir))) == 2


def test_DirectoryMap_copy_all_overwrite(tmpdir):

    # Make a source directory with some files
    src_tmpdir = tmpdir.mkdir("test_src")

    config1 = src_tmpdir.join("config.txt")
    config1.write("content")

    config2 = src_tmpdir.join("config.yaml")
    config2.write("content")

    src_dir = Directory(str(src_tmpdir))

    # Make a target directory
    dst_tmpdir = tmpdir.mkdir("test_dst")
    dst_dir = Directory(str(dst_tmpdir))

    # Make a dst file to be overwritten
    config3 = dst_tmpdir.join("config.yaml")
    config3.write("deleteme")

    test_dirmap = DirectoryMap(dst_dir, src_dir)

    # Test the method can overwrite existing files
    test_dirmap.copy_all(overwrite=True)

    assert len(dst_tmpdir.listdir()) == 2
    assert config3.read() == "content"


def test_DirectoryMap_safe_copy_all(tmpdir):

    # Make a source directory with some files
    src_tmpdir = tmpdir.mkdir("test_src")

    config1 = src_tmpdir.join("config.txt")
    config1.write("content")

    config2 = src_tmpdir.join("config.yaml")
    config2.write("content")

    src_dir = Directory(str(src_tmpdir))

    # Make a target directory
    dst_tmpdir = tmpdir.mkdir("test_dst")
    dst_dir = Directory(str(dst_tmpdir))

    # Make a dst file not to be overwritten
    config3 = dst_tmpdir.join("config.yaml")
    config3.write("deleteme")

    test_dirmap = DirectoryMap(dst_dir, src_dir)

    # Test the method will ovoid overwrite existing files
    test_dirmap.safe_copy_all()

    assert len(dst_tmpdir.listdir()) == 2
    assert config3.read() == "deleteme"
