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

import numpy as np
from mdo_engine.boundary.interface import MaskVariable, QueryInterface

from . import ProjectInterface


class SystemTypeInterface(ProjectInterface):
    """Interface for ensuring the system type has been provided"""

    @classmethod
    def get_name(cls):
        """A class method for the common name of the interface.

        Returns:
          str: A unique string
        """

        return "System Type Selection"

    @classmethod
    def declare_inputs(cls):
        """A class method to declare all the variables required as inputs by
        this interface.

        Returns:
          list: List of inputs identifiers

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the data descriptions. For example:

              inputs = ["My:first:variable",
                        "My:second:variable",
                       ]
        """

        input_list = ["device.system_type"]

        return input_list

    @classmethod
    def declare_outputs(cls):
        """A class method to declare all the output variables provided by
        this interface.

        Returns:
          list: List of output identifiers

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the data descriptions. For example:

              outputs = ["My:first:variable",
                         "My:third:variable",
                        ]
        """

        outputs = ["hidden.pipeline_active"]

        return outputs

    @classmethod
    def declare_optional(cls):
        """A class method to declare all the variables which should be flagged
        as optional.

        Returns:
          list: List of optional variable identifiers

        Note:
          Currently only inputs marked as optional have any logical effect.
          However, this may change in future releases hence the general
          approach.

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the declare_inputs output. For example::

              optional = ["My:first:variable",
                         ]
        """

        return None

    @classmethod
    def declare_id_map(cls):
        """Declare the mapping for variable identifiers in the data description
        to local names for use in the interface. This helps isolate changes in
        the data description or interface from effecting the other.

        Returns:
          dict: Mapping of local to data description variable identifiers

        Example:
          The returned value must be a dictionary containing all the inputs and
          outputs from the data description and a local alias string. For
          example:

              id_map = {"var1": "My:first:variable",
                        "var2": "My:second:variable",
                        "var3": "My:third:variable"
                       }

        """

        id_map = {
            "not_used": "device.system_type",
            "output": "hidden.pipeline_active",
        }

        return id_map

    def connect(self):
        """The connect method is used to execute the external program and
        populate the interface data store with values.

        Note:
          Collecting data from the interface for use in the external program
          can be accessed using self.data.my_input_variable. To put new values
          into the interface once the program has run we set
          self.data.my_output_variable = value

        """

        self.data.output = True

        return


class OptionsInterface(ProjectInterface):
    """Interface for providing database filtering option values"""

    @classmethod
    def get_name(cls):
        """A class method for the common name of the interface.

        Returns:
          str: A unique string
        """

        return "Site and System Options"

    @classmethod
    def declare_inputs(cls):
        """A class method to declare all the variables required as inputs by
        this interface.

        Returns:
          list: List of inputs identifiers

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the data descriptions. For example:

              inputs = ["My:first:variable",
                        "My:second:variable",
                       ]
        """

        input_list = [
            "device.system_type",
            "hidden.available_sites",
            "hidden.available_systems",
            "hidden.corridor_boundaries",
            "hidden.lease_boundaries",
            "hidden.site_boundaries",
            "hidden.landing_points",
        ]

        return input_list

    @classmethod
    def declare_outputs(cls):
        """A class method to declare all the output variables provided by
        this interface.

        Returns:
          list: List of output identifiers

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the data descriptions. For example:

              outputs = ["My:first:variable",
                         "My:third:variable",
                        ]
        """

        output_list = [
            "device.available_names",
            "site.available_names",
            "hidden.corridor_selected",
            "hidden.lease_selected",
        ]

        return output_list

    @classmethod
    def declare_optional(cls):
        """A class method to declare all the variables which should be flagged
        as optional.

        Returns:
          list: List of optional variable identifiers

        Note:
          Currently only inputs marked as optional have any logical effect.
          However, this may change in future releases hence the general
          approach.

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the declare_inputs output. For example::

              optional = ["My:first:variable",
                         ]
        """

        option_list = [
            "hidden.available_sites",
            "hidden.available_systems",
            "hidden.corridor_boundaries",
            "hidden.lease_boundaries",
            "hidden.site_boundaries",
            "hidden.landing_points",
        ]

        return option_list

    @classmethod
    def declare_id_map(cls):
        """Declare the mapping for variable identifiers in the data description
        to local names for use in the interface. This helps isolate changes in
        the data description or interface from effecting the other.

        Returns:
          dict: Mapping of local to data description variable identifiers

        Example:
          The returned value must be a dictionary containing all the inputs and
          outputs from the data description and a local alias string. For
          example:

              id_map = {"var1": "My:first:variable",
                        "var2": "My:second:variable",
                        "var3": "My:third:variable"
                       }

        """

        id_map = {
            "sys_type": "device.system_type",
            "all_sites": "hidden.available_sites",
            "all_systems": "hidden.available_systems",
            "corridor_boundaries": "hidden.corridor_boundaries",
            "corridor_selected": "hidden.corridor_selected",
            "lease_boundaries": "hidden.lease_boundaries",
            "site_names": "site.available_names",
            "site_boundaries": "hidden.site_boundaries",
            "landing_points": "hidden.landing_points",
            "system_names": "device.available_names",
            "lease_selected": "hidden.lease_selected",
        }

        return id_map

    def connect(self):
        """The connect method is used to execute the external program and
        populate the interface data store with values.

        Note:
          Collecting data from the interface for use in the external program
          can be accessed using self.data.my_input_variable. To put new values
          into the interface once the program has run we set
          self.data.my_output_variable = value

        """

        if self.data.all_systems is not None:
            systems_df = self.data.all_systems
            systems_type_df = systems_df[
                systems_df["device_type"].str.contains(self.data.sys_type)
            ]

            system_names = systems_type_df["description"]
            self.data.system_names = system_names.reset_index(drop=True)

        if self.data.all_sites is not None:
            self.data.site_names = self.data.all_sites["site_name"]
            self.data.corridor_selected = False
            self.data.lease_selected = False

        return


