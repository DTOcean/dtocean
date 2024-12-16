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

"""
This module contains the package interface to the dtocean reliability
module.

Note:
  The function decorators (such as "@classmethod", etc) must not be removed.

.. module:: reliability
   :platform: Windows
   :synopsis: mdo_engine interface for dtocean_core package

.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import logging
import os
import pickle

import pandas as pd
import pkg_resources
from dtocean_reliability import Network, SubNetwork
from polite_config.configuration import ReadINI
from polite_config.paths import Directory, ModPath, UserDataPath

from ..utils.maintenance import get_user_compdict, get_user_network
from ..utils.reliability import get_component_dict
from ..utils.version import Version
from . import ThemeInterface

# Check module version
pkg_title = "dtocean-reliability"
major_version = 3
version = pkg_resources.get_distribution(pkg_title).version

if not Version(version).major == major_version:
    err_msg = (
        "Incompatible version of {} detected! Major version {} is "
        "required, but version {} is installed"
    ).format(pkg_title, major_version, version)
    raise ImportError(err_msg)

# Set up logging
module_logger = logging.getLogger(__name__)


class ReliabilityInterface(ThemeInterface):
    """Interface to the reliability theme."""

    def __init__(self):
        super(ReliabilityInterface, self).__init__()

    @classmethod
    def get_name(cls):
        """A class method for the common name of the interface.

        Returns:
          str: A unique string
        """

        return "Reliability"

    @classmethod
    def declare_weight(cls):
        return 2

    @classmethod
    def declare_inputs(cls):
        """A class method to declare all the variables required as inputs by
        this interface.

        Returns:
          list: List of inputs identifiers

        Example:
          The returned value can be None or a list of identifier strings which
          appear in the data descriptions. For example::

              inputs = ["My:first:variable",
                        "My:second:variable",
                       ]
        """

        input_list = [
            "device.subsystem_failure_rates",
            "device.control_subsystem_failure_rates",
            "project.layout",
            "project.electrical_network",
            "project.electrical_component_data",
            "project.moorings_foundations_network",
            "project.reliability_time",
            "project.reliability_confidence",
            "project.apply_kfactors",
            "component.static_cable_NCFR",
            "component.static_cable_perkm_NCFR",
            "component.dynamic_cable_NCFR",
            "component.dry_mate_connectors_NCFR",
            "component.wet_mate_connectors_NCFR",
            "component.collection_points_NCFR",
            "component.transformers_NCFR",
            "component.static_cable_CFR",
            "component.static_cable_perkm_CFR",
            "component.dynamic_cable_CFR",
            "component.dry_mate_connectors_CFR",
            "component.wet_mate_connectors_CFR",
            "component.collection_points_CFR",
            "component.transformers_CFR",
            "component.foundations_anchor_NCFR",
            "component.foundations_pile_NCFR",
            "component.moorings_chain_NCFR",
            "component.moorings_forerunner_NCFR",
            "component.moorings_rope_NCFR",
            "component.moorings_shackle_NCFR",
            "component.moorings_swivel_NCFR",
            "component.foundations_anchor_CFR",
            "component.foundations_pile_CFR",
            "component.moorings_chain_CFR",
            "component.moorings_forerunner_CFR",
            "component.moorings_rope_CFR",
            "component.moorings_shackle_CFR",
            "component.moorings_swivel_CFR",
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
          appear in the data descriptions. For example::

              outputs = ["My:first:variable",
                         "My:third:variable",
                        ]
        """

        output_list = [
            "project.system_reliability_CFR",
            "project.export_reliability_CFR",
            "project.substation_reliability_CFR",
            "project.electrical_reliability_CFR",
            "project.mandf_reliability_CFR",
            "project.foundations_reliability_CFR",
            "project.moorings_reliability_CFR",
            "project.umbilical_reliability_CFR",
            "project.device_reliability_CFR",
            "project.system_reliability_NCFR",
            "project.export_reliability_NCFR",
            "project.substation_reliability_NCFR",
            "project.electrical_reliability_NCFR",
            "project.system_reliability_NCFR",
            "project.mandf_reliability_NCFR",
            "project.foundations_reliability_NCFR",
            "project.moorings_reliability_NCFR",
            "project.umbilical_reliability_NCFR",
            "project.device_reliability_NCFR",
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
        optional = [
            "device.subsystem_failure_rates",
            "device.control_subsystem_failure_rates",
            "project.layout",
            "project.electrical_network",
            "project.electrical_component_data",
            "project.moorings_foundations_network",
            "project.reliability_time",
            "project.reliability_confidence",
            "project.apply_kfactors",
            "component.collection_points_NCFR",
            "component.dry_mate_connectors_NCFR",
            "component.dynamic_cable_NCFR",
            "component.static_cable_NCFR",
            "component.static_cable_perkm_NCFR",
            "component.transformers_NCFR",
            "component.wet_mate_connectors_NCFR",
            "component.collection_points_CFR",
            "component.dry_mate_connectors_CFR",
            "component.dynamic_cable_CFR",
            "component.static_cable_CFR",
            "component.static_cable_perkm_CFR",
            "component.transformers_CFR",
            "component.wet_mate_connectors_CFR",
            "component.moorings_chain_NCFR",
            "component.foundations_anchor_NCFR",
            "component.moorings_forerunner_NCFR",
            "component.foundations_pile_NCFR",
            "component.moorings_rope_NCFR",
            "component.moorings_shackle_NCFR",
            "component.moorings_swivel_NCFR",
            "component.moorings_chain_CFR",
            "component.foundations_anchor_CFR",
            "component.moorings_forerunner_CFR",
            "component.foundations_pile_CFR",
            "component.moorings_rope_CFR",
            "component.moorings_shackle_CFR",
            "component.moorings_swivel_CFR",
        ]

        return optional

    @classmethod
    def declare_id_map(self):
        """Declare the mapping for variable identifiers in the data description
        to local names for use in the interface. This helps isolate changes in
        the data description or interface from effecting the other.

        Returns:
          dict: Mapping of local to data description variable identifiers

        Example:
          The returned value must be a dictionary containing all the inputs and
          outputs from the data description and a local alias string. For
          example::

              id_map = {"var1": "My:first:variable",
                        "var2": "My:second:variable",
                        "var3": "My:third:variable"
                       }

        """

        id_map = {
            "array_layout": "project.layout",
            "subsystem_failure_rates": "device.subsystem_failure_rates",
            "control_subsystem_failure_rates": "device.control_subsystem_failure_rates",
            "moor_found_network": "project.moorings_foundations_network",
            "electrical_network": "project.electrical_network",
            "electrical_components": "project.electrical_component_data",
            "reliability_time": "project.reliability_time",
            "reliability_confidence": "project.reliability_confidence",
            "apply_kfactors": "project.apply_kfactors",
            "collection_points_NCFR": "component.collection_points_NCFR",
            "dry_mate_connectors_NCFR": "component.dry_mate_connectors_NCFR",
            "dynamic_cable_NCFR": "component.dynamic_cable_NCFR",
            "static_cable_NCFR": "component.static_cable_NCFR",
            "static_cable_perkm_NCFR": "component.static_cable_perkm_NCFR",
            "transformers_NCFR": "component.transformers_NCFR",
            "wet_mate_connectors_NCFR": "component.wet_mate_connectors_NCFR",
            "collection_points_CFR": "component.collection_points_CFR",
            "dry_mate_connectors_CFR": "component.dry_mate_connectors_CFR",
            "dynamic_cable_CFR": "component.dynamic_cable_CFR",
            "static_cable_CFR": "component.static_cable_CFR",
            "static_cable_perkm_CFR": "component.static_cable_perkm_CFR",
            "transformers_CFR": "component.transformers_CFR",
            "wet_mate_connectors_CFR": "component.wet_mate_connectors_CFR",
            "moorings_chain_NCFR": "component.moorings_chain_NCFR",
            "foundations_anchor_NCFR": "component.foundations_anchor_NCFR",
            "moorings_forerunner_NCFR": "component.moorings_forerunner_NCFR",
            "foundations_pile_NCFR": "component.foundations_pile_NCFR",
            "moorings_rope_NCFR": "component.moorings_rope_NCFR",
            "moorings_shackle_NCFR": "component.moorings_shackle_NCFR",
            "moorings_swivel_NCFR": "component.moorings_swivel_NCFR",
            "moorings_chain_CFR": "component.moorings_chain_CFR",
            "foundations_anchor_CFR": "component.foundations_anchor_CFR",
            "moorings_forerunner_CFR": "component.moorings_forerunner_CFR",
            "foundations_pile_CFR": "component.foundations_pile_CFR",
            "moorings_rope_CFR": "component.moorings_rope_CFR",
            "moorings_shackle_CFR": "component.moorings_shackle_CFR",
            "moorings_swivel_CFR": "component.moorings_swivel_CFR",
            "system_reliability_CFR": "project.system_reliability_CFR",
            "export_reliability_CFR": "project.export_reliability_CFR",
            "substation_reliability_CFR": "project.substation_reliability_CFR",
            "electrical_reliability_CFR": "project.electrical_reliability_CFR",
            "mandf_reliability_CFR": "project.mandf_reliability_CFR",
            "foundations_reliability_CFR": "project.foundations_reliability_CFR",
            "moorings_reliability_CFR": "project.moorings_reliability_CFR",
            "umbilical_reliability_CFR": "project.umbilical_reliability_CFR",
            "device_reliability_CFR": "project.device_reliability_CFR",
            "system_reliability_NCFR": "project.system_reliability_NCFR",
            "export_reliability_NCFR": "project.export_reliability_NCFR",
            "substation_reliability_NCFR": "project.substation_reliability_NCFR",
            "electrical_reliability_NCFR": "project.electrical_reliability_NCFR",
            "mandf_reliability_NCFR": "project.mandf_reliability_NCFR",
            "foundations_reliability_NCFR": "project.foundations_reliability_NCFR",
            "moorings_reliability_NCFR": "project.moorings_reliability_NCFR",
            "umbilical_reliability_NCFR": "project.umbilical_reliability_NCFR",
            "device_reliability_NCFR": "project.device_reliability_NCFR",
        }

        return id_map

    def connect(self, debug_entry=False, export_data=True):
        """The connect method is used to execute the external program and
        populate the interface data store with values.

        Note:
          Collecting data from the interface for use in the external program
          can be accessed using self.data.my_input_variable. To put new values
          into the interface once the program has run we set
          self.data.my_output_variable = value

        """

        input_dict = self.get_input_dict(self.data)

        if input_dict is None:
            return

        if self.data.reliability_time is None:
            reliability_time = 8766
        else:
            reliability_time = self.data.reliability_time

        confidence_map = {
            "Pessimistic": "lower",
            "Normal": "mean",
            "Optimistic": "upper",
        }

        if self.data.reliability_confidence is None:
            confidence_level = "mean"
        else:
            confidence_level = confidence_map[self.data.reliability_confidence]

        input_dict["reliability_time"] = reliability_time
        input_dict["confidence_level"] = confidence_level

        if export_data:
            userdir = UserDataPath("dtocean_core", "DTOcean", "config")

            if userdir.isfile("files.ini"):
                configdir = userdir
            else:
                configdir = ModPath("dtocean_core", "config")

            files_ini = ReadINI(configdir, "files.ini")
            files_config = files_ini.get_config()

            appdir_path = userdir.get_path("..")
            debug_folder = files_config["debug"]["path"]
            debug_path = os.path.join(appdir_path, debug_folder)
            debugdir = Directory(debug_path)
            debugdir.makedir()

            pkl_path = debugdir.get_path("reliability_inputs.pkl")
            pickle.dump(input_dict, open(pkl_path, "wb"), -1)

        electrical_network = None
        moorings_network = None
        user_network = None

        if input_dict["electrical_network_hier"] is not None:
            electrical_network = SubNetwork(
                input_dict["electrical_network_hier"],
                input_dict["electrical_network_bom"],
            )

        if input_dict["moor_found_network_hier"] is not None:
            moorings_network = SubNetwork(
                input_dict["moor_found_network_hier"],
                input_dict["moor_found_network_bom"],
            )

        if input_dict["user_hier"] is not None:
            user_network = SubNetwork(
                input_dict["user_hier"], input_dict["user_bom"]
            )

        # Build electrical data input

        network = Network(
            input_dict["compdict"],
            electrical_network,
            moorings_network,
            user_network,
        )

        if debug_entry:
            return

        year_hours = 24.0 * 365.25
        reliability_key = "R ({} hours)".format(reliability_time)
        metrics_map = {
            "System": "System ID",
            "lambda": "Failure Rate",
            "MTTF": "MTTF",
            "RPN": "RPN",
            reliability_key: "Reliability (at time $T$)",
        }

        severities = ["critical", "noncritical"]
        var_appends = ["_CFR", "_NCFR"]

        subsystems = [
            "Export cable",
            "Substation",
            "Elec sub-system",
            "M&F sub-system",
            "Moorings lines",
            "Foundation",
            "Umbilical",
            "User sub-systems",
        ]

        out_vars = [
            "export_reliability",
            "substation_reliability",
            "electrical_reliability",
            "mandf_reliability",
            "foundations_reliability",
            "moorings_reliability",
            "umbilical_reliability",
            "device_reliability",
        ]

        for severity, var_append in zip(severities, var_appends):
            severity_network = network.set_failure_rates(
                severity, confidence_level, input_dict["k_factors"]
            )
            systems_metrics = severity_network.get_systems_metrics(
                reliability_time
            )

            systems_df = self.get_system_dataframe(
                systems_metrics, ["Link"], metrics_map, year_hours
            )

            var = "system_reliability" + var_append
            self.data[var] = systems_df

            for system, var in zip(subsystems, out_vars):
                sub_metrics = severity_network.get_subsystem_metrics(
                    system, reliability_time
                )

                if sub_metrics is None:
                    continue

                systems_df = self.get_system_dataframe(
                    sub_metrics, ["Link", "Curtails"], metrics_map, year_hours
                )

                var += var_append
                self.data[var] = systems_df

        return

    @classmethod
    def get_input_dict(cls, data):
        if (
            data.moor_found_network is None
            and data.electrical_network is None
            and data.subsystem_failure_rates
        ):
            return None

        if data.moor_found_network is None:
            moor_found_network_hier = None
            moor_found_network_bom = None
        else:
            moor_found_network_hier = data.moor_found_network["topology"]
            moor_found_network_bom = data.moor_found_network["nodes"]

        if data.electrical_network is None:
            electrical_network_hier = None
            electrical_network_bom = None
        else:
            electrical_network_hier = data.electrical_network["topology"]
            electrical_network_bom = data.electrical_network["nodes"]

        # k-factor default
        k_factors = {}

        if data.apply_kfactors is None:
            data.apply_kfactors = False

        # Component Check
        if data.electrical_network is not None:
            # k-factor substitution
            if data.apply_kfactors:
                data.static_cable_NCFR = data.static_cable_perkm_NCFR
                data.static_cable_CFR = data.static_cable_perkm_CFR

            if (
                data.collection_points_NCFR is None
                or data.collection_points_CFR is None
                or data.dry_mate_connectors_NCFR is None
                or data.dry_mate_connectors_CFR is None
                or data.dynamic_cable_NCFR is None
                or data.dynamic_cable_CFR is None
                or data.static_cable_NCFR is None
                or data.static_cable_CFR is None
                or data.transformers_NCFR is None
                or data.transformers_CFR is None
                or data.wet_mate_connectors_NCFR is None
                or data.wet_mate_connectors_CFR is None
            ):
                msg = (
                    "Insufficient component reliability data entered to "
                    "undertake analysis for electrical network"
                )
                module_logger.info(msg)

                return None

            # k-factor electrical data
            if data.apply_kfactors:
                if data.electrical_components is None:
                    err_str = (
                        "Electrical network component data must be "
                        "provided if using k-factors"
                    )
                    raise ValueError(err_str)

                valid_types = ["array", "export"]
                m2km = lambda x: x / 1e3

                for _, row in data.electrical_components.iterrows():
                    if row["Installation Type"] not in valid_types:
                        continue

                    key = row["Marker"]
                    value = m2km(row["Quantity"])
                    k_factors[key] = value

        if data.moor_found_network is None:
            if (
                data.moorings_chain_NCFR is None
                or data.moorings_chain_CFR is None
                or data.foundations_anchor_NCFR is None
                or data.foundations_anchor_CFR is None
                or data.moorings_forerunner_NCFR is None
                or data.moorings_forerunner_CFR is None
                or data.foundations_pile_NCFR is None
                or data.foundations_pile_CFR is None
                or data.moorings_rope_NCFR is None
                or data.moorings_rope_CFR is None
                or data.moorings_shackle_NCFR is None
                or data.moorings_shackle_CFR is None
                or data.moorings_swivel_NCFR is None
                or data.moorings_swivel_CFR is None
            ):
                msg = (
                    "Insufficient component reliability data entered to "
                    "undertake analysis for moorings and foundations "
                    "network"
                )
                module_logger.info(msg)

                return None

        ## COMPONENTS
        compdict = {}

        if (
            data.collection_points_NCFR is None
            or data.collection_points_CFR is None
        ):
            pass

        else:
            collection_points_dict = get_component_dict(
                "collection point",
                data.collection_points_CFR,
                data.collection_points_NCFR,
                check_keys=compdict.keys(),
            )
            compdict.update(collection_points_dict)

        if (
            data.dry_mate_connectors_NCFR is None
            or data.dry_mate_connectors_CFR is None
        ):
            pass

        else:
            dry_mate_connectors_dict = get_component_dict(
                "dry mate",
                data.dry_mate_connectors_CFR,
                data.dry_mate_connectors_NCFR,
                check_keys=compdict.keys(),
            )
            compdict.update(dry_mate_connectors_dict)

        if data.dynamic_cable_NCFR is None or data.dynamic_cable_CFR is None:
            pass

        else:
            dynamic_cable_dict = get_component_dict(
                "dynamic cable",
                data.dynamic_cable_CFR,
                data.dynamic_cable_NCFR,
                check_keys=compdict.keys(),
            )
            compdict.update(dynamic_cable_dict)

        if data.static_cable_NCFR is None or data.static_cable_CFR is None:
            pass

        else:
            static_cable_dict = get_component_dict(
                "static cable",
                data.static_cable_CFR,
                data.static_cable_NCFR,
                check_keys=compdict.keys(),
            )
            compdict.update(static_cable_dict)

        if data.transformers_NCFR is None or data.transformers_CFR is None:
            pass

        else:
            transformers_dict = get_component_dict(
                "transformer",
                data.transformers_CFR,
                data.transformers_NCFR,
                check_keys=compdict.keys(),
            )
            compdict.update(transformers_dict)

        if (
            data.wet_mate_connectors_NCFR is None
            or data.wet_mate_connectors_CFR is None
        ):
            pass

        else:
            wet_mate_connectors_dict = get_component_dict(
                "wet mate",
                data.wet_mate_connectors_CFR,
                data.wet_mate_connectors_NCFR,
                check_keys=compdict.keys(),
            )
            compdict.update(wet_mate_connectors_dict)

        if data.moorings_chain_NCFR is None or data.moorings_chain_CFR is None:
            pass

        else:
            moorings_chain_dict = get_component_dict(
                "chain",
                data.moorings_chain_CFR,
                data.moorings_chain_NCFR,
                check_keys=compdict.keys(),
            )
            compdict.update(moorings_chain_dict)

        if (
            data.foundations_anchor_NCFR is None
            or data.foundations_anchor_CFR is None
        ):
            pass

        else:
            foundations_anchor_dict = get_component_dict(
                "anchor",
                data.foundations_anchor_CFR,
                data.foundations_anchor_NCFR,
                check_keys=compdict.keys(),
            )
            compdict.update(foundations_anchor_dict)

        if (
            data.moorings_forerunner_NCFR is None
            or data.moorings_forerunner_CFR is None
        ):
            pass

        else:
            moorings_forerunner_dict = get_component_dict(
                "forerunner",
                data.moorings_forerunner_CFR,
                data.moorings_forerunner_NCFR,
                check_keys=compdict.keys(),
            )
            compdict.update(moorings_forerunner_dict)

        if (
            data.foundations_pile_NCFR is None
            or data.foundations_pile_CFR is None
        ):
            pass

        else:
            foundations_pile_dict = get_component_dict(
                "pile",
                data.foundations_pile_CFR,
                data.foundations_pile_NCFR,
                check_keys=compdict.keys(),
            )
            compdict.update(foundations_pile_dict)

        if data.moorings_rope_NCFR is None or data.moorings_rope_CFR is None:
            pass

        else:
            moorings_rope_dict = get_component_dict(
                "rope",
                data.moorings_rope_CFR,
                data.moorings_rope_NCFR,
                check_keys=compdict.keys(),
            )
            compdict.update(moorings_rope_dict)

        if (
            data.moorings_shackle_NCFR is None
            or data.moorings_shackle_CFR is None
        ):
            pass

        else:
            moorings_shackle_dict = get_component_dict(
                "shackle",
                data.moorings_shackle_CFR,
                data.moorings_shackle_NCFR,
                check_keys=compdict.keys(),
            )
            compdict.update(moorings_shackle_dict)

        if (
            data.moorings_swivel_NCFR is None
            or data.moorings_swivel_CFR is None
        ):
            pass

        else:
            moorings_swivel_dict = get_component_dict(
                "swivel",
                data.moorings_swivel_CFR,
                data.moorings_swivel_NCFR,
                check_keys=compdict.keys(),
            )
            compdict.update(moorings_swivel_dict)

        if data.array_layout is None or data.subsystem_failure_rates is None:
            user_hier = None
            user_bom = None

        else:
            # Manufacture the user network for the device subsytems:
            subsytem_comps = ["hydro001", "pto001", "support001"]

            subsystem_rates = data.subsystem_failure_rates

            if data.control_subsystem_failure_rates is not None:
                subsytem_comps.insert(2, "control001")
                subsystem_rates.update(data.control_subsystem_failure_rates)

            user_hier, user_bom = get_user_network(
                subsytem_comps, data.array_layout
            )

            user_compdict = get_user_compdict(subsytem_comps, subsystem_rates)
            compdict.update(user_compdict)

        result = {
            "compdict": compdict,
            "electrical_network_hier": electrical_network_hier,
            "electrical_network_bom": electrical_network_bom,
            "moor_found_network_hier": moor_found_network_hier,
            "moor_found_network_bom": moor_found_network_bom,
            "user_hier": user_hier,
            "user_bom": user_bom,
            "k_factors": k_factors,
        }

        return result

    @classmethod
    def get_system_dataframe(cls, metrics, drop_cols, metrics_map, year_hours):
        systems_df = pd.DataFrame(metrics)

        for col in drop_cols:
            systems_df = systems_df.drop(col, axis=1)

        systems_df = systems_df.rename(columns=metrics_map)
        systems_df = systems_df.sort_values(by=["System ID"])

        systems_df["Failure Rate"] = systems_df["Failure Rate"].apply(
            lambda x: x * 1e6
        )
        systems_df["MTTF"] = systems_df["MTTF"].apply(lambda x: x / year_hours)

        return systems_df
