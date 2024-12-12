
import builtins

from copy import deepcopy

from mdo_engine.boundary import DataDefinition, Structure

class autoDefinition(DataDefinition):

    @property
    def package_name(self):

        return "mdo_engine"

    @property
    def company_name(self):

        return "DTOcean"

    @property
    def local_yaml_dir(self):
        '''The paths of the yaml definition files.'''
        return 'auto'

    @property
    def  user_yaml_dir(self):
        '''The paths of the yaml definition files.'''
        return None

class UnitData(Structure):

    '''A single item of data'''

    def get_data(self, raw, meta_data):

        return raw

    def get_value(self, data):

        return deepcopy(data)


class Simple(Structure):

    '''Simple single value data such as a bool, str, int or float'''

    def get_data(self, raw, meta_data):

        simple = raw

        if meta_data._types:

            try:
                simple_type = getattr(builtins, meta_data._types)
                simple = simple_type(simple)
            except TypeError:
                errStr = ("Raw data is of incorrect type. Should be "
                          "{}, but is {}.").format(meta_data._types,
                                                   type(simple))
                raise TypeError(errStr)

        return simple

    def get_value(self, data):

        return deepcopy(data)

class AutoSimple(Simple):

    '''Simple single value data such as a bool, str, int or float'''

    @staticmethod
    def auto_connect(self):

        self.data.result = self._two * self.meta.result.auto

        return
    
    @staticmethod
    def get_valid_extensions(self):

        return [".spt"]

