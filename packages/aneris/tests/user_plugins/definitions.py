
from aneris.boundary import DataDefinition

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
        return None
        
    @property
    def  user_yaml_dir(self):
        '''The paths of the yaml definition files.'''
        return "yaml"   
