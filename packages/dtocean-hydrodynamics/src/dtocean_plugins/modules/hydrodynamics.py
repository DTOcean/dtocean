#    Copyright (C) 2016-2025 Mathew Topper
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
This module contains the package interface to the dtocean hydrodynamics
module.

Note:
  The function decorators (such as "@classmethod", etc) must not be removed.

.. module:: hydrodynamics
   :platform: Windows
   :synopsis: mdo-engine interface for dtocean_core package

.. moduleauthor:: Mathew Topper <damm_horse@yahoo.co.uk>
"""

import pickle
from pathlib import Path
from typing import Any

import numpy as np
from mdo_engine.boundary.interface import MaskVariable
from natsort import natsorted
from polite_config.paths import UserDataPath

from dtocean_hydro.input import WP2_MachineData, WP2_SiteData, WP2input
from dtocean_hydro.main import WP2
from dtocean_hydro.utils.convert import (
    bearing_to_vector,
    check_bin_widths,
    make_power_histograms,
    make_tide_statistics,
    make_wave_statistics,
    radians_to_bearing,
    vector_to_bearing,
)
from dtocean_plugins.modules.modules import ModuleInterface


class HydroInterface(ModuleInterface):
    """Interface to the Spreadsheet class of dtocean_demo, providing a table
    of random numbers.

      Attributes:
        id_map (dict): Mapping of internal variable names to local variable
          names.

    """

    @classmethod
    def get_name(cls):
        """A class method for the common name of the interface.

        Returns:
          str: A unique string
        """

        return "Hydrodynamics"

    @classmethod
    def declare_weight(cls):
        return 1

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
                        "My: second:variable",
                       ]
        """

        input_list = [
            "site.lease_boundary",
            "bathymetry.layers",
            "corridor.landing_point",
            "farm.nogo_areas",
            MaskVariable(
                "farm.blockage_ratio",
                "device.system_type",
                ["Tidal Fixed", "Tidal Floating"],
            ),
            MaskVariable(
                "farm.spectrum_name",
                "device.system_type",
                ["Wave Fixed", "Wave Floating"],
            ),
            MaskVariable(
                "farm.spec_gamma",
                "device.system_type",
                ["Wave Fixed", "Wave Floating"],
            ),
            MaskVariable(
                "farm.spec_spread",
                "device.system_type",
                ["Wave Fixed", "Wave Floating"],
            ),
            MaskVariable(
                "farm.tidal_occurrence",
                "device.system_type",
                ["Tidal Fixed", "Tidal Floating"],
            ),
            MaskVariable(
                "farm.tidal_series",
                "device.system_type",
                ["Tidal Fixed", "Tidal Floating"],
            ),
            MaskVariable(
                "farm.tidal_occurrence_point",
                "device.system_type",
                ["Tidal Fixed", "Tidal Floating"],
            ),
            MaskVariable(
                "project.tidal_occurrence_nbins",
                "device.system_type",
                ["Tidal Fixed", "Tidal Floating"],
            ),
            MaskVariable(
                "farm.wave_series",
                "device.system_type",
                ["Wave Fixed", "Wave Floating"],
            ),
            "device.system_type",
            "device.power_rating",
            "device.installation_depth_max",
            "device.installation_depth_min",
            "device.minimum_distance_x",
            "device.minimum_distance_y",
            "device.yaw",
            MaskVariable(
                "device.bidirection",
                "device.system_type",
                ["Tidal Fixed", "Tidal Floating"],
            ),
            MaskVariable(
                "device.cut_in_velocity",
                "device.system_type",
                ["Tidal Fixed", "Tidal Floating"],
            ),
            MaskVariable(
                "device.cut_out_velocity",
                "device.system_type",
                ["Tidal Fixed", "Tidal Floating"],
            ),
            MaskVariable(
                "device.turbine_hub_height",
                "device.system_type",
                ["Tidal Fixed", "Tidal Floating"],
            ),
            MaskVariable(
                "device.turbine_diameter",
                "device.system_type",
                ["Tidal Fixed", "Tidal Floating"],
            ),
            MaskVariable(
                "device.turbine_interdistance",
                "device.system_type",
                ["Tidal Fixed", "Tidal Floating"],
            ),
            MaskVariable(
                "device.turbine_performance",
                "device.system_type",
                ["Tidal Fixed", "Tidal Floating"],
            ),
            MaskVariable(
                "device.wave_data_directory",
                "device.system_type",
                ["Wave Fixed", "Wave Floating"],
            ),
            "project.rated_power",
            "project.main_direction",
            "options.boundary_padding",
            "options.optimisation_threshold",
            "options.power_bin_width",
            "options.user_array_option",
            "options.user_array_layout",
            MaskVariable(
                "options.tidal_data_directory",
                "device.system_type",
                ["Tidal Fixed", "Tidal Floating"],
            ),
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
            "project.annual_energy",
            "project.array_efficiency",
            "project.annual_energy_per_device",
            "device.external_forces",
            "project.layout",
            "project.main_direction",
            "project.mean_power_per_device",
            "project.mean_power_pmf_per_device",
            "project.mean_power_hist_per_device",
            "project.number_of_devices",
            "project.q_factor",
            "project.q_factor_per_device",
            "project.resource_reduction",
            "device.wave_power_matrix",
            "farm.tidal_occurrence",
            "farm.wave_occurrence",
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
            "farm.tidal_occurrence",
            "farm.tidal_series",
            "farm.tidal_occurrence_point",
            "project.tidal_occurrence_nbins",
            "device.turbine_interdistance",
            "project.main_direction",
            "farm.nogo_areas",
            "options.boundary_padding",
            "options.power_bin_width",
            "options.user_array_layout",
            "options.tidal_data_directory",
        ]

        return optional

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
          example::

              id_map = {"var1": "My:first:variable",
                        "var2": "My:second:variable",
                        "var3": "My:third:variable"
                       }

        """

        id_map = {
            "AEP_array": "project.annual_energy",
            "AEP_per_device": "project.annual_energy_per_device",
            "array_efficiency": "project.array_efficiency",
            "bathymetry": "bathymetry.layers",
            "bidirection": "device.bidirection",
            "blockage_ratio": "farm.blockage_ratio",
            "boundary_padding": "options.boundary_padding",
            "export_landing_point": "corridor.landing_point",
            "cut_in": "device.cut_in_velocity",
            "cut_out": "device.cut_out_velocity",
            "device_position": "project.layout",
            "ext_forces": "device.external_forces",
            "hub_height": "device.turbine_hub_height",
            "lease_area": "site.lease_boundary",
            "main_direction": "project.main_direction",
            "max_install": "device.installation_depth_max",
            "min_dist_x": "device.minimum_distance_x",
            "min_dist_y": "device.minimum_distance_y",
            "min_install": "device.installation_depth_min",
            "n_bodies": "project.number_of_devices",
            "nogo_areas": "farm.nogo_areas",
            "op_threshold": "options.optimisation_threshold",
            "perf_curves": "device.turbine_performance",
            "pow_bins": "options.power_bin_width",
            "pow_per_device": "project.mean_power_per_device",
            "pow_pmf_per_device": "project.mean_power_pmf_per_device",
            "pow_hist_per_device": "project.mean_power_hist_per_device",
            "power_matrix": "device.wave_power_matrix",
            "q_factor_array": "project.q_factor",
            "q_factor_per_device": "project.q_factor_per_device",
            "rated_array_power": "project.rated_power",
            "rated_power_device": "device.power_rating",
            "resource_reduction": "project.resource_reduction",
            "rotor_diam": "device.turbine_diameter",
            "spectrum_dir_spreading_farm": "farm.spec_spread",
            "spectrum_gamma_farm": "farm.spec_gamma",
            "spectrum_type_farm": "farm.spectrum_name",
            "tidal_data_directory": "options.tidal_data_directory",
            "tidal_nbins": "project.tidal_occurrence_nbins",
            "tidal_occurrence": "farm.tidal_occurrence",
            "tidal_occurrence_point": "farm.tidal_occurrence_point",
            "tidal_series": "farm.tidal_series",
            "turbine_interdist": "device.turbine_interdistance",
            "type": "device.system_type",
            "user_array_layout": "options.user_array_layout",
            "user_array_option": "options.user_array_option",
            "wave_data_directory": "device.wave_data_directory",
            "wave_occurrence": "farm.wave_occurrence",
            "wave_series": "farm.wave_series",
            "yaw_angle": "device.yaw",
        }

        return id_map

    def connect(self, debug_entry=False, export_data=False):
        """The connect method is used to execute the external program and
        populate the interface data store with values.

        Note:
          Collecting data from the interface for use in the external program
          can be accessed using self.data.my_input_variable. To put new values
          into the interface once the program has run we set
          self.data.my_output_variable = value

        """

        #   #------------------------------------------------------------------------------
        #   #------------------------------------------------------------------------------
        #   #------------------ WP2 site data class
        #   #------------------------------------------------------------------------------
        #   #------------------------------------------------------------------------------
        #   Sitedata class: The class contains all the information relative to the area of deployment
        # of the array.
        #
        # Args:
        # LeaseArea (numpy.ndarray) [m]: UTM coordinates of the lease area poligon expressed as [X,Y].
        # X is the column vector containing the easting coordinates
        # Y is the column vector containing the northing coordinates
        # NogoAreas (list) [m]: list containing the UTM coordinates of the nogo areas poligons expressed as [X,Y].
        # MeteoceanConditions (dict): dictionary gathering all the information related to the metocean conditions
        # of the site. The dictionary is different for wave and tidal cases:
        # Wave keys:
        # 'Te' (numpy.ndarray)[s]: Vector containing the wave energy periods
        # 'Hs' (numpy.ndarray)[m]: Vector containing the significant wave height
        # 'dir' (numpy.ndarray)[rad]: Vector containing the wave direction
        # 'p' (numpy.ndarray)[-]: Probability of occurence of the sea state
        # 'specType' (tup): description of the spectral shape recorded at the site
        # (spectrum name, gamma factor, spreading parameter)
        # 'SSH' (float)[m]: Sea Surface Height wrt the bathymetry datum at a single point
        # Tidal keys:
        # 'V' (numpy.ndarray)[m/s]: northing-direction of the velocity field
        # 'U' (numpy.ndarray)[m/s]: easting-direction of the velocity field
        # 'p' (numpy.ndarray)[-]: probability of occurency of the state
        # 'TI' (numpy.ndarray)[-]: Turbulence intensity. It can be a single float or a matrix where the
        # TI is specified at each grid node.
        # 'x' (numpy.ndarray)[m]: Vector containing the easting coordinate of the grid nodes
        # 'y' (numpy.ndarray)[m]: Vector containing the northing coordinate of the grid nodes
        # 'SSH' (numpy.ndarray)[m]: Sea Surface Height wrt the bathymetry datum
        #       Beta (float, optional if None): TIDAL ONLY bed roughness (default = 0.4)
        #       Alpha (float, optional if None): TIDAL ONLY power law exponent (default = 7.)
        # Main_Direction (numpy.ndarray, optional) [m]: xy vector defining the main orientation of the array. If not provided it will be
        # assessed from the Metocean conditions.
        # Bathymetry (numpy.ndarray) [m]: Describes the vertical profile of the sea bottom at each (given) UTM coordinate.
        # Expressed as [X,Y,Z]
        # BR (float) [-]: describes the ratio between the lease area surface over the site area surface enclosed in a channel.
        # 1. - closed channel
        # 0. - open sea
        # electrical_connection_point (numpy.ndarray) [m]: UTM coordinates of the electrical connection point at the shore line
        #        boundary_padding (float, optional) [m]: Padding added to inside of the lease area in which devices may not be placed

        # Check whether the bin width divides the RP perfectly
        check_bin_widths(self.data.rated_power_device, self.data.pow_bins)

        if "Tidal" in self.data.type:
            if self.data.tidal_occurrence is not None:
                occurrence_matrix = {
                    "x": self.data.tidal_occurrence["UTM x"].values,
                    "y": self.data.tidal_occurrence["UTM y"].values,
                    "p": self.data.tidal_occurrence["p"].values,
                    "U": self.data.tidal_occurrence["U"].values,
                    "V": self.data.tidal_occurrence["V"].values,
                    "SSH": self.data.tidal_occurrence["SSH"].values,
                    "TI": self.data.tidal_occurrence["TI"].values,
                }

                # Don't let farm.tidal_occurrence be an output
                self.data.tidal_occurrence = None

            elif self.data.tidal_series is None:
                err_msg = (
                    "Tidal time series or representative velocity "
                    "fields must be provided."
                )
                raise ValueError(err_msg)

            elif self.data.tidal_occurrence_point is None:
                err_msg = (
                    "The tidal occurance extraction point must be "
                    "specified when creating velocity fields from "
                    "the tidal time series."
                )
                raise ValueError(err_msg)

            else:
                if self.data.tidal_nbins is None:
                    tidal_nbins = len(self.data.tidal_series.t)
                else:
                    tidal_nbins = self.data.tidal_nbins

                x = self.data.tidal_series.coords["UTM x"]
                y = self.data.tidal_series.coords["UTM y"]

                tide_dict = {
                    "U": self.data.tidal_series.U.values,
                    "V": self.data.tidal_series.V.values,
                    "SSH": self.data.tidal_series.SSH.values,
                    "TI": self.data.tidal_series.TI.values,
                    "x": x.values,
                    "y": y.values,
                    "t": self.data.tidal_series.t.values,
                    "xc": self.data.tidal_occurrence_point.x,
                    "yc": self.data.tidal_occurrence_point.y,
                    "ns": tidal_nbins,
                }

                if self.data.tidal_nbins is None:
                    n_steps = len(self.data.tidal_series.t.values)
                    p = np.ones(n_steps) * (1.0 / n_steps)

                    tide_dict.pop("xc")
                    tide_dict.pop("yc")
                    tide_dict["p"] = p

                    occurrence_matrix = tide_dict

                else:
                    occurrence_matrix = make_tide_statistics(tide_dict)

                p_total = sum(occurrence_matrix["p"])

                if not np.isclose(p_total, 1.0):
                    errStr = (
                        "Tidal statistics probabilities invalid. Total "
                        "probability equals {}"
                    ).format(p_total)
                    raise ValueError(errStr)

                occurrence_matrix_coords = [
                    occurrence_matrix["x"],
                    occurrence_matrix["y"],
                    occurrence_matrix["p"],
                ]

                matrix_xset = {
                    "values": {
                        "U": occurrence_matrix["U"],
                        "V": occurrence_matrix["V"],
                        "SSH": occurrence_matrix["SSH"],
                        "TI": occurrence_matrix["TI"],
                    },
                    "coords": occurrence_matrix_coords,
                }

                self.data.tidal_occurrence = matrix_xset

        else:
            occurrence_matrix = make_wave_statistics(self.data.wave_series)

            p_total = occurrence_matrix["p"].sum()

            if not np.isclose(p_total, 1.0):
                errStr = (
                    "Wave statistics probabilities invalid. Total "
                    "probability equals {}"
                ).format(p_total)
                raise ValueError(errStr)

            occurrence_matrix_coords = [
                occurrence_matrix["Te"],
                occurrence_matrix["Hs"],
                occurrence_matrix["B"],
            ]
            matrix_xgrid = {
                "values": occurrence_matrix["p"],
                "coords": occurrence_matrix_coords,
            }

            self.data.wave_occurrence = matrix_xgrid

            # Translate spectrum type
            spectrum_map = {
                "Regular": "Regular",
                "Pierson-Moskowitz": "Pierson_Moskowitz",
                "JONSWAP": "Jonswap",
                "Bretschneider": "Bretschneider_Mitsuyasu",
                "Modified Bretschneider": "Modified_Bretschneider_Mitsuyasu",
            }

            spectrum_type = spectrum_map[self.data.spectrum_type_farm]

            spectrum_list = (
                spectrum_type,
                self.data.spectrum_gamma_farm,
                self.data.spectrum_dir_spreading_farm,
            )

            occurrence_matrix["SSH"] = 0.0  # Datum is mean sea level
            occurrence_matrix["specType"] = spectrum_list

        # Convert lease and nogo polygons
        lease_area = self.data.lease_area
        numpy_lease = np.array(lease_area.exterior.coords[:-1])

        if self.data.nogo_areas is None:
            numpy_nogo = None
        else:
            numpy_nogo = [
                np.array(x.exterior.coords[:-1])
                for x in self.data.nogo_areas.values()
            ]

        numpy_landing = np.array(self.data.export_landing_point.coords[0])

        # Bathymetry (**assume layer 1 in uppermost**)
        zv = self.data.bathymetry["depth"].sel(layer="layer 1").values.T
        xv, yv = np.meshgrid(
            self.data.bathymetry["x"].values, self.data.bathymetry["y"].values
        )
        xyz = np.dstack([xv.flatten(), yv.flatten(), zv.flatten()])[0]
        safe_xyz = xyz[~np.isnan(xyz).any(axis=1)]

        # Convert main direction to vector
        if self.data.main_direction is None:
            main_direction_vec = None
        else:
            main_direction_tuple = bearing_to_vector(self.data.main_direction)
            main_direction_vec = np.array(main_direction_tuple)

        Site = WP2_SiteData(
            numpy_lease,
            numpy_nogo,
            occurrence_matrix,
            None,
            None,
            main_direction_vec,
            safe_xyz,
            self.data.blockage_ratio,
            numpy_landing,
            self.data.boundary_padding,
        )

        # #------------------------------------------------------------------------------
        # #------------------------------------------------------------------------------
        # #------------------ WP2 machine data class
        # #------------------------------------------------------------------------------
        # #------------------------------------------------------------------------------
        #
        #    MachineData class: The class contains all the information relative to the machine
        # deployed in the array.
        #
        # Args:
        # Type (str)[-]: defines the type of device either 'tidal' or 'wave'. No other strings are accepted
        # lCS (numpy.ndarray)[m]: position vector of the local coordina system from the given reference point.
        # Wave: represents the position vector of the body CS wrt the mesh CS
        # Tidal: represents the position of the hub from the machine (reference) CS.
        # Clen (numpy.ndarray)[m]: characteristic lenght of the device:
        # Wave: unused
        # Tidal: turbine diameter and distance of the hub from the center line
        # used in case the machine is composed by two parallel turbines
        # YawAngle (float)[rad]: Yaw angle span, wrt the main direction of the array.
        # The total yawing range is two-fold the span. -Yaw/+Yaw
        # Float_flag (bool)[-]: defines whether the machine is floating (True) or not (False)
        # InstalDepth (list)[m]: defines the min and maximum water depth at which the device can be installed
        # MinDist (tuple)[m]: defines the minimum allowed distance between devices in the array configuration
        # the first element is the distance in the x axis
        # the second element is the distance in the y axis
        # OpThreshold (float)[-]: defines the minimum allowed q-facto
        # UserArray (dict): dictionary containing the description of the array layout to be optimise. Keys:
        # 'Option' (int): 1-optimisation over the internal parametric array layouts
        # 2-fixed array layout specified by the user not subject to optimisation
        # 3-array layout specified by the user subject to optimisation via expantion of the array
        # 'Value' options:
        # (str) 'rectangular'
        # (str) 'staggered'
        # (str) 'full'
        # (numpy.ndarray) [m]: [X,Y] coordiantes of the device
        #        RatedPowerArray (float)[W]: Rated power of the array.
        #        RatedPowerDevice (float)[W]: Rated power of the single isolated device.
        #        UserOutputTable (dict, optional): dictionary of dictionaries where all the array layouts inputed and analysed by the user are
        # collected. Using this option the internal WP2 calculation is skipped, and the optimisaton
        # is performed in the given data. The dictionaies keys are the arguments of the WP2 Output class.
        #        wave_data_folder (string, optional): path name of the hydrodynamic results generate by the wave external module
        #        tidal_power_curve (numpy.ndarray, optional)[-]: Power curve function of the stream velocity
        #        tidal_thrust_curve (numpy.ndarray, optional)[-]: Thrust curve function of the stream velocity
        #        tidal_velocity_curve (numpy.ndarray, optional)[m/s]: Vector containing the stream velocity
        #        tidal_cutinout (numpy.ndarray, optional): contain the cut_in and cut_out velocity of the turbine.
        # Outside the cut IN/OUT velocity range the machine will not produce
        # power. The generator is shut down, but the machine will still interact
        # with the others.
        #        tidal_bidirectional (bool, optional): bidirectional working principle of the turbine
        #        tidal_data_folder (string, optional): Path to tidal device CFD data files

        yaw_angle = np.radians(self.data.yaw_angle)
        min_install = self.data.min_install
        max_install = self.data.max_install
        min_dist = (self.data.min_dist_x, self.data.min_dist_y)
        op_threshold = self.data.op_threshold
        install_depth = (min_install, max_install)

        if "Tidal" in self.data.type:
            perf_velocity = self.data.perf_curves.index.values
            cp_curve = self.data.perf_curves["Coefficient of Power"].values
            ct_curve = self.data.perf_curves["Coefficient of Thrust"].values
            cut_in = self.data.cut_in
            cut_out = self.data.cut_out

            dev_type = "Tidal"
            lCS = [0, 0, self.data.hub_height]
            clen = (self.data.rotor_diam, self.data.turbine_interdist)
            wave_data_folder = None
            tidal_power_curve = cp_curve
            tidal_thrust_curve = ct_curve
            tidal_velocity_curve = perf_velocity
            tidal_cutinout = (cut_in, cut_out)
            tidal_bidirectional = self.data.bidirection
            tidal_data_folder = self.data.tidal_data_directory

        else:
            dev_type = "Wave"
            lCS = None
            clen = None
            wave_data_folder = self.data.wave_data_directory
            tidal_power_curve = None
            tidal_thrust_curve = None
            tidal_velocity_curve = None
            tidal_cutinout = None
            tidal_bidirectional = None
            tidal_data_folder = None

        # Set user_array_dict value key
        if self.data.user_array_option in [
            "User Defined Flexible",
            "User Defined Fixed",
        ]:
            if self.data.user_array_layout is None:
                errStr = (
                    "A predefined array layout must be provided when "
                    "using the '{}' array layout option"
                ).format(self.data.user_array_option)
                raise ValueError(errStr)

            numpy_layout = np.array(
                [point.coords[0][:2] for point in self.data.user_array_layout]
            )

            user_array_dict: dict[str, Any] = {"Value": numpy_layout}

        else:
            user_array_dict: dict[str, Any] = {
                "Value": self.data.user_array_option.lower()
            }

        # Set user_array_dict option key
        if self.data.user_array_option == "User Defined Flexible":
            user_array_dict["Option"] = 3
        elif self.data.user_array_option == "User Defined Fixed":
            user_array_dict["Option"] = 2
        else:
            user_array_dict["Option"] = 1

        if "Floating" in self.data.type:
            float_flag = True
        else:
            float_flag = False

        Machine = WP2_MachineData(
            dev_type,
            lCS,
            clen,
            yaw_angle,
            float_flag,
            install_depth,
            min_dist,
            op_threshold,
            user_array_dict,
            self.data.rated_array_power * 1e6,  # Watts
            self.data.rated_power_device * 1e6,  # Watts
            None,
            wave_data_folder,
            tidal_power_curve,
            tidal_thrust_curve,
            tidal_velocity_curve,
            tidal_cutinout,
            tidal_bidirectional,
            tidal_data_folder,
        )

        iWP2input = WP2input(Machine, Site)

        if export_data:
            userdir = UserDataPath("dtocean_core", "DTOcean", "config")
            debug_path = userdir.parent / "debug"
            debug_path.mkdir(exist_ok=True)

            pkl_path = debug_path / "hydrodynamics_inputs.pkl"
            pickle.dump(iWP2input, open(pkl_path, "wb"))

        if debug_entry:
            return

        main = WP2(iWP2input, debug=False)
        result = main.optimisationLoop()

        if result == -1:
            errStr = "Hydrodynamics module failed to execute successfully."
            raise RuntimeError(errStr)

        if export_data:
            assert isinstance(debug_path, Path)
            pkl_path = debug_path / "hydrodynamics_outputs.pkl"
            pickle.dump(result, open(pkl_path, "wb"))

        AEP_per_device = {}
        pow_per_device = {}
        pmf_per_device = {}
        layout = {}
        q_factor_per_device = {}
        dev_ids = []

        # Layout
        for dev_id, coords in result.Array_layout.items():
            dev_id = dev_id.lower()
            layout[dev_id] = np.array(coords)
            dev_ids.append(dev_id)

        dev_ids = natsorted(dev_ids)

        self.data.device_position = layout
        self.data.n_bodies = int(result.Nbodies)

        # Total annual energy (convert to MWh)
        self.data.AEP_array = float(result.Annual_Energy_Production_Array) / 1e6

        # Array capacity factor
        ideal_energy = (
            365 * 24 * self.data.n_bodies * self.data.rated_power_device
        )
        self.data.array_efficiency = self.data.AEP_array / ideal_energy

        # Annual energy per device (convert to MWh)
        for dev_id, AEP in zip(dev_ids, result.Annual_Energy_Production_perD):
            AEP_per_device[dev_id] = float(AEP) / 1e6  # SimpleDIct

        self.data.AEP_per_device = AEP_per_device

        # Mean power per device (convert to MW)
        for dev_id, power in zip(dev_ids, result.power_prod_perD):
            pow_per_device[dev_id] = float(power) / 1e6  # SimpleDIct

        self.data.pow_per_device = pow_per_device

        for dev_id, pow_per_state in zip(dev_ids, result.power_prod_perD_perS):
            # Power probability mass function (convert to MW)
            flat_prob = occurrence_matrix["p"].flatten("F")
            pow_list = pow_per_state / 1e6

            assert np.isclose(flat_prob.sum(), 1.0)
            assert len(flat_prob) == len(pow_list)

            # Find uniques powers
            unique_powers = []

            for power in pow_list:
                if not np.isclose(power, unique_powers).any():
                    unique_powers.append(power)

            # Catch any matching powers and sum the probabilities
            powers = []
            probs = []

            match_index_check = []

            for power in unique_powers:
                matches = np.isclose(power, pow_list)
                assert len(matches) >= 1
                match_idx = np.where(matches)
                match_probs = flat_prob[match_idx]
                match_index_check.extend(match_idx[0].tolist())

                powers.append(power)
                probs.append(match_probs.sum())

                # Nullify the found indexes to ensure uniqueness
                pow_list[match_idx] = np.nan
                flat_prob[match_idx] = np.nan

            repeated_indexes = set(
                [x for x in match_index_check if match_index_check.count(x) > 1]
            )

            assert len(repeated_indexes) == 0
            assert np.isclose(sum(probs), 1.0)

            pmf_per_device[dev_id] = np.array(zip(powers, probs))

        # Power probability histograms
        dev_pow_hists = make_power_histograms(
            pmf_per_device, self.data.rated_power_device, self.data.pow_bins
        )

        self.data.pow_pmf_per_device = pmf_per_device
        self.data.pow_hist_per_device = dev_pow_hists

        # Resource modification
        self.data.q_factor_per_device = q_factor_per_device
        self.data.q_factor_array = result.q_factor_Array

        self.data.resource_reduction = float(result.Resource_Reduction)

        for dev_id, q_factor in zip(dev_ids, result.q_factor_Per_Device):
            q_factor_per_device[dev_id] = q_factor

        # Main Direction
        self.data.main_direction = vector_to_bearing(*result.main_direction)

        # Device type specific outputs
        if "Wave" in self.data.type:
            # External forces
            fex_dict = result.Hydrodynamic_Parameters
            modes = np.array(fex_dict["mode_def"])
            freqs = np.array(fex_dict["wave_fr"])

            # Convert directions to bearings
            bearings = [radians_to_bearing(x) for x in fex_dict["wave_dir"]]
            dirs = np.array(bearings)

            fex_raw = (
                np.zeros([len(modes), len(freqs), len(dirs)], dtype=complex)
                * np.nan
            )

            for i, mode_fex in enumerate(fex_dict["fex"]):
                if mode_fex:
                    fex_raw[i, :, :] = np.expand_dims(mode_fex, axis=1)

            fex_xgrid = {"values": fex_raw, "coords": [modes, freqs, dirs]}

            self.data.ext_forces = fex_xgrid

            ## Power Matrix in kW
            assert result.power_matrix_machine is not None
            assert result.power_matrix_dims is not None
            power_matrix = result.power_matrix_machine / 1000.0
            power_matrix_dims = result.power_matrix_dims

            # Convert directions to bearings
            bearings = [
                radians_to_bearing(x) for x in power_matrix_dims["dirs"]
            ]

            occurrence_matrix_coords = [
                power_matrix_dims["te"],
                power_matrix_dims["hm0"],
                bearings,
            ]

            matrix_xgrid = {
                "values": power_matrix,
                "coords": occurrence_matrix_coords,
            }

            self.data.power_matrix = matrix_xgrid

        return
