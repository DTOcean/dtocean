#    Copyright (C) 2021-2025 Mathew Topper
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
This module contains the tool interface checking device spacing constraints

Note:
  The function decorators (such as "@classmethod", etc) must not be removed.

.. moduleauthor:: Mathew Topper <damm_horse@yahoo.co.uk>
"""

from typing import Optional, Union

import numpy as np
from mdo_engine.boundary.interface import MaskVariable
from shapely.geometry import Polygon, box

from dtocean_hydro.array import Array_pkg
from dtocean_hydro.utils.bathymetry_utility import get_unfeasible_regions
from dtocean_hydro.utils.convert import (
    bearing_to_vector,
    make_tide_statistics,
    make_wave_statistics,
)
from dtocean_hydro.utils.set_wdirs_multibody import anglewrap, convertangle
from dtocean_plugins.tools.base import Tool

FloatOrInt = Union[float, int]


class SpacingConstraintsTool(Tool):
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

        return "Device Minimum Spacing Check"

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
            "device.installation_depth_max",
            "device.installation_depth_min",
            "device.minimum_distance_x",
            "device.minimum_distance_y",
            MaskVariable(
                "device.turbine_interdistance",
                "device.system_type",
                ["Tidal Fixed", "Tidal Floating"],
            ),
            "project.main_direction",
            "options.boundary_padding",
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

        output_list = None

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
            "options.boundary_padding",
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
            "bathymetry": "bathymetry.layers",
            "boundary_padding": "options.boundary_padding",
            "lease_area": "site.lease_boundary",
            "max_install": "device.installation_depth_max",
            "min_dist_x": "device.minimum_distance_x",
            "min_dist_y": "device.minimum_distance_y",
            "min_install": "device.installation_depth_min",
            "spectrum_dir_spreading_farm": "farm.spec_spread",
            "spectrum_gamma_farm": "farm.spec_gamma",
            "spectrum_type_farm": "farm.spectrum_name",
            "tidal_nbins": "project.tidal_occurrence_nbins",
            "tidal_occurrence": "farm.tidal_occurrence",
            "tidal_occurrence_point": "farm.tidal_occurrence_point",
            "tidal_series": "farm.tidal_series",
            "turbine_interdist": "device.turbine_interdistance",
            "type": "device.system_type",
            "wave_series": "farm.wave_series",
            "main_direction": "project.main_direction",
        }

        return id_map

    def configure(self, layout):  # pylint: disable=arguments-differ
        config_dict = {"layout": layout}
        self.set_config(config_dict)

    def connect(self, **kwargs):  # pylint: disable=unused-argument
        if "layout" not in self._config:
            err_msg = "Key 'layout' missing from config. Was configure called?"
            raise RuntimeError(err_msg)

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

        else:
            occurrence_matrix = make_wave_statistics(self.data.wave_series)

            p_total = occurrence_matrix["p"].sum()

            if not np.isclose(p_total, 1.0):
                errStr = (
                    "Wave statistics probabilities invalid. Total "
                    "probability equals {}"
                ).format(p_total)
                raise ValueError(errStr)

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

        # Snap lease area to bathymetry
        bathy_x = self.data.bathymetry["x"]
        bathy_y = self.data.bathymetry["y"]
        bathy_box = box(
            bathy_x.min(), bathy_y.min(), bathy_x.max(), bathy_y.max()
        )

        lease_area = self.data.lease_area
        sane_lease_area = lease_area.intersection(bathy_box)

        # Convert lease and nogo polygons
        numpy_lease = np.array(sane_lease_area.exterior.coords[:-1])

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

        min_install = self.data.min_install
        max_install = self.data.max_install
        min_dist = (self.data.min_dist_x, self.data.min_dist_y)
        install_depth = (min_install, max_install)

        numpy_layout = np.array(self._config["layout"])

        if main_direction_vec is None:
            if "Tidal" in self.data.type:
                main_angle = get_main_angle_tidal(occurrence_matrix)

            else:
                # convert the scatter diagram angle convention to fit the
                # East-North convention
                change_angle_convention(occurrence_matrix)
                main_angle = get_main_angle_wave(occurrence_matrix)

        else:
            main_angle = anglewrap(
                np.arctan2(main_direction_vec[1], main_direction_vec[0]),
                conversion="r2r",
            )

        (la_buffer_exterior, la_exterior) = compress_lease_area(
            numpy_lease,
            self.data.boundary_padding,
            self.data.turbine_interdist,
        )

        nogo_areas, _ = get_unfeasible_regions(safe_xyz, install_depth)

        array = Array_pkg(
            la_buffer_exterior, la_exterior, min_dist, main_angle, nogo_areas
        )

        array.coord = numpy_layout
        array.checkMinDist()

        if array.minDist_constraint:
            msg_str = (
                "Violation of the minimum distance constraint between "
                "at least one device. Maximum ellipse transect "
                "percentage: {}"
            ).format(array._mindist_percent_max)  # pylint: disable=protected-access
            raise RuntimeError(msg_str)


def compress_lease_area(
    lease_area,
    boundary_padding: Optional[FloatOrInt] = None,
    MCT_buffer: Optional[FloatOrInt] = None,
):
    if boundary_padding is None:
        boundary_padding = 0.0

    if MCT_buffer is None:
        MCT_buffer = 0.0

    overall_buffer = max(MCT_buffer, abs(max(0, boundary_padding)))
    lease_pol = Polygon(lease_area)

    # always contraction
    lease_pol_buffer = lease_pol.buffer(-overall_buffer)

    buffer_exterior = np.c_[lease_pol_buffer.exterior.xy]
    exterior = np.c_[lease_pol.exterior.xy]

    return buffer_exterior, exterior


def change_angle_convention(meteocean_conditions):
    """
    Convert the angles given in the metocean convention into the East-North
    coordinate system.
    """

    old_beta_array = meteocean_conditions["B"]
    new_beta_array = convertangle(old_beta_array)
    meteocean_conditions["B"] = new_beta_array


def get_main_angle(func):
    def wrapper(meteocean_conditions):
        main_direction = func(meteocean_conditions)
        main_angle = anglewrap(
            np.arctan2(main_direction[1], main_direction[0]), conversion="r2r"
        )

        return main_angle

    return wrapper


@get_main_angle
def get_main_angle_tidal(meteocean_conditions):
    ind_max_direction = np.argmax(meteocean_conditions["p"])
    U = np.nanmean(meteocean_conditions["U"][:, :, ind_max_direction])
    V = np.nanmean(meteocean_conditions["V"][:, :, ind_max_direction])
    main_direction = -np.array([U, V])

    return main_direction


@get_main_angle
def get_main_angle_wave(meteocean_conditions):
    # The main direction is given by the direcion of the scatter diagram with
    # highest probability of occurrence
    ind_max_direction = np.argmax(np.sum(meteocean_conditions["p"], (0, 1)))
    angle = meteocean_conditions["B"][ind_max_direction]
    main_direction = np.array([np.cos(angle), np.sin(angle)], dtype=float)

    return main_direction
