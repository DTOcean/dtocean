# -*- coding: utf-8 -*-
"""This module defines a class DataDefinition which is subclassed in order
to provide information on where the data description files are located on the
file system.

.. module:: data
   :platform: Windows
   :synopsis: Data description location specification
   
.. moduleauthor:: Mathew Topper <mathew.topper@tecnalia.com>
"""

import os
import abc
import sys
import glob
import pickle
import datetime as dt
from types import NoneType
from numbers import Number

import pandas as pd
import pandas.core.indexes 

from polite.paths import object_dir, UserDataDirectory

from ..utilities.files import yaml_to_py

# Compatibility for old pandas versions
sys.modules['pandas.indexes'] = pandas.core.indexes


class DataDefinition(object):

    __metaclass__ = abc.ABCMeta

    @property
    @abc.abstractmethod
    def package_name(self):

        return

    @property
    @abc.abstractmethod
    def company_name(self):

        return

    @property
    @abc.abstractmethod
    def local_yaml_dir(self):

        '''Directory path for retrieving the data catalog definitions
        in YAML format. This directory is relative to this definition'''

        return

    @property
    @abc.abstractmethod
    def user_yaml_dir(self):

        '''Directory path for retrieving the data catalog definitions
        in YAML format'''

        return

    def get_metadef_lists(self):

        for abs_yaml_path in self._get_yaml_local_paths():

            yield yaml_to_py(abs_yaml_path)

        for abs_yaml_path in self._get_yaml_user_paths():

            yield yaml_to_py(abs_yaml_path)

        return

    def _get_yaml_paths(self, yaml_dir):

        '''Get the absolute paths to the yaml files'''

        search_ext = ".yaml"

        yaml_wcard = "{}/*{}".format(yaml_dir, search_ext)
        yaml_paths = [path for path in glob.glob(yaml_wcard)]

        return yaml_paths

    def _get_yaml_local_paths(self):

        '''Get the absolute paths to the yaml files from a local directory'''

        if self.local_yaml_dir is None: return []

        local_dir = object_dir(self)
        yaml_dir = os.path.join(local_dir, self.local_yaml_dir)
        yaml_paths = self._get_yaml_paths(yaml_dir)

        return yaml_paths

    def _get_yaml_user_paths(self):

        '''Get the absolute paths to the yaml files from the user directory'''

        if self.user_yaml_dir is None: return []

        local_dir = UserDataDirectory(self.package_name,
                                      self.company_name)

        yaml_dir = os.path.join(local_dir.get_path(), self.user_yaml_dir)
        yaml_paths = self._get_yaml_paths(yaml_dir)

        return yaml_paths


class Structure(object):
    
    '''Boundary class to define creation and and access to Data objects. Also 
    contains methods used for automatic interfaces associated to the Structure
    class'''
    
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def get_data(self, raw, meta_data):
        
        """Returns a structured data object from raw input and meta data"""
        
        return
    
    @abc.abstractmethod
    def get_value(self, data):
        
        return
    
    def save_value(self, data, root_path):
        
        file_path = "{}.pkl".format(root_path)
        data_value = self.get_value(data)
        
        with open(file_path, "wb") as fstream:
            pickle.dump(data_value, fstream, -1)
        
        return file_path
    
    def load_data(self, file_path):
            
        # Bypass the get_data method in this case, but it may be necesary to
        # call it for loading from other file types. In some cases unpickling
        # is unique, such as opening old versions of pandas dataframes.
        
        try:
                
            with open(file_path, "rb") as fstream:
                data = pickle.load(fstream)
        
        except ImportError:
            
            data = pd.read_pickle(file_path)
        
        return data
    
    @classmethod
    def equals(cls, left, right): 
        
        return left == right
    
    def __call__(self, data):
        
        value = self.get_value(data)
        
        # If data is immutable do not check for equivalence.
        if isinstance(data, (str,
                             tuple,
                             bool,
                             frozenset,
                             NoneType,
                             Number,
                             dt.date,
                             dt.time,
                             dt.datetime,
                             dt.timedelta,
                             dt.tzinfo)):
            
            return value
        
        elif value is data:
            
            errStr = ("Value returned from structure {} must not be the "
                      "original data").format(self.__class__.__name__)
            raise RuntimeError(errStr)
        
        return value


class SerialBox(object):
    
    def __init__(self, identifier, load_dict):
        
        self.identifier = identifier
        self.load_dict = load_dict
        
        return