class SiteBoundaryInterface(ProjectInterface):
    """Interface for populating cable corridor & lease area polygons and
    the projection string
    """

    @classmethod
    def get_name(cls):
        """A class method for the common name of the interface.

        Returns:
          str: A unique string
        """

        return "Site Boundary Selection"

    @classmethod
    def declare_inputs(cls):
        """A class method to declare all the variables required as inputs by
        this interface.

        Returns:
          list: List of inputs identifiers

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the data descriptions. For example:

              inputs = ["My:first:variable",
                        "My:second:variable",
                       ]
        """

        input_list = [
            "hidden.available_sites",
            "hidden.corridor_boundaries",
            "hidden.lease_boundaries",
            "hidden.landing_points",
            "site.selected_name",
            "hidden.site_boundaries",
        ]

        return input_list

    @classmethod
    def declare_outputs(cls):
        """A class method to declare all the output variables provided by
        this interface.

        Returns:
          list: List of output identifiers

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the data descriptions. For example:

              outputs = ["My:first:variable",
                         "My:third:variable",
                        ]
        """

        output_list = [
            "site.corridor_boundary",
            "site.lease_boundary",
            "site.projection",
            "hidden.site_boundary",
            "corridor.landing_point",
            "hidden.corridor_selected",
            "hidden.lease_selected",
        ]

        return output_list

    @classmethod
    def declare_optional(cls):
        """A class method to declare all the variables which should be flagged
        as optional.

        Returns:
          list: List of optional variable identifiers

        Note:
          Currently only inputs marked as optional have any logical effect.
          However, this may change in future releases hence the general
          approach.

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the declare_inputs output. For example::

              optional = ["My:first:variable",
                         ]
        """

        option_list = None

        return option_list

    @classmethod
    def declare_id_map(cls):
        """Declare the mapping for variable identifiers in the data description
        to local names for use in the interface. This helps isolate changes in
        the data description or interface from effecting the other.

        Returns:
          dict: Mapping of local to data description variable identifiers

        Example:
          The returned value must be a dictionary containing all the inputs and
          outputs from the data description and a local alias string. For
          example:

              id_map = {"var1": "My:first:variable",
                        "var2": "My:second:variable",
                        "var3": "My:third:variable"
                       }

        """

        id_map = {
            "all_sites": "hidden.available_sites",
            "corridor_poly": "site.corridor_boundary",
            "corridor_boundaries": "hidden.corridor_boundaries",
            "corridor_selected": "hidden.corridor_selected",
            "landing_points": "hidden.landing_points",
            "landing_point": "corridor.landing_point",
            "lease_boundaries": "hidden.lease_boundaries",
            "lease_poly": "site.lease_boundary",
            "proj_string": "site.projection",
            "selected_site": "site.selected_name",
            "lease_selected": "hidden.lease_selected",
            "site_boundaries": "hidden.site_boundaries",
            "site_poly": "hidden.site_boundary",
        }

        return id_map

    def connect(self):
        """The connect method is used to execute the external program and
        populate the interface data store with values.

        Note:
          Collecting data from the interface for use in the external program
          can be accessed using self.data.my_input_variable. To put new values
          into the interface once the program has run we set
          self.data.my_output_variable = value

        """

        sites_df = self.data.all_sites
        site_matches = sites_df["site_name"] == self.data.selected_site

        if np.sum(site_matches) == 0:
            names_str = ", ".join(sites_df["site_name"])
            errStr = (
                "No site with name '{}' found. Available names " "are {}"
            ).format(self.data.selected_site, names_str)
            raise ValueError(errStr)

        if np.sum(site_matches) > 1:
            errStr = (
                "More than one site with name '{}' found. Database "
                "is corrupt."
            ).format(self.data.selected_site)
            raise ValueError(errStr)

        site_corridor = self.data.corridor_boundaries[self.data.selected_site]
        site_lease = self.data.lease_boundaries[self.data.selected_site]
        site_boundary = self.data.site_boundaries[self.data.selected_site]
        landing_point = self.data.landing_points[self.data.selected_site]
        proj_strings = sites_df[site_matches]["lease_area_proj4_string"]

        self.data.corridor_poly = site_corridor
        self.data.lease_poly = site_lease
        self.data.site_poly = site_boundary
        self.data.landing_point = landing_point

        self.data.corridor_selected = True
        self.data.lease_selected = True

        self.data.proj_string = proj_strings.values[0]

        return


