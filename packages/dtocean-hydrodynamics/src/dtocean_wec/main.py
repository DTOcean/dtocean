# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Francesco Ferri, Mathew Topper
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
Created on Fri Jun 10 11:22:25 2016

.. moduleauthor:: Francesco Ferri <ff@civil.aau.dk>
.. moduleauthor:: Mathew Topper <damm_horse@yahoo.co.uk>
"""

import logging
import os
import sys

from PySide6.QtCore import QItemSelection, QObject, Qt, Signal, Slot
from PySide6.QtGui import QBrush, QColor, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMdiSubWindow,
    QMessageBox,
    QWidget,
)

import dtocean_wave.utils.hdf5_interface as h5i
from dtocean_hydro.configure import get_install_paths

from .form_utils import clean_prj_folder, final_data_check
from .generated.ui_load_new import Ui_Form as Ui_LN
from .generated.ui_mdi_layout import Ui_MainWindow
from .generated.ui_new_selection import Ui_Form as Ui_NP
from .pfit_form import PowerPerformance
from .plot_form import Plotter
from .tab1 import ReadDb
from .tab2 import RunNemoh
from .tab3 import ReadNemoh
from .tab4 import ReadWamit
from .utils.mesh_plotter import PythonQtOpenGLMeshViewer


class QtHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        record = self.format(record)
        if record:
            XStream.stdout().write("%s\n" % record)
        # originally: XStream.stdout().write("{}\n".format(record))


logger = logging.getLogger(__name__)
handler = QtHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class XStream(QObject):
    _stdout = None
    _stderr = None
    messageWritten = Signal(str)

    def flush(self):
        pass

    def fileno(self):
        return -1

    def write(self, msg):
        if not self.signalsBlocked():
            self.messageWritten.emit(msg)

    @staticmethod
    def stdout():
        if not XStream._stdout:
            XStream._stdout = XStream()
            sys.stdout = XStream._stdout
        return XStream._stdout

    @staticmethod
    def stderr():
        if not XStream._stderr:
            XStream._stderr = XStream()
            sys.stderr = XStream._stderr
        return XStream._stderr


class NewProject(QWidget, Ui_NP):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)


class Entrance(QWidget, Ui_LN):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)


class MainWindow(QMainWindow, Ui_MainWindow):
    count = 0

    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.lw_area.hide()
        self.run_entrance()
        self._data = None

        XStream.stdout().messageWritten.connect(self.console.insertPlainText)
        XStream.stderr().messageWritten.connect(self.console.insertPlainText)

        # Get path to data dirs through configuration
        path_dict = get_install_paths()
        self.bin_path = path_dict["bin_path"]
        self.wec_share_path = path_dict["wec_share_path"]

        self.form_hyd = None
        self.form_power = None
        self.form_plot = None

        self.sub_hyd = None
        self.sub_power = None
        self.sub_plot = None

        self._test_dialog = None

        # File menu
        self.actionNew_Project.triggered.connect(self.handle_new_project)
        self.actionLoad_Project.triggered.connect(self.handle_new_project)
        self.actionSave_Project.triggered.connect(self.handle_save_project)

        # DTOcean menu
        self.actionGenerate_array_hydrodynamic.triggered.connect(
            self.save_dtocean_format
        )

        # Windows menu
        self.actionHydrodynamic.triggered.connect(self.handle_open_hyd)
        self.actionPerformance_Fit.triggered.connect(self.handle_open_power)
        self.actionData_Visualisation.triggered.connect(self.handle_open_plot)

        return

    def task_show_mesh(self, path):
        self.mesh_view = PythonQtOpenGLMeshViewer(path["path"], path["f_n"])
        self.mesh_view.show()

    @Slot()
    def handle_new_project(self):
        if self._data is None:
            self.gen_new_project()
        else:
            self.new_project_choice()

    @Slot()
    def handle_load_project(self):
        if self._data is None:
            self.load_project()
        else:
            self.load_project_choice()

    @Slot()
    def handle_save_project(self):
        if self._data is None:
            return

        self.pull_data_from_child()
        self.save_project()

    @Slot()
    def handle_open_hyd(self):
        if self.form_hyd is None:
            return

        if not self.form_hyd.isVisible():
            self.form_hyd.show()

    @Slot()
    def handle_open_power(self):
        if self.form_power is None:
            return

        if not self.form_power.isVisible():
            self.form_power.show()

    @Slot()
    def handle_open_plot(self):
        if self.form_plot is None:
            return

        if not self.form_plot.isVisible():
            self.form_plot.show()

    def pull_data_from_child(self):
        if self._data is None:
            self._data = {}

        if self.form_hyd is not None and self.form_hyd._data is not None:
            if "inputs_hydrodynamic" in self.form_hyd._data:
                self._data["inputs_hydrodynamic"] = self.form_hyd._data[
                    "inputs_hydrodynamic"
                ]

            if "hyd" in self.form_hyd._data:
                self._data["hyd"] = self.form_hyd._data["hyd"]

        if self.form_power is not None and self.form_power._data is not None:
            if "inputs_pm_fit" in self.form_power._data:
                self._data["inputs_pm_fit"] = self.form_power._data[
                    "inputs_pm_fit"
                ]

            if "p_fit" in self.form_power._data:
                self._data["p_fit"] = self.form_power._data["p_fit"]

    def save_choice(self):
        msgBox = QMessageBox()
        msgBox.setText("The project contains unsaved data.")
        msgBox.setInformativeText(
            "Do you want to save your changes before to close the project?"
        )
        msgBox.setStandardButtons(
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel
        )
        msgBox.setDefaultButton(QMessageBox.StandardButton.Save)
        ret = msgBox.exec_()
        return ret

    def load_project_choice(self):
        ret = self.save_choice()

        if ret == QMessageBox.StandardButton.Save:
            # should never be reached
            self.save_project()
            self.clear_project_data()
            self.load_project()
        elif ret == QMessageBox.StandardButton.Discard:
            self.clear_project_data()
            self.load_project()
        elif ret == QMessageBox.StandardButton.Cancel:
            print("No project has been loaded")
            pass
        else:
            print("No project has been loaded")
            pass

    def closeEvent(self, event):
        choice = QMessageBox.question(
            self,
            "Quit",
            "Do you want to exit the program?",
            QMessageBox.StandardButton.Yes,
            QMessageBox.StandardButton.No,
        )
        if choice == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def new_project_choice(self):
        ret = self.save_choice()

        if ret == QMessageBox.StandardButton.Save:
            # should never be reached
            if self._data is None:
                return

            prj_folder = self._data["prj_folder"]
            prj_fn = self._data["prj_filename"]
            project = os.path.join(prj_folder, prj_fn)
            h5i.save_dict_to_hdf5(self._data, project)
            self.gen_new_project()

        elif ret == QMessageBox.StandardButton.Discard:
            self.gen_new_project()

        elif ret == QMessageBox.StandardButton.Cancel:
            print("No new project has been generated")

        else:
            print("No new project has been generated")

    def task_save_hydrodynamic(self, data):
        if self._data is None:
            self._data = {}

        self._data["inputs_hydrodynamic"] = data
        self.save_project()

    def save_project(self):
        if self._data is None:
            return

        prj_folder = self._data["prj_folder"]
        prj_fn = self._data["prj_filename"]
        project = os.path.join(prj_folder, prj_fn)
        h5i.save_dict_to_hdf5(self._data, project)

    def task_end_pfit(self, data):
        assert self.form_plot is not None
        assert self.form_hyd is not None

        if self._data is None:
            self._data = {}

        self._data["p_fit"] = data
        self.save_project()
        self.form_plot.set_data(self._data)

        self.list_model.item(1).setForeground(QBrush(QColor(0, 150, 0)))
        self.list_model.item(2).setForeground(QBrush(QColor(0, 150, 0)))
        if (
            self.form_hyd._data["inputs_hydrodynamic"]["general_input"][
                "get_array_mat"
            ]
            == 1
        ):
            self.actionGenerate_array_hydrodynamic.setEnabled(True)

    def set_pfit_data(self, data):
        if self._data is None:
            self._data = {}

        self._data["inputs_pm_fit"] = data
        self.save_project()

    def set_wec_db_results(self, data):
        self._data = data
        self._data["inputs_pm_fit"]["data_folder"] = self._data[
            "inputs_hydrodynamic"
        ]["general_input"]["data_folder"]
        self.set_hydrodynamic_results(self._data["hyd"])

    def set_hydrodynamic_results(self, data):
        if self._data is None:
            self._data = {}

        self._data["hyd"] = data
        self.save_project()

        assert self.form_plot is not None
        assert self.form_power is not None

        self.form_plot.setEnabled(True)
        self.form_power.setEnabled(True)

        self.list_model.item(0).setForeground(QBrush(QColor(0, 150, 0)))
        self.list_model.item(1).setForeground(QBrush(QColor(0, 0, 150)))
        self.list_model.item(2).setForeground(QBrush(QColor(0, 0, 150)))
        self.form_plot.set_data(self._data)
        self.form_power.set_data(self._data)

    def run_entrance(self):
        self.entrance = Entrance()
        self.mdi_area.addSubWindow(self.entrance)
        self.entrance.show()
        self.entrance.btn_load.clicked.connect(self.load_project)
        self.entrance.btn_new.clicked.connect(self.gen_new_project)

    def clear_project_data(self):
        if self._data is not None:
            self.list_model.item(0).setForeground(QBrush(QColor(0, 0, 150)))
            self.list_model.item(1).setForeground(QBrush(QColor(0, 0, 0)))
            self.list_model.item(2).setForeground(QBrush(QColor(0, 0, 0)))

        self._data = None

    def set_forms_data(self):
        if self.form_hyd is None or self._data is None:
            return

        self.form_hyd.set_data(self._data)

        # self.form_power.set_data(self._data)
        # self.form_plot.set_data(self._data)

    def load_project(self):
        self.mdi_area.closeAllSubWindows()
        self.clear_project_data()
        project_folder = QFileDialog.getExistingDirectory(
            self, "Select a project folder"
        )
        project_folder = str(project_folder)
        prj_name = os.path.basename(os.path.normpath(project_folder))
        prj_filename = "".join([prj_name, "_data_collection.hdf5"])
        project = os.path.join(project_folder, prj_filename)

        if os.path.isfile(project):
            dictionary = h5i.load_dict_from_hdf5(project)
            dictionary["prj_folder"] = project_folder
            dictionary["prj_filename"] = prj_filename
            dictionary["prj_name"] = prj_name
            self._data = dictionary
            self.populate_project()
        else:
            choice = QMessageBox().question(
                self,
                "Wrong Project Folder",
                "The selected folder does not contains a valid project data collection.\n Do you want to select another folder?",
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No,
            )
            if choice == QMessageBox.StandardButton.Yes:
                self.load_project()
            else:
                return -1

    def populate_project(self):
        if self._data is None:
            return

        prj_id = self._data["inputs_hydrodynamic"]["general_input"][
            "input_type"
        ]
        if prj_id == 1:
            self.create_project(1)
        elif prj_id == 2:
            self.create_project(2)
        elif prj_id == 3:
            self.create_project(3)
        elif prj_id == 4:
            self.create_project(4)
        else:
            print("Input type not understood")

        # self.form_hyd.populate_prj()

    def gen_new_project(self):
        self.mdi_area.closeAllSubWindows()
        self.clear_project_data()
        self.new_project = NewProject(self)
        self.mdi_area.addSubWindow(self.new_project)
        self.new_project.show()

        self.new_project.btn_t1.clicked.connect(lambda: self.create_project(1))
        self.new_project.btn_t2.clicked.connect(lambda: self.create_project(2))
        self.new_project.btn_t3.clicked.connect(lambda: self.create_project(3))
        self.new_project.btn_t4.clicked.connect(lambda: self.create_project(4))
        self.new_project.btn_prj.clicked.connect(self.browse_prj)
        self.actionGenerate_array_hydrodynamic.setDisabled(True)

    def browse_prj(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select a project folder"
        )
        folder = str(folder)
        prj_name = os.path.basename(os.path.normpath(folder))
        if os.path.isdir(folder):
            if os.listdir(folder):
                msgBox = QMessageBox()
                msgBox.setText(
                    "The project folder is not empty \n Select another folder or clear the actual folder?"
                )
                select_button = msgBox.addButton(
                    "Select",
                    QMessageBox.ButtonRole.YesRole,
                )
                clear_button = msgBox.addButton(
                    "Clear",
                    QMessageBox.ButtonRole.NoRole,
                )
                msgBox.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

                self._test_dialog = msgBox
                msgBox.exec()
                self._test_dialog = None

                if msgBox.clickedButton() == select_button:
                    self.browse_prj()
                elif msgBox.clickedButton() == clear_button:
                    try:
                        clean_prj_folder(folder)
                    except:
                        return -1
                else:
                    return -1
        else:
            return -1

        self.new_project.le_prj.setText(folder)
        self._data = h5i.create_empty_project(folder, prj_name)

    def populate_listview(self):
        self.lw_area.show()
        model = QStandardItemModel()
        ls_item = [
            "Hydrodynamic",  # Must be store-bought
            "Performance Fit",  # Must be homemade
            "Data Visualisation",  # Must be saucy
        ]

        for it in ls_item:
            # Create an item with a caption
            item = QStandardItem(it)
            # Add a checkbox to it
            item.setCheckable(False)
            item.setEditable(False)
            item.setForeground(QBrush(QColor(0, 0, 0)))
            # Add the item to the model
            model.appendRow(item)

        model.item(0).setForeground(QBrush(QColor(0, 0, 150)))
        self.lw_area.setModel(model)
        self.list_model = model
        self.lw_area_selection_model = self.lw_area.selectionModel()
        self.lw_area_selection_model.selectionChanged.connect(
            self.handle_list_selection
        )

    @Slot(QItemSelection, QItemSelection)  # type: ignore
    def handle_list_selection(
        self,
        selected: QItemSelection,
        deselected: QItemSelection,
    ):
        index = selected.indexes()[0]
        print(
            "selected item index found at %s with data: %s"
            % (index.row(), index.data())
        )
        if index.data() == "Hydrodynamic":
            if self.form_hyd is None:
                return

            if not self.form_hyd.isVisible():
                self.form_hyd.show()

        elif index.data() == "Performance Fit":
            if self.form_power is None:
                return

            if not self.form_power.isVisible():
                self.form_power.show()

        elif index.data() == "Data Visualisation":
            if self.form_plot is None:
                return

            if not self.form_plot.isVisible():
                self.form_plot.show()

        else:
            pass

    def set_full_project(self):
        self.form_plot = Plotter(self)
        self.form_power = PowerPerformance(self)

        sub_window = QMdiSubWindow(self.mdi_area)
        sub_window.setWidget(self.form_power)
        sub_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        sub_window.show()
        self.sub_power = sub_window

        sub_window = QMdiSubWindow(self.mdi_area)
        sub_window.setWidget(self.form_plot)
        sub_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        sub_window.show()
        self.sub_plot = sub_window

        self.form_plot.setEnabled(False)
        self.form_power.setEnabled(False)

    def create_project(self, prj_id):
        if self._data is None:
            self.new_project.le_prj.setStyleSheet(
                "QLineEdit {border: 1px solid red}"
            )
        else:
            self.mdi_area.closeActiveSubWindow()
            self.populate_listview()
            self.set_full_project()

            if prj_id == 1:
                self.form_hyd = ReadDb(self)
            elif prj_id == 2:
                self.form_hyd = RunNemoh(self)
            elif prj_id == 3:
                self.form_hyd = ReadNemoh(self)
            elif prj_id == 4:
                self.form_hyd = ReadWamit(self)
            else:
                raise RuntimeError("Input type not understood")

            sub_window = QMdiSubWindow(self.mdi_area)
            sub_window.setWidget(self.form_hyd)
            sub_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
            sub_window.show()
            self.sub_hyd = sub_window

            self.mdi_area.tileSubWindows()
            self.actionSave_Project.setEnabled(True)
            self.set_forms_data()

    @Slot()
    def save_dtocean_format(self):
        status = final_data_check(self._data)
        if status[0]:
            assert self._data is not None
            x = self._data["hyd"]
            y = self._data["p_fit"]

            data2dtocean = dict(
                list(x.items())
                + list(y.items())
                + [(k, x[k] + y[k]) for k in set(x) & set(y)]
            )
            # update_wec_power_matrix(data2dtocean)
            h5i.save_dict_to_hdf5(
                data2dtocean,
                os.path.join(self._data["prj_folder"], "wec_solution.h5"),
            )
        else:
            assert len(status) == 2
            print("The following fields are missing from the data attribute")
            print(" , \n".join(status[1]))


def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
