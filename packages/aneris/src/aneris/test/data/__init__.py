
from aneris.boundary import DataDefinition
from aneris.entity.data import MetaData


class MyMetaData(MetaData):

    '''Concrete MetaData class for storing metadata for a variable in memory.

    '''

    def __init__(self, props_dict):

        self._name = None
        self._units = None
        self._types = None
        
        super(MyMetaData, self).__init__(props_dict)

        return

    @classmethod
    def get_base_properties(cls):
        '''Properties that must be provided'''
        base_props = super(MyMetaData, cls).get_base_properties()
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


class testDefinition(DataDefinition):

    @property
    def package_name(self):

        return "aneris"

    @property
    def company_name(self):

        return "DTOcean"

    @property
    def local_yaml_dir(self):
        '''The paths of the yaml definition files.'''
        return 'yaml'

    @property
    def  user_yaml_dir(self):
        '''The paths of the yaml definition files.'''
        return None
