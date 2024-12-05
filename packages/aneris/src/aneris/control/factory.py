# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 15:44:28 2015

@author: Mathew Topper
"""

from ..utilities.identity import get_unique_id

class InterfaceFactory(object):
    
    def __init__(self, auto_cls):
        
        self._AutoCls = auto_cls
        
        return
        
    def has_connect_method(self, data_obj):
        
        if self._AutoCls.get_connect_name() is None: return True
        
        result = hasattr(data_obj, self._AutoCls.get_connect_name())
        
        # Check for nullification
        result = (result and not
                  hasattr(data_obj,
                          "_{}".format(self._AutoCls.get_connect_name())))
        
        return result

    def _make_auto_id(self):
    
        new_id = get_unique_id(self._AutoCls.unavailable_ids)
        self._AutoCls.unavailable_ids.append(new_id)
    
        return "{}{}".format(self._AutoCls.__name__, new_id)
        
    def _make_varname_list_method(self, varname):
    
        @classmethod
        def factory_method(cls):
    
            return [varname]
    
        return factory_method
        
    def _make_general_method(self, f):
        
        @classmethod
        def factory_method(cls):
            
            result = f(cls)
                
            return result
                    
        return factory_method
    
    def _make_get_name(self, varname):
    
        @classmethod
        def get_name(cls):
    
            auto_name = "{} {} Interface".format(varname,
                                                 self._AutoCls.__name__)
    
            return auto_name
    
        return get_name
    
    def _make_declare_id_map(self, varname):
    
        @classmethod
        def declare_id_map(cls):
    
            id_map = {"result": varname}
    
            return id_map
    
        return declare_id_map
    
    def _make_connect_method(self, f=None, args=None):
        
        if f is None:
            
            def connect(cls):
            
                return
        
        elif args is None:
            
            def connect(cls):
            
                result = f(cls)
                
                return result
                
        else:
    
            def connect(cls):
                
                result = f(cls, *args)
                
                return result
    
        return connect

    
    def __call__(self, metadata, data_obj):
        
        if not self.has_connect_method(data_obj):
            
            nameStr = self._AutoCls.get_connect_name()
            nullStr = "_{}".format(nameStr)
            errStr = ("Given structure does not contain the required {} "
                      "method or it contains the nullifier method "
                      "{}").format(nameStr, nullStr)
            
            raise AttributeError(errStr)
    
        new_id = self._make_auto_id()
        new_get_name = self._make_get_name(metadata.identifier)
        
        if "declare_inputs" in self._AutoCls.__abstractmethods__:
        
            new_declare_inputs = self._make_varname_list_method(
                                                        metadata.identifier)
            
        else:
            
            new_declare_inputs = self._AutoCls.declare_inputs
            
        if "declare_optional" in self._AutoCls.__abstractmethods__:
        
            new_declare_optional = self._make_varname_list_method(
                                                        metadata.identifier)
            
        else:
            
            new_declare_optional = self._AutoCls.declare_optional
            
        if "declare_outputs" in self._AutoCls.__abstractmethods__:
        
            new_declare_outputs = self._make_varname_list_method(
                                                        metadata.identifier)
            
        else:
            
            new_declare_outputs = self._AutoCls.declare_outputs            

        new_declare_id_map = self._make_declare_id_map(metadata.identifier)
        
        abstract_dict = {"get_name": new_get_name,
                         "declare_inputs": new_declare_inputs,
                         "declare_optional": new_declare_optional,
                         "declare_outputs": new_declare_outputs,
                         "declare_id_map": new_declare_id_map,
                         }
        
        auto_connect_name = self._AutoCls.get_connect_name()
        auto_method_names = self._AutoCls.get_method_names()
        
        if "connect" in self._AutoCls.__abstractmethods__:
            
            auto_method = getattr(data_obj, auto_connect_name)
            new_connect_function = self._make_connect_method(auto_method)
            abstract_dict["connect"] = new_connect_function
            
        elif auto_connect_name is not None:
            
            auto_method = getattr(data_obj, auto_connect_name)
            new_connect_function = self._make_connect_method(auto_method)
            abstract_dict["connect"] = new_connect_function
            
        if auto_method_names is not None:
            
            for method_name in auto_method_names:
            
                auto_method = getattr(data_obj, method_name)
                new_method_function = self._make_general_method(auto_method)
                abstract_dict[method_name] = new_method_function
        
        NewInterface = type(new_id,
                            (self._AutoCls,),
                            abstract_dict
                            )

        return NewInterface
