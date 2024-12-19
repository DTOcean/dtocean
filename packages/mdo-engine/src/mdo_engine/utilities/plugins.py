# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 17:10:16 2015

@author: Mathew Topper
"""

import importlib
import inspect
import logging
import pkgutil
import traceback

# Set up logging
module_logger = logging.getLogger(__name__)


class Plugin:
    """Plugin discovery control classes."""

    def _discover_plugins(self, package, super_cls, warn_import=False):
        """Retrieve all of the matching subclass names found in the package"""

        names = get_module_names_from_package(package)
        names.append(package.__name__)

        cls_map: dict[str, type] = {}

        for mod_name in names:
            data_sub_mods = get_subclass_names_from_module(mod_name, super_cls)

            for cls_name in data_sub_mods:
                class_attr = get_class_attr(cls_name, mod_name, warn_import)
                if class_attr is not None:
                    cls_map[cls_name] = class_attr

        return cls_map


def get_module_names_from_package(package):
    """Return the names of modules in the given package"""

    prefix = package.__name__ + "."
    module_names = get_module_names_from_paths(package.__path__, prefix)

    return module_names


def get_module_names_from_paths(package_paths, prefix=""):
    """Return the names of modules in the given list of package paths"""

    module_names = []

    for _, modname, _ in pkgutil.iter_modules(package_paths, prefix):
        module_names.append(modname)

    return module_names


def get_class_descriptions_from_module(module_name):
    """Get the classes contained in a module as a dictionary."""

    def filter(y):
        return lambda x: inspect.isclass(x) and x.__module__ == y

    clsmembers = inspect.getmembers(
        importlib.import_module(module_name), filter(module_name)
    )
    return dict(clsmembers)


def get_subclass_names_from_module(module_name, super_name):
    """Get all classes in a module that are subclasses of the given super
    class type"""

    match_super = []

    try:
        clsmembers = get_class_descriptions_from_module(module_name)
    except ImportError:
        return match_super

    for name, cls in clsmembers.items():
        if name == super_name:
            continue

        all_supers = [x.__name__ for x in inspect.getmro(cls)]

        if super_name in all_supers:
            match_super.append(name)

    return match_super


def create_object_map(class_map):
    """Take a mapping of class and module names and return a similar mapping
    but with instances of the classes themselves."""

    object_map = {}

    for cls_name, cls_attr in class_map.items():
        object_map[cls_name] = cls_attr()

    return object_map


def create_object_list(class_map):
    """Take a mapping of class and module names and return a list with
    instances of the classes themselves."""

    object_list = []

    for cls_name, cls_attr in class_map.items():
        object_list.append(cls_attr())

    return object_list


def get_class_attr(cls_name, mod_name, warn_import=False):
    """Return a class attribute from the class and module names."""

    module = get_module_attr(mod_name, warn_import)

    if module is None:
        return
    else:
        return getattr(module, cls_name)


def get_module_attr(mod_name, warn_import=False):
    """Return a module attribute."""

    try:
        module = importlib.import_module(mod_name)
    except Exception:
        msgStr = (
            "Importing module {} failed with an unexpected error:\n{}"
        ).format(mod_name, traceback.format_exc())
        if warn_import:
            module_logger.warning(msgStr)
            return
        else:
            raise Exception(msgStr)

    return module


def get_public_attributes(cls_attr):
    """Return all the public attributes contained in a class"""

    public_attrs = (name for name in dir(cls_attr) if not name.startswith("_"))

    return public_attrs