class FilterInterface(ProjectInterface, QueryInterface):
    """Interface to filter the database for a selected site and technology."""

    def __init__(self):
        ProjectInterface.__init__(self)
        QueryInterface.__init__(self)

        return

    @classmethod
    def get_name(cls):
        """A class method for the common name of the interface.

        Returns:
          str: A unique string
        """

        return "Database Filtering Interface"

    @classmethod
    def declare_inputs(cls):
        """A class method to declare all the variables required as inputs by
        this interface.

        Returns:
          list: List of inputs identifiers

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the data descriptions. For example:

              inputs = ["My:first:variable",
                        "My:second:variable",
                       ]
        """

        input_list = [
            "hidden.available_sites",
            "hidden.available_systems",
            "hidden.corridor_selected",
            "hidden.lease_selected",
            MaskVariable("site.selected_name", "hidden.available_sites"),
            MaskVariable("device.selected_name", "hidden.available_systems"),
        ]

        return input_list

    @classmethod
    def declare_outputs(cls):
        """A class method to declare all the output variables provided by
        this interface.

        Returns:
          list: List of output identifiers

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the data descriptions. For example:

              outputs = ["My:first:variable",
                         "My:third:variable",
                        ]
        """

        outputs = ["hidden.site_filtered", "hidden.device_filtered"]

        return outputs

    @classmethod
    def declare_optional(cls):
        """A class method to declare all the variables which should be flagged
        as optional.

        Returns:
          list: List of optional variable identifiers

        Note:
          Currently only inputs marked as optional have any logical effect.
          However, this may change in future releases hence the general
          approach.

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the declare_inputs output. For example:

              optional = ["My:first:variable",
                         ]
        """

        option_list = [
            "hidden.available_sites",
            "hidden.available_systems",
            "hidden.corridor_selected",
            "hidden.lease_selected",
            "site.selected_name",
            "device.selected_name",
        ]

        return option_list

    @classmethod
    def declare_id_map(cls):
        """Declare the mapping for variable identifiers in the data description
        to local names for use in the interface. This helps isolate changes in
        the data description or interface from effecting the other.

        Returns:
          dict: Mapping of local to data description variable identifiers

        Example:
          The returned value must be a dictionary containing all the inputs and
          outputs from the data description and a local alias string. For
          example:

              id_map = {"var1": "My:first:variable",
                        "var2": "My:second:variable",
                        "var3": "My:third:variable"
                       }

        """

        id_map = {
            "all_sites": "hidden.available_sites",
            "all_systems": "hidden.available_systems",
            "corridor_selected": "hidden.corridor_selected",
            "device_filtered": "hidden.device_filtered",
            "selected_site": "site.selected_name",
            "selected_system": "device.selected_name",
            "site_filtered": "hidden.site_filtered",
            "lease_selected": "hidden.lease_selected",
        }

        return id_map

    def connect(self):
        """The connect method is used to execute the external program and
        populate the interface data store with values.

        Note:
          Collecting data from the interface for use in the external program
          can be accessed using self.data.my_input_variable. To put new values
          into the interface once the program has run we set
          self.data.my_output_variable = value

        """

        # The main task is to prepare the database for providing project
        # data. This is done using stored proceedure calls. Firstly, get the
        # ID given the name

        if self.data.selected_system is not None:
            systems_df = self.data.all_systems
            system_matches = (
                systems_df["description"] == self.data.selected_system
            )
            system_ids = systems_df[system_matches]["id"]

            if len(system_ids) == 0:
                names_str = ", ".join(systems_df["description"])
                errStr = (
                    "No system with name '{}' found. Available names " "are {}"
                ).format(self.data.selected_system, names_str)
                raise ValueError(errStr)

            if len(system_ids) > 1:
                errStr = (
                    "More than one system with name '{}' found. "
                    "Database is corrupt."
                ).format(self.data.selected_system)
                raise ValueError(errStr)

            self._db.call_stored_proceedure(
                "filter.sp_filter_device_data", [system_ids.values[0].item()]
            )

            self.data.device_filtered = True

        if self.data.selected_site is not None:
            sites_df = self.data.all_sites
            site_matches = sites_df["site_name"] == self.data.selected_site
            site_ids = sites_df[site_matches]["id"]

            if len(site_ids) == 0:
                names_str = ", ".join(sites_df["site_name"])
                errStr = (
                    "No site with name '{}' found. Available names " "are {}"
                ).format(self.data.selected_system, names_str)
                raise ValueError(errStr)

            if len(site_ids) > 1:
                errStr = (
                    "More than one site with name '{}' found. Database "
                    "is corrupt."
                ).format(self.data.selected_site)
                raise ValueError(errStr)

            self._db.call_stored_proceedure(
                "filter.sp_filter_site_data", [site_ids.values[0].item()]
            )

            self.data.site_filtered = True

        return


