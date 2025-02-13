# -*- coding: utf-8 -*-

"""This module provides function for configuring the application. This
includes settings for logging and helpers for user modified configuration
files.

.. module:: configuration
     :synopsis: Provides configuration helpers

.. moduleauthor:: Mathew Topper <damm_horse@yahoo.co.uk>

"""

import logging
from logging.config import dictConfig
from pathlib import Path
from typing import Any, Optional, TypeAlias, Union

import yaml
from configobj import ConfigObj
from configobj.validate import ValidateError, Validator

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader

from .paths import DirectoryMap

NestedDict: TypeAlias = dict[str, "str | NestedDict"]
StrOrPath = Union[str, Path]


class Config:
    """Base class for handling configuration files.

    Args:
        directory (polite.paths.Directory, polite.paths.DirectoryMap)
        file_name (str): File name of the config file.
    """

    def __init__(self, directory: Union[Path, DirectoryMap], file_name: str):
        if isinstance(directory, DirectoryMap):
            self.target_dir = directory.target_dir
            self.directory_map = directory
        else:
            self.target_dir = directory
            self.directory_map = None

        self.config_file_name = file_name

    def get_config_path(self):
        return self.target_dir / self.config_file_name

    def copy_config(self, overwrite=False, new_ext=".new"):
        """Copy a user editable config file to the target directory.

        Args:
            overwrite (bool, optional): Copy the config files to
              target directory even if it already exists. Default to False
            new_dir (str, optional): If user_config_path exists and overwrite
              is False copy the configuration with this extension. Defaults to
              ".new".

        """

        if self.directory_map is None:
            error_str = "No source directory available."
            raise ValueError(error_str)

        self.directory_map.copy_file(
            self.config_file_name, overwrite=overwrite, new_ext=new_ext
        )

    def config_exists(self):
        result = (self.target_dir / self.config_file_name).is_file()
        return result

    @classmethod
    def make_head_foot_bar(cls, header_title, bar_width, bar_char="*"):
        """Make header and footer strings consisting of a bar of characters of
        fixed width, with a title embeded in the header bar.

        Args:
            header_title (str): The title to be placed in the header bar.
            bar_width (int): The number of characters in the header and
              footer.
            bar_char (str, optional): Character to use for the bar. Default is
              "*".

        Returns:
            tuple: Tuple containing the strings (header, footer).
        """

        # Build the header and footer
        title_space = " {} ".format(header_title)
        header = "{0:{1}^{2}}".format(title_space, bar_char[0], bar_width)
        footer = bar_char * bar_width

        return (header, footer)


class ReadINI(Config):
    """Class to prepare and read ini configuration files. This class uses
    the configobj package.

    Args:
        directory (polite.paths.Directory, polite.paths.DirectoryMap)
        config_file_name (str): File name of the config file.
        validation_file_name (str, optional): Name of the file to be used to
          validate the inputs to the configuration file.

    Attributes:
        validation_file_name (str): File name of the configobj validation file.

    """

    def __init__(
        self,
        directory: Union[Path, DirectoryMap],
        config_file_name: str,
        validation_file_name=None,
    ):
        super(ReadINI, self).__init__(directory, config_file_name)
        self.validation_file_name = validation_file_name

    def get_validation_path(self):
        if self.validation_file_name is None:
            return self.target_dir
        return self.target_dir / self.validation_file_name

    def copy_config(self, overwrite=False, new_ext=".new"):
        """Copy a user editable config file to the target directory.

        Args:
            overwrite (bool, optional): Copy the config files to
              target directory even if it already exists. Default to False
            new_dir (str, optional): If user_config_path exists and overwrite
              is False copy the configuration with this extension. Defaults to
              ".new".

        """

        super(ReadINI, self).copy_config(overwrite, new_ext)

        if self.validation_file_name is None:
            return

        assert self.directory_map is not None
        self.directory_map.copy_file(
            self.validation_file_name, overwrite=overwrite, new_ext=new_ext
        )

    def config_exists(self):
        result = super(ReadINI, self).config_exists()

        if self.validation_file_name is not None:
            result = (
                result
                and (self.target_dir / self.validation_file_name).is_file()
            )

        return result

    def get_config(self, configspec_path=None):
        """Load the INI configuration file to a ConfigObj class,
        without validation, but allowing a configspec to be given.
        """

        # Get the path to the configspec file
        ini_config_path = self.get_config_path()

        # Test for existance of the file
        if not self.config_exists():
            error_str = "Expected file not found at path: {}".format(
                ini_config_path
            )
            raise IOError(error_str)

        if configspec_path is None:
            configspec = None
        else:
            configspec = str(configspec_path)

        config = ConfigObj(
            str(ini_config_path),
            configspec=configspec,
        )

        return config

    def get_valid_config(self, error_title="Config File Errors", bar_width=42):
        """Check whether the configuration file is valid, using the
        validation file specified in self.validation_file_name.

        This file is anticipated to be located with the "config" directory
        of the source code and the file name is appended to this directory
        path.

        Args:
            error_title (str, optional): The title to be placed in the header
              of the validation error messages. Default "Config File Errors".
            bar_width (int, optional): The number of characters in the header
              and footer. Default is 42.
        """

        # Get the path to the configspec file
        ini_valid_path = self.get_validation_path()
        config = self.get_config(ini_valid_path)

        validator = Validator()
        result = config.validate(validator, preserve_errors=True)

        if result != True:  # noqa: E712
            # Build the header and footer
            header, footer = self.make_head_foot_bar(error_title, bar_width)

            # Iterate through the failures in the config file
            log_msgs = ["", header]
            log_msgs.extend(self._type_fails(result))
            log_msgs.append(footer)

            log_msg = "\n".join(log_msgs)

            # module_logger.debug(log_msg)

            error_str = (
                'Configuration file "{}" failed ' "validation:\n{}"
            ).format(self.config_file_name, log_msg)
            raise ValidateError(error_str)

        return config

    def _type_fails(self, results):
        """Create strings with the specific validation errors.

        Args:
            results: The results of a ConfigObj.validate call.

        Results:
            list: A list of strings containing the validation errors.

        """

        log_lines = []

        # Iterate through the failures in the config file
        for key, value in results.items():
            if issubclass(type(value), ValidateError):
                log_str = (' - Key "{}" failed with error:\n' "   {}").format(
                    key, value
                )
                log_lines.append(log_str)

            elif value is False:
                log_str = ' - Key "{}" must be set.'.format(key)
                log_lines.append(log_str)

            elif isinstance(value, dict):
                add_logs = self._type_fails(value)
                log_lines.extend(add_logs)

        return log_lines


