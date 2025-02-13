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
Created on Mon Jun 13 17:55:42 2016

.. moduleauthor:: Francesco Ferri <ff@civil.aau.dk>
.. moduleauthor:: Mathew Topper <damm_horse@yahoo.co.uk>
"""

import os
import shutil
from pathlib import Path
from typing import Union

import numpy as np

from .submodule.main import BemSolution
from .utils.data_interface import DataStructure

StrOrPath = Union[str, Path]


def send_data_to_bem_interface(
    data, db_folder, bin_folder, force_read_flag=False
):
    print("Creating the data structure")
    dataobj = DataStructure(data, force_read_flag=force_read_flag)
    in_stat = dataobj.check_inputs()
    if in_stat[0]:
        print("Sending data to the BEM class")
        wec_obj = BemSolution(dataobj, db_folder, bin_folder, debug=False)
        wec_obj.call_module()
        assert wec_obj.reader is not None

        print("Saving the data")
        hyd = {
            "periods": wec_obj.reader.periods,
            "directions": wec_obj.reader.directions,
            "m_m": wec_obj.reader.m_m,
            "m_add": wec_obj.reader.m_add,
            "c_rad": wec_obj.reader.c_rad,
            "k_hst": wec_obj.reader.k_hst,
            "pto_dof": wec_obj.reader.pto_dof,
            "mooring_dof": wec_obj.reader.moor_dof,
            "order": wec_obj.reader.order,
            "f_ex": wec_obj.reader.f_ex,
            "diffraction_tr_mat": wec_obj.reader.diffraction_tr_mat,
            "force_tr_mat": wec_obj.reader.force_tr_mat,
            "amplitude_coefficient_radiation": wec_obj.reader.amplitude_coefficient_radiation,
            "water_depth": wec_obj.reader.water_depth,
            "cyl_radius": wec_obj.reader.cyl_radius,
            "modes": wec_obj.reader.modes,
            "max_order": wec_obj.reader.order,
            "truncation_order": wec_obj.reader.truncation_order,
        }

        return (True, hyd)
    else:
        assert len(in_stat) == 2
        print("The data submitted did not pass the input check")
        return (False, in_stat[1])


def raise_error(el, obj, el_sh, label_err, gt=True):
    label_err.setText("")
    label_err.setStyleSheet("QLabel {color:black}")
    obj.setStyleSheet("QLineEdit {border: 0px}")

    if not el:
        label_err.setText("invalid inputs")
        label_err.setStyleSheet("QLabel {color:red}")
        obj.setStyleSheet("QLineEdit {border: 1px solid red}")
        return -1

    elif not len(el) == el_sh:
        if gt:
            if not len(el) >= el_sh:
                label_err.setText("invalid inputs")
                label_err.setStyleSheet("QLabel {color:red}")
                obj.setStyleSheet("QLineEdit {border: 1px solid red}")

                return -1
    return 0


def check_wec_db_data(wec_db_data):
    requirements = ["hyd", "p_fit", "inputs_hydrodynamic", "inputs_pm_fit"]
    missing_fields = [x for x in requirements if x not in wec_db_data.keys()]

    if missing_fields:
        return (False, missing_fields)

    return (True, wec_db_data)


def final_data_check(dic):
    requirements_hyd = [
        "m_m",
        "m_add",
        "c_rad",
        "f_ex",
        "periods",
        "directions",
        "k_hst",
        "diffraction_tr_mat",
        "force_tr_mat",
        "amplitude_coefficient_radiation",
        "water_depth",
        "cyl_radius",
        "modes",
        "max_order",
        "truncation_order",
        "mooring_dof",
        "pto_dof",
    ]
    requirements_pfit = [
        "c_ext",
        "k_ext",
        "c_fit",
        "k_fit",
        "c_pto",
        "k_mooring",
        "te",
        "hm0",
        "wave_dir",
        "scatter_diagram",
    ]

    ind_key = [
        iel
        for iel, el in enumerate(requirements_hyd)
        if el not in dic["hyd"].keys()
    ]
    list_miss_items_hyd = np.asarray(requirements_hyd)[ind_key].tolist()

    ind_key = [
        iel
        for iel, el in enumerate(requirements_pfit)
        if el not in dic["p_fit"].keys()
    ]
    list_miss_items_pfit = np.asarray(requirements_pfit)[ind_key].tolist()

    list_miss_items = list_miss_items_hyd + list_miss_items_pfit
    if list_miss_items:
        return (False, list_miss_items)

    return (True,)


def _dtocean_data_check(dic):
    requirements = [
        "m_m",
        "m_add",
        "c_rad",
        "f_ex",
        "periods",
        "directions",
        "k_hst",
        "diffraction_tr_mat",
        "force_tr_mat",
        "amplitude_coefficient_radiation",
        "water_depth",
        "cyl_radius",
        "modes",
        "max_order",
        "truncation_order",
        "mooring_dof",
        "pto_dof",
        "c_ext",
        "k_ext",
        "c_fit",
        "k_fit",
        "c_pto",
        "k_mooring",
        "te",
        "hm0",
        "wave_dir",
        "scatter_diagram",
        "power_matrix",
    ]

    ind_key = [
        iel for iel, el in enumerate(requirements) if el not in dic.keys()
    ]
    list_miss_items = np.asarray(requirements)[ind_key].tolist()

    list_miss_items = list_miss_items
    if list_miss_items:
        return (False, list_miss_items)

    return (True,)


def clean_prj_folder(path, exept=None, only=None):
    # remove all files and subfolders from the project folder
    folder_ls = os.listdir(path)
    if exept is not None:
        if isinstance(exept, list):
            for ex in exept:
                folder_ls = [el for el in folder_ls if el != ex]
        folder_ls = [el for el in folder_ls if el != exept]
    if only is not None:
        folder_ls = [el for el in folder_ls if el == only]

    for el in folder_ls:
        el_path = os.path.join(path, el)
        try:
            if os.path.isfile(el_path):
                os.unlink(el_path)
            elif os.path.isdir(el_path):
                shutil.rmtree(el_path)
        except OSError as e:
            return (False, e)

    return (True, "")