class BoundariesInterface(ProjectInterface):
    """Interface to expose the area defining polygons."""

    @classmethod
    def get_name(cls):
        """A class method for the common name of the interface.

        Returns:
          str: A unique string
        """

        return "Project Boundaries Interface"

    @classmethod
    def declare_inputs(cls):
        """A class method to declare all the variables required as inputs by
        this interface.

        Returns:
          list: List of inputs identifiers

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the data descriptions. For example:

              inputs = ["My:first:variable",
                        "My:second:variable",
                       ]
        """

        input_list = [
            "site.projection",
            "site.lease_boundary",
            "site.corridor_boundary",
            "corridor.landing_point",
        ]

        return input_list

    @classmethod
    def declare_outputs(cls):
        """A class method to declare all the output variables provided by
        this interface.

        Returns:
          list: List of output identifiers

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the data descriptions. For example:

              outputs = ["My:first:variable",
                         "My:third:variable",
                        ]
        """

        outputs = None

        return outputs

    @classmethod
    def declare_optional(cls):
        """A class method to declare all the variables which should be flagged
        as optional.

        Returns:
          list: List of optional variable identifiers

        Note:
          Currently only inputs marked as optional have any logical effect.
          However, this may change in future releases hence the general
          approach.

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the declare_inputs output. For example:

              optional = ["My:first:variable",
                         ]
        """

        option_list = [
            "site.corridor_boundary",
            "site.lease_boundary",
            "corridor.landing_point",
        ]

        return option_list

    @classmethod
    def declare_id_map(cls):
        """Declare the mapping for variable identifiers in the data description
        to local names for use in the interface. This helps isolate changes in
        the data description or interface from effecting the other.

        Returns:
          dict: Mapping of local to data description variable identifiers

        Example:
          The returned value must be a dictionary containing all the inputs and
          outputs from the data description and a local alias string. For
          example:

              id_map = {"var1": "My:first:variable",
                        "var2": "My:second:variable",
                        "var3": "My:third:variable"
                       }

        """

        id_map = {
            "projection": "site.projection",
            "corridor_poly": "site.corridor_boundary",
            "lease_poly": "site.lease_boundary",
            "landing_point": "corridor.landing_point",
        }

        return id_map

    def connect(self):
        """The connect method is used to execute the external program and
        populate the interface data store with values.

        Note:
          Collecting data from the interface for use in the external program
          can be accessed using self.data.my_input_variable. To put new values
          into the interface once the program has run we set
          self.data.my_output_variable = value

        """

        return