class ReadYAML(Config):
    """Class to read and write YAML configuration files. This class uses
    the pyyaml package.

    Args:
        directory (polite.paths.Directory, polite.paths.DirectoryMap)
        yaml_file_name (str): File name of the yaml file.
    """

    def __init__(
        self,
        directory: Union[Path, DirectoryMap],
        yaml_file_name: str,
    ):
        super(ReadYAML, self).__init__(directory, yaml_file_name)

    def read(self):
        """Load the YAML configuration file."""

        # Get the file path
        yaml_config_path = self.get_config_path()

        with open(yaml_config_path, "r") as conf:
            config_dict = yaml.load(conf, Loader=Loader)

        return config_dict

    def write(self, obj_to_serialise: Any, default_flow_style: bool = False):
        """Write the YAML configuration file."""

        # Write the file
        yaml_config_path = self.get_config_path()

        # Ensure target directory exists
        self.target_dir.mkdir(exist_ok=True)

        with open(yaml_config_path, "w") as yaml_file:
            yaml.dump(
                obj_to_serialise,
                yaml_file,
                default_flow_style=default_flow_style,
                Dumper=Dumper,
            )


class Logger(ReadYAML):
    """Class to configure and control the python logging system.

    Args:
        directory (polite.paths.Directory, polite.paths.DirectoryMap)
        config_file_name (str, optional): Name of the logging config file.
          Defaults to "logging.yaml".

    Attributes:
        logging_config_file_name (str): File name of the logging config file.

    """

    def __init__(self, directory, config_file_name="logging.yaml"):
        super(Logger, self).__init__(directory, config_file_name)

    def configure_logger(
        self,
        log_config_dict: Optional[NestedDict] = None,
        file_prefix: Optional[StrOrPath] = None,
    ):
        """Load the logging configuration file.

        Args:
            log_config_dict (dict, optional): A Python logging dictionary
              config. Calls self.read() by default.
            file_prefix (str | pathlib.Path, optional): Apply a prefix path to
              file handlers.
        """

        if log_config_dict is None:
            log_config_dict = self.read()
            assert isinstance(log_config_dict, dict)

        if file_prefix is None:
            dictConfig(log_config_dict)
            return

        handlers = log_config_dict["handlers"]
        assert isinstance(handlers, dict)

        file_prefix_path = Path(file_prefix)
        updated_handlers: NestedDict = {}

        for key, handler in handlers.items():
            assert isinstance(handler, dict)
            handler_class = handler["class"]

            assert isinstance(handler_class, str)
            handler_class_name = handler_class.split(".")[-1]

            if handler_class_name not in (
                "FileHandler",
                "RotatingFileHandler",
                "TimedRotatingFileHandler",
                "WatchedFileHandler",
            ):
                continue

            updated_handler = handler.copy()
            log_filename = updated_handler["filename"]
            assert isinstance(log_filename, str)

            log_path = file_prefix_path / Path(log_filename)
            updated_handler["filename"] = log_path.as_posix()
            updated_handlers[key] = updated_handler

        if updated_handlers:
            file_prefix_path.mkdir(exist_ok=True)
            handlers.update(updated_handlers)

        dictConfig(log_config_dict)

    @classmethod
    def get_named_logger(
        cls,
        log_name: str,
        log_level: Optional[str] = None,
        info_message: Optional[str] = None,
    ):
        """Return a named logger.

        Args:
            log_name (str): Name of the logger.
            log_level (str, optional): Valid logging level.
            info_message (str, optional): Message to broadcast on the logger
              info channel.
        """

        named_logger = logging.getLogger(log_name)

        if log_level is not None:
            named_logger.setLevel(log_level)

        if info_message is not None:
            named_logger.info(info_message)

        return named_logger

    def __call__(
        self,
        log_name: str,
        log_level: Optional[str] = None,
        info_message: Optional[str] = None,
        file_prefix: Optional[StrOrPath] = None,
    ):
        """Load the logging configuration and start a named logger in one step.

        Args:
            log_name (str): Name of the logger.
            log_level (str, optional): Valid logging level.
            info_message (str, optional): Message to broadcast on the logger
              info channel.
            file_prefix (str | pathlib.Path, optional): Apply a prefix path to
              file handlers.
        """
        if self.directory_map is not None:
            self.copy_config()
        self.configure_logger(file_prefix=file_prefix)
        return self.get_named_logger(log_name, log_level, info_message)
