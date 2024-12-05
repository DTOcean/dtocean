# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 10:53:17 2015

@author: Mathew Topper
"""

from copy import deepcopy
from collections import OrderedDict

class Hub(object):
    
    """A Hub groups a particular class of interfaces and calculates the
    data requirements of each interface considering all the input and outputs
    of the others.
    
    Args:
      interface_name (str): The name of the interface class to control with the
        hub.
    
    """

    
    def __init__(self, interface_type,
                       no_complete=False):
        
        self.interface_type = interface_type
        self.has_order = False
        self.force_completed = False
        self._no_complete = no_complete
        self._id = None
        self._scheduled_interface_map = OrderedDict()
        self._completed_interface_map = OrderedDict()
                
        return
        
    def add_interface(self, interface_cls_name, interface_obj):
        
        """Assosiate an interface object to the Hub
        
        Args:
          interface_cls_name (str): The name of the interface class
          interface_obj (aneris.boundary.interface.Interface): An object of 
            the interface class
            
        """
        
        if (interface_cls_name in self._scheduled_interface_map or
            interface_cls_name in self._completed_interface_map):
            
            errStr = ("Interface {} is already associated to the "
                      "hub.").format(interface_cls_name)
            raise KeyError(errStr)
            
        self._scheduled_interface_map[interface_cls_name] = interface_obj

        return
        
    def remove_interface(self, interface_cls_name):
        
        """Dissassociate an interface from the hub
        
        Args:
          interface_cls_name (str): The name of the interface class
          
        """
        
        if interface_cls_name in self._scheduled_interface_map:
            
            del self._scheduled_interface_map[interface_cls_name]
            
        elif interface_cls_name in self._completed_interface_map:
            
            del self._completed_interface_map[interface_cls_name]
            
        else:
            
            errStr = ("Class {} not found in interface "
                      "maps.").format(interface_cls_name)
            raise KeyError(errStr)

        return
    
    def refresh_interface(self, interface_cls_name, interface_obj):
        
        """Replace the interface object for a given class name.
        
        Args:
          interface_cls_name (str): The name of the interface class
          interface_obj (aneris.boundary.interface.Interface): An object of 
            the interface class
            
        """
        
        if interface_cls_name in self._scheduled_interface_map:
            
            self._scheduled_interface_map[interface_cls_name] = interface_obj
            
        elif interface_cls_name in self._completed_interface_map:
            
            self._completed_interface_map[interface_cls_name] = interface_obj
            
        else:
            
            errStr = ("Class {} not found in interface "
                      "maps.").format(interface_cls_name)
            raise KeyError(errStr)

        return
        
    def get_interface_obj(self, interface_cls_name):
        
        """Retrieve an interface object
        
        Args:
          interface_cls_name (str): The name of the interface class
          
        Returns:
          aneris.boundary.interface.Interface
          
         """
        
        if interface_cls_name in self._scheduled_interface_map:
            
            obj = self._scheduled_interface_map[interface_cls_name]
            
        elif interface_cls_name in self._completed_interface_map:
            
            obj = self._completed_interface_map[interface_cls_name]
            
        else:
            
            errStr = ("Class {} not found in interface "
                      "maps.").format(interface_cls_name)
            raise KeyError(errStr)
        
        return deepcopy(obj)
        
    def get_preceding_interfaces(self, interface_cls_name,
                                       ignore_completed=False):
                
        # If the hub has no ordering then return an empty dictionary
        if not self.has_order:
            
            return {}
        
        elif ignore_completed:
        
            all_interfaces = self.get_scheduled_map()  
        
        else:
            
            all_interfaces = self.get_interface_map()  
            
        preceeding_interfaces = OrderedDict()
            
        if interface_cls_name in all_interfaces:
            
            interface_names = all_interfaces.keys()
            interface_index = interface_names.index(interface_cls_name)

            for i in interface_names[:interface_index]:
                
                preceeding_interfaces[i] = all_interfaces[i]
            
        return preceeding_interfaces
        
    def get_upcoming_interfaces(self, interface_cls_name,
                                      ignore_sequenced=False):
                
        # If the hub has no ordering then return an empty dictionary
        if not self.has_order:
            
            return {}
            
        elif ignore_sequenced:
            
            all_interfaces = self.get_completed_map()
            
        else:
            
            all_interfaces = self.get_interface_map()
        
        upcoming_interfaces = OrderedDict()
            
        if interface_cls_name in all_interfaces:
            
            interface_names = all_interfaces.keys()
            interface_index = interface_names.index(interface_cls_name)
            
            for i in interface_names[interface_index:]:
    
                upcoming_interfaces[i] = all_interfaces[i]
            
        return upcoming_interfaces
        
    def get_completed_map(self):
        
        """Retrieve all the completed interfaces in a dictionary
          
        Returns:
          dict: aneris.boundary.interface.Interface objects keyed by their 
            class names
          
        """
        
        # Reverse the order
        names = self.get_completed_cls_names()
        completed_map = OrderedDict()
        
        for key in names:
            completed_map[key] = self._completed_interface_map[key]
        
        return completed_map
        
    def get_scheduled_map(self):
        
        """Retrieve all the scheduled (not completed) interfaces in a
        dictionary
          
        Returns:
          dict: aneris.boundary.interface.Interface objects keyed by their 
            class names
          
        """
        
        scheduled_map = deepcopy(self._scheduled_interface_map)
        
        return scheduled_map
        
    def get_interface_map(self):
        
        """Retrieve all the sequenced interfaces in a dictionary
          
        Returns:
          dict: aneris.boundary.interface.Interface objects keyed by their 
            class names
          
        """
        
        unified_map = self.get_scheduled_map()
        
        # Add the reversed completed map
        names = self.get_completed_cls_names()
        
        for k in names:
            unified_map[k] = self._completed_interface_map[k]
        
        return unified_map
        
    def get_next_scheduled(self):
        
        scheduled_keys = self._scheduled_interface_map.keys()
        
        if scheduled_keys:
            return scheduled_keys[0]
        else:
            return None
                
    def get_last_completed(self):
        
        completed_keys = self._completed_interface_map.keys()
        
        if not completed_keys:
            
            result = None
            
        else:
            
            result = completed_keys[0]
        
        return result
        
    def get_scheduled_cls_names(self):
                
        all_names = self._scheduled_interface_map.keys()
        
        return all_names
        
    def get_completed_cls_names(self):
        
        all_names = list(reversed(self._completed_interface_map.keys()))
                
        return all_names
        
    def get_sequenced_cls_names(self):
        
        all_names = []
        all_names.extend(self.get_scheduled_cls_names())
        all_names.extend(self.get_completed_cls_names())
        
        return all_names
                
    def set_completed(self, interface_cls_name):
        
        if self._no_complete: return
        
        if interface_cls_name in self.get_scheduled_cls_names():
            
            obj = self._scheduled_interface_map[interface_cls_name]
            del self._scheduled_interface_map[interface_cls_name]
                        
        else:
            
            errStr = ("Class {} not found in scheduled interface "
                      "map.").format(interface_cls_name)
            raise KeyError(errStr)
        
        # Put the completed interface at position 0 in the dict.
        new_completed = OrderedDict()
        new_completed[interface_cls_name] = obj
        new_completed.update(self._completed_interface_map)

        self._completed_interface_map = new_completed
                        
        return
        
    def is_completed(self, interface_cls_name):

        if interface_cls_name in self._completed_interface_map.keys():
            
            result = True
            
        else:
            
            result = False
            
        return result
        
    def undo(self):
        
        last_key = self.get_last_completed()
        
        if last_key is None: return False
            
        obj = self._completed_interface_map[last_key]
        del self._completed_interface_map[last_key]
        
        # Put the scheduled interface at position 0 in the dict.
        new_scheduled = OrderedDict()
        new_scheduled[last_key] = obj
        new_scheduled.update(self._scheduled_interface_map)
                    
        self._scheduled_interface_map = new_scheduled
                        
        return True
        
    def rollback(self, interface_cls_name):
        
        if interface_cls_name not in self.get_completed_cls_names():
            
            errStr = ("Class {} not found in completed interface "
                      "map.").format(interface_cls_name)
            raise KeyError(errStr)
        
        while interface_cls_name in self.get_completed_cls_names():
            
            self.undo()
            
        return
        
    def reset(self):
        
        while self.undo(): continue
            
        return

    def check_next_scheduled(self, interface_cls_name):
        
        '''If possible move the given interface to being the next
        scheduled interface otherwise throw an error.'''
        
        if interface_cls_name in self._scheduled_interface_map:
            
            pass
            
        elif interface_cls_name in self._completed_interface_map:
            
            self.rollback(interface_cls_name)
            
        else:
            
            errStr = ("Interface {} can not be "
                      "scheduled.").format(interface_cls_name)
            raise ValueError(errStr)
            
        return

    @classmethod
    def _last_dict_key(cls, ordered_dict):
        
        if not ordered_dict:
            
            last_key = None
            
        else:
        
            last_key = next(reversed(ordered_dict))
        
        return last_key


class Pipeline(Hub):
    
    """Class to consider "activation" and "ordering" of data handlers."""
    
    def __init__(self, interface_name,
                       no_complete=False):
        
        super(Pipeline, self).__init__(interface_name,
                                       no_complete)
        self.has_order = True
                
        return
        
    def get_next_scheduled(self):
        
        if not self._scheduled_interface_map:
            
            last_key = None
            
        else:
        
            last_key = next(iter(self._scheduled_interface_map))
        
        return last_key
        
    def set_completed(self, interface_cls_name=None):
        
        '''Update the next interface to the next availble.
        Set to None if the last interface has been reached'''
        
        next_cls_name = self.get_next_scheduled()
        
        if (interface_cls_name is not None and
                next_cls_name != interface_cls_name):
                    
            errStr = ("Interface {} is not the next interface in the "
                      "pipeline.").format(interface_cls_name)
            raise ValueError(errStr)
        
        super(Pipeline, self).set_completed(next_cls_name)
        
        return
        
    def check_next_scheduled(self, interface_cls_name):
        
        '''If possible move the given interface to being the next
        scheduled interface otherwise throw an error.'''
        
        if self.get_next_scheduled() == interface_cls_name:
            
            pass
            
        elif interface_cls_name in self._completed_interface_map:
            
            self.rollback(interface_cls_name)
            
        else:
            
            errStr = ("Interface {} can not be "
                      "scheduled.").format(interface_cls_name)
            raise ValueError(errStr)
            
        return
