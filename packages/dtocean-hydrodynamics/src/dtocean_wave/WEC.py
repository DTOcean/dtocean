# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Pau Mercadez Ruiz
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
This module contains the class used to describe the behavior of the single WEC

.. module:: WEC
   :platform: Windows
   :synopsis: WEC model

.. moduleauthor:: Pau Mercadez Ruiz <pmr@civil.aau.dk>
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import logging

import numpy as np
import utils.read_bem_solution as reader
from utils.StrDyn import EnergyProduction

module_logger = logging.getLogger(__name__)


class wec(object):
    """
    WEC: the class assess the hydrodynamic model ot the given WEC

    Args:
        FilesPath (str): name of the path containing the WECmodes.wp2, mesh files and results (WAMIT case)
        water_depth (float): average water depth at the site location
        lCS (list): local coordinate system of the machine
        debug (boolean): debug flag

    Attributes:
        solver (?): solver used to generate the hydrodynamic model
        pathname (str):  name of the path containing the WECmodes.wp2, mesh files and results (WAMIT case)
        depth (float): average water depth of the site
        iInput (WP2input class): object gathering the required WP2 package inputs
        iHydro (Hydro_pkg class): object containing the specification of the sea states, frequencies and directions to be analysed
        period (numpy.ndarray): vector containing the wave periods to be analysed
        wnumber (numpy.ndarray): vector containing the wave numbers to be analysed
        dir (numpy.ndarray): vector containing the wave directions to be analysed
        _debug (boolean): debug flag
        Fex (numpy.ndarray): excitation force in function of the dof, frequency and direction
        Madd (numpy.ndarray): added mass in function of the dof and frequency
        Crad (numpy.ndarray): radiation damping in function of the dof and frequency
        Khyd (numpy.ndarray): hydrostatic matrix function of the dofs
        M (numpy.ndarray): mass matrix function of the dofs
        radius (float): circumscribing cylinder radius
        fpazimuth (numpy.ndarray): angular discretisation of the circumscribing cylinder
        fpdepth (numpy.ndarray): vertical discretisation of the circumscribing cylinder
        depth (flaot): average water depth of the location
        totDOF (float): total number of degree of freedom of the system
        ptoDOF (numpy.ndarray): ID of the dofs connected to the power take off system
        mooDOF (numpy.ndarray): ID of the dofs connected to the mooring system
        CPTO (numpy.ndarray): PTO damping function of the sea states and dof for the array
        CPTO_sm (numpy.ndarray): PTO damping function of the sea states and dof for the single machine
        Kmooring (numpy.ndarray): mooring stiffness function of the sea states and dof for the array
        Kmooring_sm (numpy.ndarray): mooring stiffness function of the sea states and dof for the single machine
        order (numpy.ndarray): max order of the wave modes used to describe the array field around and generated by the body
        truncorder (numpy.ndarray): representative order of the wave modes used to describe the array field around and generated by the body
        G (numpy.ndarray): force transfer matrix associated with the WEC
        D (numpy.ndarray): diffraction transfer matrix associated with the WEC
        AR (numpy.ndarray): partial wave amplitude associated with the WEC
        energyproduction (numpy.ndarray): average energy produced per year for the given sea states
        power (numpy.ndarray): power matrix of the WEC
        RAO (numpy.ndarray): response amplitude operator of the WEC
        Cfit (numpy.ndarray): damping fitting, calculated to reduce the error between the cetified and calculated power matrixes
        Kfit (numpy.ndarray): stiffness fitting, calculated to reduce the error between the cetified and calculated power matrixes
    """

    def __init__(self, FilesPath, water_depth, rated_power, debug=False):
        self.pathname = FilesPath
        self.depth = water_depth
        self.rated_power = rated_power
        self._debug = debug

        # the following input are populated using the given BEM solution
        self.period = None
        self.wnumber = None
        self.dir = None

    def load_single_machine_model(self, specType, pickup=True):
        """
        load_single_machine_model: loads the hydrodynamic model of the single machine passed by the user.
        Args (optional):
            pickup (unused)

        Returns:

        """
        (
            self.M,
            self.Madd,
            self.Crad,
            self.Khyd,
            self.Fex,
            self.period,
            self.directions,
            self.D,
            self.G,
            self.AR,
            self.water_depth,
            self.radius,
            self.modes,
            self.order,
            self.truncorder,
        ) = reader.read_hydrodynamic_solution(self.pathname)

        (
            self.Cfit,
            self.Kfit,
            self.CPTO,
            self.Kmooring,
            self.w_te,
            self.w_hm0,
            self.w_dirs,
            self.scatter_diagram,
            self.power_matrix,
        ) = reader.read_performancefit_solution(self.pathname)

        # Calculate Tp values for power matrix
        self.w_tp = convert_te2tp(self.w_te, specType[0], specType[1])

        # Clip any values above rated power in power matrix
        self.power_matrix = np.clip(self.power_matrix, None, self.rated_power)

    #        This check has been moved in the main file and it will trigger a warning to be exposed to the user.
    #        if not np.allclose(self.water_depth, self.depth):
    #            raise ValueError("The water depth of the BEM solution and the",
    #            "one calculated from the bathyemtry are not in agreement. ",
    #            "The given bem solution cannot be used.")

    def energy(self, hydro_mb):
        """
        _energy: assess the enegy production of the machine for the given sea states

        Args:
            iHydro (Hydro_pkg class): object containing the specification of the sea states, frequencies and directions to be analysed
        """

        NBo = 1  # Number of bodies

        (Pyr, P, RAO) = EnergyProduction(
            NBo,
            hydro_mb.B,
            hydro_mb.Hs,
            hydro_mb.Tp,
            self.directions,
            self.period,
            [hydro_mb.ScatDiag, hydro_mb.specType],
            self.M,
            self.Madd,
            self.CPTO,
            self.Crad,
            self.Kmooring,
            self.Khyd,
            self.Fex,
            self.Kfit,
            self.Cfit,
            self.rated_power,
        )

        self.energyproduction = Pyr
        self.power = P
        self.RAO = RAO

    def matrix_zoh_interp(self, hydro_mb):
        """ZOH interpolation of numpy matrixes"""
        cpto = wec.__reshape_matrix(
            self.CPTO, hydro_mb, self.w_tp, self.w_hm0, self.w_dirs
        )
        cfit = wec.__reshape_matrix(
            self.Cfit, hydro_mb, self.w_tp, self.w_hm0, self.w_dirs
        )
        kmoor = wec.__reshape_matrix(
            self.Kmooring, hydro_mb, self.w_tp, self.w_hm0, self.w_dirs
        )
        kfit = wec.__reshape_matrix(
            self.Kfit, hydro_mb, self.w_tp, self.w_hm0, self.w_dirs
        )

        return (cpto, cfit, kmoor, kfit)

    @staticmethod
    def __reshape_matrix(mat, hydro_mb, w_tp, w_hm0, w_dirs):
        """ZOH interpolation of numpy matrixes between the isolated scatter diagram and the lease area scatter diagram
        Args:
            mat: numpy array to be used
            hydro_mb: metocean conditions at the lease area site

        Returns: out_mat: zoh copy of the input matrix mat

        """
        per_mb = hydro_mb.Tp
        hei_mb = hydro_mb.Hs
        dir_mb = hydro_mb.B
        n_mb_per = len(per_mb)
        n_mb_hei = len(hei_mb)
        n_mb_dir = len(dir_mb)
        n_dof = mat.shape[-1]

        i_per = np.argmin(np.abs(np.subtract.outer(w_tp, per_mb)), 0)
        i_hei = np.argmin(np.abs(np.subtract.outer(w_hm0, hei_mb)), 0)
        i_dir = np.argmin(np.abs(np.subtract.outer(w_dirs, dir_mb)), 0)

        out_mat = np.zeros((n_mb_per, n_mb_hei, n_mb_dir, n_dof, n_dof))
        for iper in range(n_mb_per):
            for ihei in range(n_mb_hei):
                for idir in range(n_mb_dir):
                    out_mat[iper, ihei, idir, :, :] = mat[
                        i_per[iper], i_hei[ihei], i_dir[idir], :, :
                    ]
        return out_mat


def convert_te2tp(te, specType, gamma):
    coeff = np.array(
        [
            [1.22139232e00],
            [-7.26257028e-02],
            [1.74397331e-02],
            [-2.19288663e-03],
            [1.07357912e-04],
        ]
    )

    # convert Te to Tp for the Metocean condition relative to the deployment site
    conversion_factor = 1.16450471

    if specType == "Jonswap":
        if gamma > 7 or gamma < 1:
            module_logger.warning(
                "The gamma value of the JONSWAP spectrum "
                "in the metocean data specification is out "
                "of the confident range [1-7]."
            )

        conversion_factor = (
            coeff[0]
            + coeff[1] * gamma
            + coeff[2] * gamma**2
            + coeff[3] * gamma**3
            + coeff[4] * gamma**4
        )

    tp = te * conversion_factor

    return tp


if __name__ == "__main__":
    FilesPath = r"C:\Users\francesco\Desktop\dtocean_wave_test"
    wec_obj = wec(FilesPath, 51.0, np.array([0.0, 0.0, 0.0, 0.0]), debug=False)
    wec_obj.load_hydrodynamic_model()
    wec_obj.Transfers()
