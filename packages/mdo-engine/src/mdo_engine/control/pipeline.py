# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 10:53:17 2015

@author: Mathew Topper
"""

import logging
from types import ModuleType
from typing import Sequence

from ..boundary.interface import WeightedInterface
from ..control.sockets import Socket
from ..entity import Hub, Pipeline

# Set up logging
module_logger = logging.getLogger(__name__)


class Sequencer:
    """Class to consider "activation" and "ordering" of interfaces relating
    to a particular class of socket."""

    def __init__(
        self,
        interface_types,
        interface_modules,
        sort_weighted=True,
        warn_import=False,
    ):
        self._sort_weighted = sort_weighted
        self._sockets = self._init_sockets(
            interface_types, interface_modules, warn_import
        )

        return

    def _init_sockets(
        self,
        interface_types: Sequence[str],
        interface_modules: Sequence[ModuleType],
        warn_import=False,
    ):
        """Create a socket classes to locate and communicate with the chosen
        interface class. Store name mappings.
        """

        sockets: dict[str, Socket] = {}

        for cls_name in interface_types:
            socket_obj = Socket()
            for interface_module in interface_modules:
                socket_obj.discover_interfaces(interface_module, cls_name, warn_import)

            sockets[cls_name] = socket_obj

        return sockets

    @property
    def _names(self):
        """Create a socket classes to locate and communicate with the chosen
        interface class. Store name mappings.
        """

        socket_names = {}

        for cls_name, socket_obj in self._sockets.items():
            names_map = socket_obj.get_interface_names(
                sort_weighted=self._sort_weighted
            )

            dupes = list(names_map.values())
            for x in set(names_map.values()):
                dupes.remove(x)

            if dupes:
                dupes_str = ", ".join(dupes)
                errStr = ("Duplicate interfaces names found: {}").format(dupes_str)
                raise ValueError(errStr)

            socket_names[cls_name] = names_map

        return socket_names

    def get_socket(self, interface_type):
        """Get the socket object for the Hub

        Returns:
          mdo_engine.control.sockets.Socket

        """

        return self._sockets[interface_type]

    def create_new_hub(self, interface_type, no_complete=False):
        if interface_type not in self._sockets:
            errStr = ("No socket available for interface type {}").format(
                interface_type
            )
            raise ValueError(errStr)

        new_hub = Hub(interface_type, no_complete)

        log_msg = ("New Hub created for interface {}.").format(interface_type)
        module_logger.info(log_msg)

        return new_hub

    def create_new_pipeline(self, interface_type, no_complete=False):
        if interface_type not in self._sockets:
            errStr = ("No socket available for interface type {}").format(
                interface_type
            )
            raise ValueError(errStr)

        new_pipeline = Pipeline(interface_type, no_complete)

        log_msg = ("New Pipeline created for interface {}.").format(interface_type)
        module_logger.info(log_msg)

        return new_pipeline

    def get_available_names(self, hub):
        """Return all the interface names found as plugins"""

        names_dict = self._names[hub.interface_type]
        names = list(names_dict.keys())

        return names

    def get_scheduled_names(self, hub):
        cls_names = hub.get_scheduled_cls_names()
        scheduled_names = self._filter_names(hub, cls_names)

        return scheduled_names

    def get_completed_names(self, hub):
        cls_names = hub.get_completed_cls_names()
        completed_names = self._filter_names(hub, cls_names)

        return completed_names

    def get_sequenced_names(self, hub):
        cls_names = hub.get_sequenced_cls_names()
        sequenced_names = self._filter_names(hub, cls_names)

        return sequenced_names

    def get_next_name(self, hub):
        interface_cls_name = hub.get_next_scheduled()

        if interface_cls_name is None:
            interface_name = None

        else:
            interface_list = self._filter_names(hub, [interface_cls_name])
            interface_name = interface_list[0]

        return interface_name

    def refresh_interfaces(self, hub):
        completed_names = self.get_completed_names(hub)
        sequenced_names = self.get_sequenced_names(hub)

        all_names = completed_names + sequenced_names

        for interface_name in all_names:
            (interface_cls_name, interface_obj) = self._get_interface(
                hub, interface_name
            )

            # Store an object of the interface
            hub.refresh_interface(interface_cls_name, interface_obj)

        return

    def is_available(self, hub, interface_name):
        """Return all the interface names found as plugins for the given
        hub type"""

        result = False

        names_dict = self._names[hub.interface_type]
        if interface_name in names_dict:
            result = True

        return result

    def get_cls_name(self, hub, interface_name):
        if not self.is_available(hub, interface_name):
            return None

        # Get the interface class name from the module name
        names_dict = self._names[hub.interface_type]
        interface_cls_name = names_dict[interface_name]

        return interface_cls_name

    def get_weight(self, hub, interface_name):
        """Get the weighting of the interface if set"""

        socket = self.get_socket(hub.interface_type)
        interface_cls_name = self.get_cls_name(hub, interface_name)

        if interface_cls_name is None:
            return None

        interface_obj = socket.get_interface_object(interface_cls_name)

        if issubclass(interface_obj, WeightedInterface):
            result = interface_obj.declare_weight()

        else:
            result = None

        return result

    def has_name(self, hub, interface_name):
        """Check if a hub has a sequenced interface name"""

        result = False

        if not self.is_available(hub, interface_name):
            return result

        interface_cls_name = self.get_cls_name(hub, interface_name)
        if interface_cls_name in hub.get_interface_map():
            result = True

        return result

    def sequence(self, hub, interface_name):
        """Sequence an interface for execution."""

        interface_cls_name, interface_obj = self._get_interface(hub, interface_name)

        # Store an object of the interface
        hub.add_interface(interface_cls_name, interface_obj)

        return

    def check_next(self, hub, interface_name):
        interface_cls_name = self.get_cls_name(hub, interface_name)

        if interface_cls_name is None:
            errStr = "Interface {} is not type {}".format(
                interface_name, hub.interface_type
            )
            raise ValueError(errStr)

        hub.check_next_scheduled(interface_cls_name)

        return

    def complete(self, hub, interface_name):
        interface_cls_name = self.get_cls_name(hub, interface_name)

        if interface_cls_name is None:
            errStr = "Interface {} is not type {}".format(
                interface_name, hub.interface_type
            )
            raise ValueError(errStr)

        hub.set_completed(interface_cls_name)

        return

    def is_complete(self, hub, interface_name):
        interface_cls_name = self.get_cls_name(hub, interface_name)

        if interface_cls_name is None:
            errStr = "Interface {} is not type {}".format(
                interface_name, hub.interface_type
            )
            raise ValueError(errStr)

        result = hub.is_completed(interface_cls_name)

        return result

    def _filter_names(self, hub, value_list):
        names_dict = self._names[hub.interface_type]
        result = [k for k, v in names_dict.items() if v in value_list]

        return result

    def _get_interface(self, hub, interface_name):
        socket = self.get_socket(hub.interface_type)
        interface_cls_name = self.get_cls_name(hub, interface_name)

        if interface_cls_name is None:
            errStr = "Interface {} is not type {}".format(
                interface_name, hub.interface_type
            )
            raise ValueError(errStr)

        interface_obj = socket.get_interface_object(interface_cls_name)

        return interface_cls_name, interface_obj
