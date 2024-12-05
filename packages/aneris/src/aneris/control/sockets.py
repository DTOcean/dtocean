# -*- coding: utf-8 -*-
"""
Control classes relating to entities used to pass data to external objects.
"""

# Set up logging
import logging

module_logger = logging.getLogger(__name__)

from collections import OrderedDict

from ..utilities.plugins import Plugin
from ..boundary.interface import WeightedInterface

class Socket(Plugin):

    '''Class to aquire data from external sources described by interface
    plugins.'''

    def __init__(self):

        super(Socket, self).__init__()
        self._interface_classes = {}

        return

    def discover_interfaces(self, package, super_cls, warn_import=False):

        '''Retrieve all of the interfaces. Should be abstract?'''

        log_msg = 'Searching for {} classes'.format(super_cls)
        module_logger.debug(log_msg)

        cls_map = self._discover_plugins(package, super_cls, warn_import)
        self._interface_classes.update(cls_map)

        return

    def add_interface(self, interface_class):

        self._interface_classes[interface_class.__name__] = interface_class

        return

    def get_all_variables(self):

        '''Return a unique list of all valid variables available from the
        interfaces discovered.'''

        all_vars = set()

        # Work through the interfaces
        for cls_name, cls_attr in self._interface_classes.items():

            inputs, _ =  cls_attr.get_inputs(True)
            outputs = cls_attr.get_outputs()

            all_vars = set([])
            all_vars = all_vars.union(set(inputs))
            all_vars = all_vars.union(set(outputs))

        return list(all_vars)

    def get_providing_interfaces(self, variable_id):

        '''Return a list of interfaces which provide the given variable
        identifier as an output.

        Maybe this should output the interface types as well?'''

        providing_interfaces = []

        # Work through the interfaces
        for cls_name, cls_attr in self._interface_classes.items():

            outputs = cls_attr.get_outputs()

            if variable_id in outputs:

                providing_interfaces.append(cls_name)

        return providing_interfaces
        
    def get_receiving_interfaces(self, variable_id):

        '''Return a list of interfaces that use the given variable identifier
        as an input.

        Maybe this should output the interface types as well?'''

        receiving_interfaces = []

        # Work through the interfaces
        for cls_name, cls_attr in self._interface_classes.items():

            inputs, _ = cls_attr.get_inputs(True)
                
            for input_var in inputs:
                
                if variable_id == input_var:
                    receiving_interfaces.append(cls_name)
                    break

        return receiving_interfaces

    def get_interface_object(self, interface_cls_name):

        '''Return an instance of the interface class given by the interface
        name'''

        cls_attr = self._get_interface_class(interface_cls_name)
        interface_instance = cls_attr()

        return interface_instance

    def get_interface_names(self, sort_weighted=True):

        '''Return the names and classes of all the discovered interfaces'''

        interface_names = []
        class_names = []
        weights = []

        # Work through the interfaces
        for cls_name, cls_attr in self._interface_classes.items():

            interface_names.append(cls_attr.get_name())
            class_names.append(cls_name)

            if issubclass(cls_attr, WeightedInterface):
                weights.append(cls_attr.declare_weight())
                
        if weights and sort_weighted:

            sorted_lists = sorted(zip(interface_names, class_names, weights),
                                  key=lambda x: x[2])
            (sorted_names,
             sorted_classes,
             sorted_weights) = [[x[i] for x in sorted_lists] for i in range(3)]
             
            monotonic = all(x<y for x, y in zip(sorted_weights,
                                                sorted_weights[1:]))
                                                
            if not monotonic:
                
                errStr = ("Interface weights are not monotonic. Found "
                          "weights: {}").format(sorted_weights)
                raise ValueError(errStr)

            names = OrderedDict(zip(sorted_names, sorted_classes))
            
        else:
            
            names = dict(zip(interface_names, class_names))
            
        return names
        
    def _get_interface_class(self, interface_cls_name):
        
        cls_attr = self._interface_classes[interface_cls_name]

        return cls_attr


class NamedSocket(Socket):

    '''Class to aquire data from a named interface type.'''

    def __init__(self, interface_name):

        super(NamedSocket, self).__init__()
        self._interface_name = interface_name

        return

    def discover_interfaces(self, package):

        '''Retrieve all of the interfaces'''

        super(NamedSocket, self).discover_interfaces(package,
                                                     self._interface_name)

        return

