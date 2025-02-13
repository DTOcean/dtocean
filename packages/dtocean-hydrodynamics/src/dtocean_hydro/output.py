# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Francesco Ferri
#    Copyright (C) 2017-2025 Mathew Topper
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
This module contains the main class that generates the output format of the
hydrodynamic module.

.. module:: output
     :synopsis: WP2ouput module to DTOcean

.. moduleauthor:: Francesco Ferri <ff@civil.aau.dk>
.. moduleauthor:: Mathew Topper <damm_horse@yahoo.co.uk>
"""

import logging
from pprint import pformat

import numpy as np

# Start logging
module_logger = logging.getLogger(__name__)


class WP2output(object):
    """
    WP2output: output classes of the DTOcean WP2 package.
    The class is collecting the results generated by the wave or tidal modules
    and wrap them in the agreed format.

    Args:
         AEP_array (float)[Wh]: annual energy production of the whole array
         power_prod_perD_perS (numpy.ndarray)[W]: average power production
           of each device within the array for each sea state
         AEP_perD (numpy.ndarray)[Wh]: annual energy production of each device
           within the array
         power_prod_perD (numpy.ndarray)[W]: average power production of each
           device within the array
         Device_Positon (numpy.ndarray)[m]: UTM coordinates of each device in
           the array. NOTE: the UTM coordinates do not consider different UTM
           zones. The maping in the real UTM coordinates is done at a higher
           level.
         Nbodies (float)[]: number of devices in the array
         Resource_reduction (float)[]: ratio between absorbed and incoming
           energy.
         Device_Model (dictionary)[WAVE ONLY]: Simplified model of the wave
           energy converter. The dictionary keys are:
                wave_fr (numpy.ndarray)[Hz]: wave frequencies used to
                                             discretise the frequency space
                wave_dir (numpy.ndarray)[deg]: wave directions used to
                                              discretise the directional space
                mode_def (list)[]: description of the degree of freedom of the
                                   system in agreement with the definition used
                                   in Nemoh
                f_ex (numpy.ndarray)[]: excitation force as a function of
                                        frequency, direction and total degree
                                        of freedoms, normalised by the wave
                                        height.
                                        The degree of freedoms need to be
                                        intended for the whole array, which
                                        is considered as a single body with
                                        several dofs.
         q_perD (numpy.ndarray)[]: q-factor for each device, calculated as
           energy produced by the device within the array over the energy
           produced by the device without interaction
         q_array (float)[]: q-factor for the array, calculated as energy
           produced by the array over the energy produced by the device without
           interaction times the number of devices.
         TI (float)[TIDAL ONLY]: turbulence intensity per seastate
         power_matrix_machine (numpy.ndarray) [WAVE ONLY]:
             power matrix of the single WEC.
         main_direction (numpy.ndarray):
             Easing and Northing coordinate of the main direction vector.

    Attributes:
           same as input arguments

    Returns: None
    """

    def __init__(
        self,
        AEP_array,
        power_prod_perD_perS,
        AEP_perD,
        power_prod_perD,
        Device_Positon,
        Nbodies,
        Resource_reduction,
        Device_Model,
        q_perD,
        q_array,
        main_direction,
        TI=None,
        power_matrix_machine=None,
        power_matrix_dims=None,
    ):
        self.Annual_Energy_Production_Array = AEP_array
        self.power_prod_perD_perS = power_prod_perD_perS
        self.Annual_Energy_Production_perD = AEP_perD
        self.power_prod_perD = power_prod_perD
        self.Array_layout = Device_Positon
        self.Nbodies = Nbodies
        self.Resource_Reduction = Resource_reduction
        self.Hydrodynamic_Parameters = Device_Model
        self.q_factor_Per_Device = q_perD
        self.q_factor_Array = q_array
        self.main_direction = main_direction
        self.TI = TI
        self.power_matrix_machine = power_matrix_machine
        self.power_matrix_dims = power_matrix_dims

        return

    def remap_res(self, connection_point):
        array_layout = np.zeros((self.Nbodies, 2))

        for key in self.Array_layout.keys():
            ID = int(key[6:])
            array_layout[ID, :] = np.array(self.Array_layout[key])

        index_remap = array_indexing(connection_point, array_layout)

        power_prod_perD_perS = self.power_prod_perD_perS
        AEP_perD = self.Annual_Energy_Production_perD
        power_prod_perD = self.power_prod_perD
        Device_Positon = array_layout
        q_perD = self.q_factor_Per_Device

        power_prod_perD_perS_n = np.zeros(power_prod_perD_perS.shape)
        AEP_perD_n = np.zeros(AEP_perD.shape)
        power_prod_perD_n = np.zeros(power_prod_perD.shape)
        Device_Positon_n = np.zeros(Device_Positon.shape)
        q_perD_n = np.zeros(q_perD.shape)

        for ii in index_remap:
            power_prod_perD_perS_n[ii[0], :] = power_prod_perD_perS[ii[1], :]
            AEP_perD_n[ii[0]] = AEP_perD[ii[1]]
            power_prod_perD_n[ii[0]] = power_prod_perD[ii[1]]
            Device_Positon_n[ii[0], :] = Device_Positon[ii[1], :]
            q_perD_n[ii[0]] = q_perD[ii[1]]

        Array_layout_dic = {}

        for bd in range(self.Nbodies):
            Array_layout_dic["Device{:03d}".format(bd + 1)] = Device_Positon_n[
                bd
            ].tolist()

        self.power_prod_perD_perS = power_prod_perD_perS_n
        self.Annual_Energy_Production_perD = AEP_perD_n
        self.power_prod_perD = power_prod_perD_n
        self.Array_layout = Array_layout_dic
        self.q_factor_Per_Device = q_perD_n

        return

    def logRes(self):
        """
        logRes: log the class attributes in the main logger
        """

        results = self._make_results()

        for line in results:
            module_logger.info(line)

        return

    def printRes(self):
        """
        printRes: print the class attributes in the current stdout
        """

        results = self._make_results()

        for line in results:
            print(line)

        return

    def _make_results(self):
        """
        _make_results: gathers the class attributes into a list
        Returns:
            result (list): attribute description and values
        """

        results = []

        results.append("\n")
        results.append("Results Summary")
        results.append("-----------------------------------\n")
        results.append("Annual Energy Production of the Array")
        results.append(self.Annual_Energy_Production_Array)
        results.append("Annual Energy Production of each device")
        results.append("Device listed with ascending ID from 0 to Nbody-1")
        results.append(self.Annual_Energy_Production_perD)
        results.append("Array Layout")
        results.append(pformat(self.Array_layout))
        results.append("q-factor of the array")
        results.append(self.q_factor_Array)
        results.append("q-factor of each device")
        results.append("Device listed with ascending ID from 0 to Nbody-1")
        results.append(self.q_factor_Per_Device)
        results.append("Max (normalised) resource reduction")
        results.append(self.Resource_Reduction)
        results.append(
            "Mean power production of each device for each sea " "state"
        )
        results.append("Device listed with ascending ID from 0 to Nbody-1")
        results.append(
            "For an array of WECs the sea state are flattened in "
            "this order wave period, wave height and wave "
            "direction"
        )
        results.append(self.power_prod_perD_perS)
        results.append("f_ex dictionary")
        results.append(pformat(self.Hydrodynamic_Parameters))
        results.append("Power matrix")
        results.append(self.power_matrix_machine)
        results.append("Main Direction")
        results.append(self.main_direction)

        return results


class ReducedOutput:
    """
    Class used to interface the wave and tidal module to the WP2 Output class

    Args:
         aep_ar (float)[Wh]: annual energy production of the whole array
         aep_dev (numpy.ndarray)[Wh]: annual energy production of each device
           within the array
         q_dev (numpy.ndarray)[]: q-factor for each device, calculated as
           energy produced by the device within the array over the energy
           produced by the device without interaction
         q_ar (float)[]: q-factor for the array, calculated as energy
           produced by the array over the energy produced by the device without
           interaction times the number of devices.
         pow_dev (numpy.ndarray)[W]: average power production of each
           device within the array
         pow_dev_state (numpy.ndarray)[W]: average power production
           of each device within the array for each sea state
         nb (float)[]: number of devices in the array
         pos (numpy.ndarray)[m]: UTM coordinates of each device in
           the array. NOTE: the UTM coordinates do not consider different UTM
           zones. The maping in the real UTM coordinates is done at a higher
           level.
         res_red (float)[]: ratio between absorbed and incoming
           energy.
         ti (float)[TIDAL ONLY]: turbulence intensity per seastate
         dev_model (dictionary)[WAVE ONLY]: Simplified model of the wave
           energy converter. The dictionary keys are:
                wave_fr (numpy.ndarray)[Hz]: wave frequencies used to
                                             discretise the frequency space
                wave_dir (numpy.ndarray)[deg]: wave directions used to
                                              discretise the directional space
                mode_def (list)[]: description of the degree of freedom of the
                                   system in agreement with the definition used
                                   in Nemoh
                f_ex (numpy.ndarray)[]: excitation force as a function of
                                        frequency, direction and total degree
                                        of freedoms, normalised by the wave
                                        height.
                                        The degree of freedoms need to be
                                        intended for the whole array, which
                                        is considered as a single body with
                                        several dofs.
         power_matrix_machine (numpy.ndarray) [WAVE ONLY]:
             power matrix of the single WEC.
         power_matrix_dims (numpy.ndarray) [WAVE ONLY]:
             dimensions for the power matrix of the single WEC.

    """

    def __init__(
        self,
        aep_ar,
        aep_dev,
        q_ar,
        q_dev,
        pow_dev,
        pow_dev_state,
        nb,
        pos,
        res_red,
        ti=None,
        dev_model=None,
        power_matrix_machine=None,
        power_matrix_dims=None,
    ):
        self.AEP_array = aep_ar
        self.power_prod_perD_perS = pow_dev_state
        self.AEP_perD = aep_dev
        self.power_prod_perD = pow_dev
        self.Device_Position = pos
        self.Nbodies = nb
        self.Resource_reduction = res_red
        self.Device_Model = dev_model
        self.q_perD = q_dev
        self.q_array = q_ar
        self.TI = ti
        self.power_matrix_machine = power_matrix_machine
        self.power_matrix_dims = power_matrix_dims


def array_indexing(pcc, array_layout):
    def get_first_element(pcc, xy2):
        diff = pcc - xy2
        dist = np.hypot(diff[:, 0], diff[:, 1])

        return dist.argmin(), dist.min()

    n = len(array_layout)
    Nbodies = len(array_layout)
    d0 = np.subtract.outer(array_layout[:, 0], array_layout[:, 0])
    d1 = np.subtract.outer(array_layout[:, 1], array_layout[:, 1])
    dist = np.hypot(d0, d1)

    id_first, _ = get_first_element(pcc, array_layout)

    map_ids = [[0, id_first]]
    id_prev = id_first

    for nb in range(Nbodies - 1):
        ds = dist[id_prev, :]
        result = min(
            enumerate(ds), key=lambda x: x[1] if x[1] > 0 else float("inf")
        )

        map_ids.append([nb + 1, result[0]])

        mask = np.ones((n, n))
        mask[id_prev, :] = 0
        mask[:, id_prev] = 0

        dist = dist * mask
        id_prev = result[0]

    return map_ids
