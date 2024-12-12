#!/usr/bin/env python

"""Utility module with functions to provide paths to application files.

.. module:: paths
   :platform: Windows
   :synopsis: Provides application paths

.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>

"""

import inspect
import os
import shutil
import sys
from pathlib import Path
from typing import Optional

from .appdirs import site_data_dir, system, user_data_dir


class ModPath(Path):
    """Path relative to a given module name's parent directory"""

    def __new__(cls, module_name, *paths):
        mod_handle = sys.modules[module_name]
        dir_path = module_dir(mod_handle)
        return Path(dir_path, *paths)


class EtcPath(Path):
    """Path relative to the Python distribution's etc directory"""

    def __new__(cls, *paths):
        def get_dir(*paths):  # pylint: disable=missing-docstring
            return os.path.abspath(os.path.join(*paths))

        exe_folder = os.path.dirname(sys.executable)

        if system == "win32":
            dir_path = get_dir(exe_folder, "etc")
        else:
            dir_path = get_dir(exe_folder, "..", "etc")

        return Path(dir_path, *paths)


class UserDataPath(Path):
    """Path relative to the user data directory for the given package."""

    def __new__(cls, package, company, *paths):
        dir_path = user_data_dir(package, company, roaming=True)
        dir_path = os.path.join(dir_path, *paths)
        return Path(dir_path)


class SiteDataPath(Path):
    """Path relative to the site data directory for the given package."""

    def __new__(cls, package, company, *paths):
        dir_path = site_data_dir(package, company)
        return Path(dir_path, *paths)


class DirectoryMap:
    """Class for moving files from one directory to another.

    Attributes:
        target_dir (pathlib.Path)
        source_dir (pathlib.Path)
        last_copy_path (str): Location of last copied configuration file.
          Defaults to None.

    """

    def __init__(self, target_dir, source_dir):
        self.target_dir: Path = target_dir
        self.source_dir: Path = source_dir
        self.last_copy_path: Optional[str] = None

        return

    def target_exists(self, file_name=None):
        """Test to see if a given target file or directory exists

        Args:
            file_name (str, optional): The name of a target file to
              check.

        Returns:
            bool: True if path exists.

        """

        if file_name is not None:
            result = (self.target_dir / file_name).is_file()

        else:
            result = self.target_dir.is_dir()

        return result

    def copy_file(
        self,
        src_name,
        dst_name=None,
        overwrite=False,
        new_ext=".new",
    ):
        """Copy a file from the source to target directory.

        Args:
            src_name (str): File name of the file to copy. It is
              assumed that this exists within the source directory.
            dst_name (str, optional): Destination file name. Defaults to the
              same as src_name.
            overwrite (bool, optional): Copy the files to target
              directory even if it already exists. Default to False.
            new_ext (str, optional): If target file exists and overwrite
              is False copy the file appending this extension. Defaults to
              ".new".

        """

        if self.source_dir is None:
            error_str = "No source directory is given."
            raise ValueError(error_str)

        if dst_name is None:
            file_name = src_name
        else:
            file_name = dst_name

        # Build the destination path
        dst_file_path = self.target_dir / file_name

        if self.target_exists(file_name) and not overwrite:
            dst_file_path = dst_file_path.with_suffix(
                dst_file_path.suffix + new_ext
            )

        # Get the source path
        src_file_path = self.source_dir / src_name

        # Prepare the destination directory
        self.target_dir.mkdir(exist_ok=True)

        # Copy the file
        shutil.copy(src_file_path, dst_file_path)

        # Punch out the dst_file_path to logging
        #        sys.stdout.write(dst_file_path)

        # Store the location of the copy directory
        self.last_copy_path = dst_file_path

        return

    def safe_copy_file(
        self,
        src_name,
        dst_name=None,
        **kwargs,
    ):
        """Copy the file to the target directory if it does not
        exist already.

        Args:
            src_name (str): File name of the file to copy. It is
              assumed that this exists within the source directory.
            dst_name (str, optional): Destination file name. Defaults to the
              same as src_name.
        """

        if dst_name is None:
            file_name = src_name
        else:
            file_name = dst_name

        # Test for existance otherwise copy the file to the user data
        # directory
        if not self.target_exists(file_name):
            self.copy_file(src_name, dst_name)

        return

    def copy_all(
        self,
        overwrite=False,
        new_ext=".new",
    ):
        """Copy all files from the source to target directory.

        Args:
            overwrite (bool, optional): Copy the files to target
              directory even if it already exists. Default to False.
            new_ext (str, optional): If target file exists and overwrite
              is False copy the file appending this extension. Defaults to
              ".new".

        """

        self._copy_all(self.copy_file, overwrite=overwrite, new_ext=new_ext)

        return

    def safe_copy_all(self):
        """Copy all files from the source to target directory if they do not
        exist.
        """

        self._copy_all(self.safe_copy_file)

        return

    def _copy_all(
        self,
        copy_method,
        overwrite=False,
        new_ext=".new",
    ):
        """Copy all files from the source to target directory.

        Args:
            copy_method: File copying method to call
            overwrite (bool, optional): Copy the files to target
              directory even if it already exists. Default to False.
            new_ext (str, optional): If target file exists and overwrite
              is False copy the file appending this extension. Defaults to
              ".new".

        """

        for src_path in self.source_dir.iterdir():
            kwargs = {"overwrite": overwrite, "new_ext": new_ext}
            copy_method(src_path.name, **kwargs)

        return


def object_path(obj):
    """Return the path of the class object.

    Args:
      object (obj): Class object.

    Returns:
        pathlib.Path: Absolute path to class source file.
    """

    return Path(inspect.getabsfile(obj.__class__))


def object_dir(obj):
    """Return the directory path containing the class object.

    Args:
      object (obj): Class object.

    Returns:
        pathlib.Path:: Absolute path to directory containing class source file.
    """

    obj_path = object_path(obj)
    return obj_path.parent


def class_path(cls):
    """Return the path of the class attribute.

    Args:
      class (cls): Class.

    Returns:
        pathlib.Path:: Absolute path to class source file.
    """

    return Path(inspect.getabsfile(cls))


def class_dir(cls):
    """Return the directory path containing the class attribute.

    Args:
      class (cls): Class.

    Returns:
        pathlib.Path:: Absolute path to directory containing class source file.
    """

    cls_path = class_path(cls)
    return cls_path.parent


def module_path(module):
    """Return the path of the modules "__file__" attribute.

    Args:
      module (module): Module object.

    Returns:
        pathlib.Path:: Absolute path to "module.__file__".

    """

    return Path(module.__file__).resolve()


def module_dir(module):
    """Returns path to the directory containing the given module.

    Args:
      module (module): Module object.

    Returns:
        pathlib.Path:: Absolute path to directory containing module.

    """

    mod_path = module_path(module)
    return mod_path.parent
