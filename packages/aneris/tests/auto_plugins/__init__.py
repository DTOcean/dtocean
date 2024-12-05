

from aneris.entity.data import MetaData

class AutoMetaData(MetaData):

    '''Concrete MetaData class for storing metadata for a variable in memory.

    '''

    def __init__(self, props_dict):
        
        
        self._name = None
        self._units = None
        self._types = None
        self._auto = None

        super(AutoMetaData, self).__init__(props_dict)
        
        return

    @classmethod
    def get_base_properties(cls):
        '''Properties that must be provided'''
        base_props = super(AutoMetaData, cls).get_base_properties()
        base_props.extend(["name"])
        return base_props

    @property
    def name(self):
        '''The name of the data'''
        return self._name

    @property
    def units(self):
        '''The units of the data'''
        return self._units

    @property
    def types(self):
        '''The types of the data'''
        return self._types
        
    @property
    def auto(self):
        '''Some data to trigger creation of an auto interface'''
        return self._auto  
