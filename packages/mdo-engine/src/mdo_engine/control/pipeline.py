# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 10:53:17 2015

@author: Mathew Topper
"""

import logging
from types import ModuleType
from typing import Any, OrderedDict, Sequence

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
        interface_modules: Sequence[ModuleType],
        sort_weighted=True,
        warn_import=False,
    ):
        self._sort_weighted = sort_weighted
        self._sockets = self._init_sockets(
            interface_types, interface_modules, warn_import
        )

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
                socket_obj.discover_interfaces(
                    interface_module, cls_name, warn_import
                )

            sockets[cls_name] = socket_obj

        return sockets

    @property
    def _names(self) -> dict[str, OrderedDict | dict]:
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
                errStr = ("Duplicate interfaces names found: {}").format(
                    dupes_str
                )
                raise ValueError(errStr)

            socket_names[cls_name] = names_map

        return socket_names

    def get_socket(self, interface_type: str):
        """Get the socket object for the Hub

        Returns:
          mdo_engine.control.sockets.Socket

        """

        return self._sockets[interface_type]

    def create_new_hub(self, interface_type: str, no_complete=False) -> Hub:
        if interface_type not in self._sockets:
            errStr = ("No socket available for interface type {}").format(
                interface_type
            )
            raise ValueError(errStr)

        new_hub = Hub(interface_type, no_complete)

        log_msg = ("New Hub created for interface {}.").format(interface_type)
        module_logger.info(log_msg)

        return new_hub

    def create_new_pipeline(
        self,
        interface_type: str,
        no_complete=False,
    ) -> Pipeline:
        if interface_type not in self._sockets:
            errStr = ("No socket available for interface type {}").format(
                interface_type
            )
            raise ValueError(errStr)

        new_pipeline = Pipeline(interface_type, no_complete)

        log_msg = ("New Pipeline created for interface {}.").format(
            interface_type
        )
        module_logger.info(log_msg)

        return new_pipeline

    def get_available_names(self, hub: Hub):
        """Return all the interface names found as plugins"""

        names_dict = self._names[hub.interface_type]
        names = list(names_dict.keys())

        return names

    def get_scheduled_names(self, hub: Hub):
        cls_names = hub.get_scheduled_cls_names()
        scheduled_names = self._filter_names(hub, cls_names)

        return scheduled_names

    def get_completed_names(self, hub: Hub):
        cls_names = hub.get_completed_cls_names()
        completed_names = self._filter_names(hub, cls_names)

        return completed_names

    def get_sequenced_names(self, hub: Hub) -> list[str]:
        cls_names = hub.get_sequenced_cls_names()
        sequenced_names = self._filter_names(hub, cls_names)
        return sequenced_names

    def get_next_name(self, hub: Hub):
        interface_cls_name = hub.get_next_scheduled()

        if interface_cls_name is None:
            interface_name = None

        else:
            interface_list = self._filter_names(hub, [interface_cls_name])
            interface_name = interface_list[0]

        return interface_name

    def refresh_interfaces(self, hub: Hub):
        completed_names = self.get_completed_names(hub)
        sequenced_names = self.get_sequenced_names(hub)

        all_names = completed_names + sequenced_names

        for interface_name in all_names:
            (interface_cls_name, interface_obj) = self._get_interface(
                hub, interface_name
            )

            # Store an object of the interface
            hub.refresh_interface(interface_cls_name, interface_obj)

    def is_available(self, hub: Hub, interface_name: str):
        """Return all the interface names found as plugins for the given
        hub type"""

        result = False

        names_dict = self._names[hub.interface_type]
        if interface_name in names_dict:
            result = True

        return result

    def get_cls_name(self, hub: Hub, interface_name: str):
        if not self.is_available(hub, interface_name):
            return None

        # Get the interface class name from the module name
        names_dict = self._names[hub.interface_type]
        interface_cls_name = names_dict[interface_name]

        return interface_cls_name

    def get_weight(self, hub: Hub, interface_name: str):
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

    def has_name(self, hub: Hub, interface_name: str):
        """Check if a hub has a sequenced interface name"""

        result = False

        if not self.is_available(hub, interface_name):
            return result

        interface_cls_name = self.get_cls_name(hub, interface_name)
        if interface_cls_name in hub.get_interface_map():
            result = True

        return result

    def sequence(self, hub: Hub, interface_name: str):
        """Sequence an interface for execution."""

        interface_cls_name, interface_obj = self._get_interface(
            hub, interface_name
        )

        # Store an object of the interface
        hub.add_interface(interface_cls_name, interface_obj)

    def check_next(self, hub: Hub, interface_name: str):
        interface_cls_name = self.get_cls_name(hub, interface_name)

        if interface_cls_name is None:
            errStr = "Interface {} is not type {}".format(
                interface_name, hub.interface_type
            )
            raise ValueError(errStr)

        hub.check_next_scheduled(interface_cls_name)

    def complete(self, hub: Hub, interface_name: str):
        interface_cls_name = self.get_cls_name(hub, interface_name)

        if interface_cls_name is None:
            errStr = "Interface {} is not type {}".format(
                interface_name, hub.interface_type
            )
            raise ValueError(errStr)

        hub.set_completed(interface_cls_name)

    def is_complete(self, hub: Hub, interface_name: str):
        interface_cls_name = self.get_cls_name(hub, interface_name)

        if interface_cls_name is None:
            errStr = "Interface {} is not type {}".format(
                interface_name, hub.interface_type
            )
            raise ValueError(errStr)

        result = hub.is_completed(interface_cls_name)

        return result

    def dump_hub(self, hub: Hub) -> dict[str, Any]:
        scheduled_interface_names = [
            x.get_name() for x in hub._scheduled_interface_map.values()
        ]
        completed_interface_names = [
            x.get_name() for x in hub._completed_interface_map.values()
        ]

        return {
            "type": hub.__class__.__name__,
            "interface_type": hub.interface_type,
            "has_order": hub.has_order,
            "force_completed": hub.force_completed,
            "no_complete": hub._no_complete,
            "scheduled_interface_names": scheduled_interface_names,
            "completed_interfaces_names": completed_interface_names,
        }

    def load_hub(self, hub_dict: dict[str, Any]) -> Hub | Pipeline:
        if hub_dict["type"] == "Hub":
            hub_class = Hub
        elif hub_dict["type"] == "Pipeline":
            hub_class = Pipeline
        else:
            raise RuntimeError("Hub type not recognised")

        hub = hub_class(hub_dict["interface_type"])
        hub.has_order = hub_dict["has_order"]
        hub.force_completed = hub_dict["force_completed"]
        hub._no_complete = hub_dict["no_complete"]

        for interface_name in hub_dict["scheduled_interface_names"]:
            interface_cls_name, interface_obj = self._get_interface(
                hub,
                interface_name,
            )
            hub._scheduled_interface_map[interface_cls_name] = interface_obj

        for interface_name in hub_dict["completed_interfaces_names"]:
            interface_cls_name, interface_obj = self._get_interface(
                hub,
                interface_name,
            )
            hub._completed_interface_map[interface_cls_name] = interface_obj

        return hub

    def _filter_names(self, hub: Hub, value_list: list[str]):
        names_dict = self._names[hub.interface_type]
        result = [k for k, v in names_dict.items() if v in value_list]
        return result

    def _get_interface(self, hub: Hub, interface_name: str):
        socket = self.get_socket(hub.interface_type)
        interface_cls_name = self.get_cls_name(hub, interface_name)

        if interface_cls_name is None:
            errStr = "Interface {} is not type {}".format(
                interface_name, hub.interface_type
            )
            raise ValueError(errStr)

        interface_obj = socket.get_interface_object(interface_cls_name)

        return interface_cls_name, interface_obj
