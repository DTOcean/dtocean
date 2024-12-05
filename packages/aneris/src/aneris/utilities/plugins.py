# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 17:10:16 2015

@author: Mathew Topper
"""

import pyclbr
import logging
import pkgutil
import traceback
from importlib import import_module

# Set up logging
module_logger = logging.getLogger(__name__)


class Plugin(object):

    '''Plugin discovery control classes.'''

    def _discover_plugins(self, package, super_cls, warn_import=False):

        '''Retrieve all of the matching subclass names found in the package'''

#        interfaces = import_module(package)

        names = get_module_names_from_package(package)
        names.append(package.__name__)

        cls_map = {}

        for mod_name in names:

            data_sub_mods = get_subclass_names_from_module(mod_name,
                                                           super_cls)

            for cls_name in data_sub_mods:

                class_attr = get_class_attr(cls_name,mod_name, warn_import)
                if class_attr is not None: cls_map[cls_name] = class_attr

        return cls_map


def get_module_names_from_package(package):

    '''Return the names of modules in the given package'''

    prefix = package.__name__ + "."
    module_names = get_module_names_from_paths(package.__path__, prefix)

    return module_names


def get_module_names_from_paths(package_paths, prefix=''):

    '''Return the names of modules in the given list of package paths'''

    module_names = []

    for _, modname, _ in pkgutil.iter_modules(package_paths, prefix):

        module_names.append(modname)

    return module_names


def get_class_descriptions_from_module(module_name):

    '''Get the classes contained in a module as a pyclbr dictionary.

    This wont work universally but it can be used for the current module as
    long as we keep the source code intact. See:

    https://docs.python.org/2/library/pyclbr.html
    '''

    print(module_name)
    clsmembers = pyclbr.readmodule(module_name)

    return clsmembers


def get_subclass_names_from_module(module_name, super_name):

    '''Get all classes in a module that are subclasses of the given super
    class type'''

    clsmembers = get_class_descriptions_from_module(module_name)

    match_super = []

    for description in clsmembers.values():

        all_supers = unroll_description(description)

        if super_name in all_supers:

            match_super.append(description.name)

    return match_super


def unroll_description(description, super_strs=None):

    '''Recurse through the pyclbr classes to find all base classes'''

    if super_strs is None: super_strs = []

    for supers in description.super:

        if isinstance(supers, pyclbr.Class):

            super_strs.append(supers.name)
            super_strs = unroll_description(supers, super_strs)

        else:

            super_strs.append(supers)

    return super_strs


def create_object_map(class_map):

    '''Take a mapping of class and module names and return a similar mapping
    but with instances of the classes themselves.'''

    object_map = {}

    for cls_name, cls_attr in class_map.items():

        object_map[cls_name] = cls_attr()

    return object_map


def create_object_list(class_map):

    '''Take a mapping of class and module names and return a list with
    instances of the classes themselves.'''

    object_list = []

    for cls_name, cls_attr in class_map.items():

        object_list.append(cls_attr())

    return object_list


def get_class_attr(cls_name, mod_name, warn_import=False):

    '''Return a class attribute from the class and module names.'''

    module = get_module_attr(mod_name, warn_import)

    if module is None:
        return
    else:
        return getattr(module, cls_name)


def get_module_attr(mod_name, warn_import=False):

    '''Return a module attribute.'''
    
    try:
        module = import_module(mod_name)
    except Exception:
        msgStr = ("Importing module {} failed with an unexpected "
                  "error:\n{}").format(mod_name, traceback.format_exc())
        if warn_import:
            module_logger.warn(msgStr)
            return
        else:
            raise Exception(msgStr)

    return module


def get_public_attributes(cls_attr):

    '''Return all the public attributes contained in a class'''

    public_attrs = (name for name in dir(cls_attr) if not name.startswith('_'))

    return public_attrs

