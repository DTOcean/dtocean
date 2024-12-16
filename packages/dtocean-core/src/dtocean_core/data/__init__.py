# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2024 Mathew Topper
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from mdo_engine.boundary import DataDefinition
from mdo_engine.entity.data import MetaData

class CoreMetaData(MetaData):

    '''Concrete MetaData class for storing metadata for a variable in memory.

    '''

    def __init__(self, props_dict):

        self._title = None
        self._description = None
        self._category = None
        self._group = None
        self._auto_only = None
        self._types = None
        self._tables = None
        self._units = None
        self._labels = None
        self._valid_values = None
        self._minimums = None
        self._minimum_equals = None
        self._maximums = None
        self._maximum_equals = None
        self._experimental = None
        
        super(CoreMetaData, self).__init__(props_dict)

        return

    @classmethod
    def get_base_properties(cls):
        '''Properties that must be provided'''
        base_props = super(CoreMetaData, cls).get_base_properties()
        base_props.extend(["title"])
        return base_props
        
    @property
    def title(self):
        '''A short name for the data'''
        
        if self.experimental is None:
            return self._title
        
        if True in self.experimental:
            title = "{} (Experimental)".format(self._title)
        else:
            title = self._title
        
        return title
        
    @property
    def description(self):
        '''A longer description of the data'''
        return self._description
    
    @property
    def category(self):
        '''Highest categorisation. Can be none if contained in variable id'''
        return self._category
    
    @property
    def group(self):
        '''Optional grouping of variables below category or subcategory'''
        return self._group
    
    @property
    def auto_only(self):
        '''Call auto_db method only if this variable has a value'''
        return self._auto_only
        
    @property
    def types(self):
        '''A list of data type can also be specified which may be used
        within the data structure'''
        return self._types

    @property
    def tables(self):
        '''List of database tables used as an interface to the data.'''
        return self._tables

    @property
    def units(self):
        '''The SI units of the data'''
        return self._units
        
    @property
    def labels(self):
        '''Short names for dimensions of data'''
        return self._labels
        
    @property
    def minimums(self):
        '''Data must be greater than this value'''
        return self._minimums
    
    @property
    def minimum_equals(self):
        '''Data must be greater than or equal to this value'''
        return self._minimum_equals
    
    @property
    def maximums(self):
        '''Data must be less than this value'''
        return self._maximums
    
    @property
    def maximum_equals(self):
        '''Data must be less than or equal to this value'''
        return self._maximum_equals
    
    @property
    def valid_values(self):
        '''List of valid values for discrete data'''
        return self._valid_values

    @property
    def experimental(self):
        '''List of experimental values or entire variable if list contains
        True'''
        return self._experimental


class CoreData(DataDefinition):

    def __init__(self):

        super(CoreData, self).__init__()

        return

    @property
    def package_name(self):

        return "dtocean-core"

    @property
    def company_name(self):

        return "DTOcean"

    @property
    def local_yaml_dir(self):
        '''The paths of the yaml definition files.'''
        return "yaml"

    @property
    def  user_yaml_dir(self):
        '''The paths of the yaml definition files.'''
        return None

