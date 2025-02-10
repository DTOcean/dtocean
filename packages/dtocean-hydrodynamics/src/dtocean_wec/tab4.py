# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Francesco Ferri
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
Created on Wed Jun 15 09:15:29 2016

.. moduleauthor:: Francesco Ferri <ff@civil.aau.dk>
"""

import os

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog, QWidget

from .form_utils import send_data_to_bem_interface
from .generated.ui_read_wamit_form import Ui_Form as Ui_T4
from .submodule.utils import input_control as in_ck
from .utils import data_check as dck
from .utils.file_utilities import split_string


class ReadWamit(QWidget, Ui_T4):
    trigger_results = Signal(dict)
    trigger_save = Signal(dict)
    trigger_reset_forms = Signal()
    trigger_mesh_view = Signal(dict)

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.btn_browse_t4.clicked.connect(self.browse_data)
        self.btn_load_data_t4.clicked.connect(self.load_data)
        self.btn_mesh_f_t4.clicked.connect(self.load_mesh)
        self.btn_view_mesh_t4.clicked.connect(self.show_mesh)
        self.btn_submit_t4.clicked.connect(self.submit)
        self.btn_load_data_t4.setEnabled(False)
        self.trigger_results.connect(parent.set_hydrodynamic_results)
        self.trigger_save.connect(parent.task_save_hydrodynamic)
        self.trigger_mesh_view.connect(parent.task_show_mesh)

        self.db_folder = os.path.join(parent.wec_share_path, "wec_db")
        self.bin_folder = parent.bin_path
        self._raw = "raw_data"
        self._prj = parent._data["prj_folder"]

    def set_data(self, data):
        self._data = data
        self.populate_prj()
        self.btn_load_data_t4.setEnabled(False)

        if "hyd" in data.keys():
            self.trigger_results.emit(self._data["hyd"])

    def save_project(self):
        inputs_hydrodynamic = self.pull_data_from_form()

        dic_cmp = dck.compare_dictionaries(
            self._data["inputs_hydrodynamic"],
            inputs_hydrodynamic,
            "d1",
            "d2",
        )

        if dic_cmp != "":
            self._data["inputs_hydrodynamic"] = inputs_hydrodynamic
            if "hyd" in self._data.keys():
                print(
                    "the hydrodynamic inputs have been modified, the hydrodynamic results and the power fit results will be deleted!"
                )
                del self._data["hyd"]
            self.trigger_save.emit(inputs_hydrodynamic)
            self.trigger_reset_forms.emit()

        else:
            self.trigger_save.emit(inputs_hydrodynamic)
            if "hyd" in self._data.keys():
                self.trigger_results.emit(self._data["hyd"])

    def pull_data_from_form(self):
        get_array_mat = self.cb_gen_array_mat_t4.isChecked()

        input_type = 4
        ndof = split_string(self.ndof_t4.text(), int)
        pto_dof = split_string(self.pto_dof_t4.text(), int, sep=",")
        moor_dof = split_string(self.moor_dof_t4.text(), int, sep=",")
        data_f = self.le_data_t4.text()
        mesh_f = self.mesh_f_t4.text()
        general_inputs = {
            "ndof": ndof,
            "pto_dof": pto_dof,
            "mooring_dof": moor_dof,
            "frequency_def": [],
            "angle_def": [],
            "data_folder": data_f,
            "water_depth": [],
            "get_array_mat": int(get_array_mat),
            "cyl_nzeta": [],
            "cyl_ntheta": [],
            "input_type": input_type,
        }

        body0 = {"body0": {"mesh": mesh_f}}
        body_inputs = {"local_cs": [], "shared_dof": [], "body": body0}
        inputs_hydrodynamic = {
            "general_input": general_inputs,
            "body_inputs": body_inputs,
        }

        return inputs_hydrodynamic

    def submit(self):
        status = self.check()
        self.save_project()
        if status:
            self.btn_load_data_t4.setEnabled(True)

            self._data["inputs_hydrodynamic"]["general_input"]["ndof"] = (
                split_string(self.ndof_t4.text(), int)
            )
            self._data["inputs_hydrodynamic"]["general_input"]["pto_dof"] = (
                split_string(self.pto_dof_t4.text(), int, sep=",")
            )
            self._data["inputs_hydrodynamic"]["general_input"][
                "mooring_dof"
            ] = split_string(self.moor_dof_t4.text(), int, sep=",")
            self._data["inputs_hydrodynamic"]["general_input"]["input_type"] = 4
            self._data["inputs_hydrodynamic"]["general_input"][
                "data_folder"
            ] = self.le_data_t4.text()
            self._data["inputs_hydrodynamic"]["general_input"][
                "get_array_mat"
            ] = int(self.cb_gen_array_mat_t4.isChecked())

        else:
            self.btn_load_data_t4.setEnabled(False)

    def check(self):
        if os.path.isdir(self.le_data_t4.text()):
            data_folder = self.le_data_t4.text()
            status = in_ck.check_wamit_results(
                data_folder, get_array_mat=self.cb_gen_array_mat_t4.isChecked()
            )
            if status[0]:
                ndof = split_string(self.ndof_t4.text(), int)

                if not ndof:
                    print("Missing number of independent dof")
                    return False
                else:
                    return True
            else:
                assert len(status) == 2
                print(status[1])
                return False
        else:
            print("The specified path is not a valid folder")
            return False

    def load_mesh(self):
        folder, _ = QFileDialog.getOpenFileName(
            self,
            "Select the mesh file relative to the body.",
        )
        self.mesh_f_t4.setText(folder)

    def show_mesh(self):
        filename = str(self.mesh_f_t4.text())
        if not os.path.isfile(filename):
            fn = os.path.basename(filename)
            filename = os.path.join(self._prj, self._raw, fn)
            if not os.path.isfile(filename):
                self.load_mesh()

        path, file_name = os.path.split(filename)
        self.trigger_mesh_view.emit({"path": path, "f_n": file_name})

    def load_data(self):
        self.btn_load_data_t4.setEnabled(False)
        self.btn_submit_t4.setEnabled(False)

        stat = send_data_to_bem_interface(
            self._data, self.db_folder, self.bin_folder
        )

        if stat[0]:
            self._data["hyd"] = stat[1]
            self.btn_submit_t4.setEnabled(True)
            self.trigger_results.emit(stat[1])

    def browse_data(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select the WAMIT results folder"
        )
        self.le_data_t4.setText(folder)

    def populate_prj(self):
        in_hy = self._data["inputs_hydrodynamic"]
        in_g = in_hy["general_input"]

        self.ndof_t4.setText(",".join([str(el) for el in in_g["ndof"]]))
        self.pto_dof_t4.setText(",".join([str(el) for el in in_g["pto_dof"]]))
        self.moor_dof_t4.setText(
            ",".join([str(el) for el in in_g["mooring_dof"]])
        )
        if os.path.isdir(in_g["data_folder"]):
            self.le_data_t4.setText(in_g["data_folder"])

        if not in_hy["body_inputs"]["body"] == -1:
            if os.path.isfile(in_hy["body_inputs"]["body"]["body0"]["mesh"]):
                self.mesh_f_t4.setText(
                    in_hy["body_inputs"]["body"]["body0"]["mesh"]
                )
        self.cb_gen_array_mat_t4.setChecked(bool(in_g["get_array_mat"]))
