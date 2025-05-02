# -*- coding: utf-8 -*-

#    Copyright (C) 2019-2025 Mathew Topper
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

# pylint: disable=protected-access

import logging
import multiprocessing
import os
import re
import sys
import threading
import traceback
import types
from copy import deepcopy
from functools import partial
from typing import TYPE_CHECKING, Any, Optional

import matplotlib as mpl
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dtocean_core.pipeline import Tree
from dtocean_plugins.strategies.position import AdvancedPosition
from dtocean_plugins.strategies.position_optimiser import (
    _load_config_template,
    dump_config,
)
from dtocean_qt.pandas.models.DataFrameModel import DataFrameModel
from mdo_engine.utilities.misc import OrderedSet
from PIL import Image
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt
from shiboken6 import Shiboken

from ..utils.display import is_high_dpi
from ..widgets.datatable import DataTableWidget
from ..widgets.dialogs import ProgressBar
from ..widgets.display import (
    MPLWidget,
    get_current_figure_size,
    get_current_filetypes,
)
from ..widgets.extendedcombobox import ExtendedComboBox
from ..widgets.scientificselect import ScientificDoubleSpinBox
from . import GUIStrategy, PyQtABCMeta, StrategyWidget

if is_high_dpi() or TYPE_CHECKING:
    from ..designer.high.advancedposition import Ui_AdvancedPositionWidget
else:
    from ..designer.low.advancedposition import Ui_AdvancedPositionWidget


# Set up logging
module_logger = logging.getLogger(__name__)

# User home directory
HOME = os.path.expanduser("~")

# Check if running coverage
RUNNING_COVERAGE = "coverage" in sys.modules

TITLE_MAP = {
    "sim_number": "Simulation #",
    "grid_orientation": "Grid Orientation",
    "delta_row": "Row Spacing",
    "delta_col": "Column Spacing",
    "n_nodes": "No. of Devices Requested",
    "n_evals": "No. of Evaluations",
    "project.capex_breakdown": "CAPEX",
}
UNIT_MAP = {
    "grid_orientation": "Deg",
    "delta_row": "m",
    "delta_col": "m",
    "project.capex_breakdown": "Euro",
}


class ThreadLoadSimulations(QtCore.QThread):
    """QThread for loading simulations"""

    taskFinished = QtCore.Signal()
    error_detected = QtCore.Signal(object, object, object)

    def __init__(self, shell, sim_numbers, remove_simulations, exclude_default):
        super(ThreadLoadSimulations, self).__init__()
        self._shell = shell
        self._sim_numbers = sim_numbers
        self._remove_simulations = remove_simulations
        self._exclude_default = exclude_default

    def run(self):  # pragma: no cover
        if RUNNING_COVERAGE:
            sys.settrace(threading.gettrace())

        self._run()

    def _run(self):
        try:
            # Block signals
            self._shell.core.blockSignals(True)
            self._shell.project.blockSignals(True)

            if self._remove_simulations:
                self._shell.strategy.remove_simulations(
                    self._shell.core,
                    self._shell.project,
                    exclude_default=self._exclude_default,
                )

            self._shell.strategy.load_simulation_ids(
                self._shell.core, self._shell.project, self._sim_numbers
            )

        except Exception:
            etype, evalue, etraceback = sys.exc_info()
            self.error_detected.emit(etype, evalue, etraceback)
        finally:
            # Reinstate signals and emit
            self._shell.core.blockSignals(False)
            self._shell.project.blockSignals(False)
            self.taskFinished.emit()


class GUIAdvancedPosition(GUIStrategy, AdvancedPosition, metaclass=PyQtABCMeta):
    """GUI for AdvancedPosition strategy."""

    def __init__(self):
        AdvancedPosition.__init__(self)
        GUIStrategy.__init__(self)

    def allow_run(self, core, project):
        if self._config is None:
            return False
        return AdvancedPosition.allow_run(core, project, self._config)

    def get_weight(self):
        """A method for getting the order of priority of the strategy.

        Returns:
          int
        """

        return 4

    def get_widget(self, parent, shell):
        config = _load_config_template()
        widget = AdvancedPositionWidget(parent, shell, config)

        return widget


class AdvancedPositionWidget(
    QtWidgets.QWidget,
    Ui_AdvancedPositionWidget,
    StrategyWidget,
):
    config_set = QtCore.Signal()
    config_null = QtCore.Signal()
    reset = QtCore.Signal()

    def __init__(self, parent, shell, config: dict[str, Any]):
        QtWidgets.QWidget.__init__(self, parent)
        Ui_AdvancedPositionWidget.__init__(self)
        StrategyWidget.__init__(self)

        self._shell = shell
        self._config = _init_config(config)
        self._max_threads = multiprocessing.cpu_count()
        self._progress: ProgressBar
        self._results_df: Optional[pd.DataFrame] = None
        self._delete_sims = True
        self._protect_default = True
        self._sims_to_load = None
        self._load_sims_thread = None
        self._param_boxes = {}
        self._param_lines = []
        self._worker_dir_status_code = None
        self._optimiser_status_code = None
        self._cost_var_box_to_var_id_map: Optional[dict[int, str]] = None
        self._var_id_to_title_map: dict[str, str]
        self._var_id_to_unit_map: dict[str, str]
        self._var_id_to_cost_var_box_map: dict[str, int]

        self._default_base_penalty = 1.0
        self._default_tolerance = 1e-11
        self._default_n_threads = 1
        self._default_min_evals = 1
        self._default_max_evals = 128
        self._default_popsize = 1
        self._default_max_resamples_algorithm = 1
        self._default_max_resamples = 2

        self.plotWidget = None
        self._init_ui(parent)

    def _init_ui(self, parent):
        ## INIT

        self.setupUi(self)

        ## CONTROL TAB

        # Signals

        self.importConfigButton.clicked.connect(self._import_config)
        self.exportConfigButton.clicked.connect(self._export_config)
        self.workDirLineEdit.returnPressed.connect(self._update_worker_dir)
        self.workDirLineEdit.editingFinished.connect(self._reset_worker_dir)
        self.workDirToolButton.clicked.connect(self._select_worker_dir)
        self.cleanDirCheckBox.stateChanged.connect(
            self._update_clean_existing_dir
        )

        ## SETTINGS TAB

        self.tabWidget.setTabEnabled(1, False)

        self.costVarBox = _init_extended_combo_box(self, "costVarBox")
        self.costVarLayout.addWidget(self.costVarBox)

        self.penaltySpinBox = _init_sci_spin_box(self, "penaltySpinBox")
        self.penaltyLayout.addWidget(self.penaltySpinBox)
        self.penaltySpinBox.setValue(self._default_base_penalty)
        self.penaltyUnitsLabel.clear()

        self.toleranceSpinBox = _init_sci_spin_box(self, "toleranceSpinBox")
        self.toleranceLayout.addWidget(self.toleranceSpinBox)
        self.toleranceSpinBox.setValue(self._default_tolerance)
        self.toleranceUnitsLabel.clear()

        self.nThreadSpinBox.setMaximum(self._max_threads)

        self._init_variables()
        self._init_manual_thread_message()

        # Signals

        self.costVarBox.currentIndexChanged.connect(self._update_objective)
        self.costVarCheckBox.stateChanged.connect(self._update_maximise)
        self.penaltySpinBox.valueChanged.connect(self._update_base_penalty)
        self.toleranceSpinBox.valueChanged.connect(self._update_tolerance)
        self.nThreadSpinBox.valueChanged.connect(self._update_n_threads)
        self.abortXSpinBox.valueChanged.connect(self._update_max_simulations)
        self.abortTimeSpinBox.valueChanged.connect(self._update_max_time)
        self.minNoiseCheckBox.stateChanged.connect(self._update_min_noise_auto)
        self.minNoiseSpinBox.valueChanged.connect(self._update_min_noise)
        self.maxNoiseSpinBox.valueChanged.connect(self._update_max_noise)
        self.populationCheckBox.stateChanged.connect(
            self._update_population_auto
        )
        self.populationSpinBox.valueChanged.connect(self._update_population)
        self.maxResamplesComboBox.currentIndexChanged.connect(
            self._update_max_resamples_algorithm
        )
        self.maxResamplesSpinBox.valueChanged.connect(
            self._update_max_resamples
        )

        ## PARAMS TAB

        self.tabWidget.setTabEnabled(2, False)

        param_names = [
            "grid_orientation",
            "delta_row",
            "delta_col",
            "n_nodes",
            "t1",
            "t2",
        ]

        param_box_classes = {
            "grid_orientation": QtWidgets.QDoubleSpinBox,
            "delta_row": QtWidgets.QDoubleSpinBox,
            "delta_col": QtWidgets.QDoubleSpinBox,
            "n_nodes": QtWidgets.QSpinBox,
            "t1": QtWidgets.QDoubleSpinBox,
            "t2": QtWidgets.QDoubleSpinBox,
        }

        param_box_types = {
            "grid_orientation": float,
            "delta_row": float,
            "delta_col": float,
            "n_nodes": int,
            "t1": float,
            "t2": float,
        }

        param_multipier_vars = {
            "delta_row": ["device.minimum_distance_x"],
            "delta_col": ["device.minimum_distance_y"],
        }

        param_limits_dict = {
            "grid_orientation": (-90, 90),
            "delta_row": (0, None),
            "delta_col": (0, None),
            "n_nodes": (0, None),
            "t1": (0, 1),
            "t2": (0, 1),
        }

        for i, param_name in enumerate(param_names):
            if param_name in TITLE_MAP:
                group_title = TITLE_MAP[param_name]
            else:
                group_title = param_name

            if param_name in UNIT_MAP:
                group_title += " ({})".format(UNIT_MAP[param_name])

            box_class = param_box_classes[param_name]
            var_box = _make_var_box(
                self, self.paramsFrame, param_name, group_title, box_class
            )
            self.paramsFrameLayout.addWidget(var_box["root"])

            box_minimum = -sys.maxsize
            box_maximum = sys.maxsize
            set_box_min = False
            set_box_max = False
            param_limits = None

            if param_name in param_limits_dict:
                param_limits = param_limits_dict[param_name]

                if param_limits[0] is not None:
                    box_minimum = param_limits[0]
                    set_box_min = True

                if param_limits[1] is not None:
                    box_maximum = param_limits[1]
                    set_box_max = True

            var_box["fixed.box"].setMinimum(box_minimum)
            var_box["fixed.box"].setMaximum(box_maximum)

            var_box["range.box.min"].setMinimum(box_minimum)
            var_box["range.box.min"].setMaximum(box_maximum)
            if set_box_min:
                var_box["range.box.min"].setValue(box_minimum)

            var_box["range.box.max"].setMinimum(box_minimum)
            var_box["range.box.max"].setMaximum(box_maximum)
            if set_box_max:
                var_box["range.box.max"].setValue(box_maximum)

            var_box["range.box.type"].addItem("Fixed")
            var_box["range.box.var"].setEnabled(False)

            if param_name in param_multipier_vars:
                var_box["range.box.type"].addItem("Multiplier")

                for var in param_multipier_vars[param_name]:
                    if var not in self._var_id_to_title_map:
                        continue
                    mapped_name = self._var_id_to_title_map[var]
                    var_box["range.box.var"].addItem(mapped_name)

            # Slots
            param_type = param_box_types[param_name]

            fixed_combo_slot = _make_fixed_combo_slot(
                self, param_name, param_type, self._var_id_to_title_map
            )

            attr_name = "fixed_combo_slot_{}".format(i)
            setattr(self, attr_name, fixed_combo_slot)

            var_box["fixed.check"].stateChanged.connect(
                getattr(self, attr_name)
            )

            fixed_value_slot = _make_fixed_value_slot(
                self, param_name, param_type
            )

            attr_name = "fixed_value_slot_{}".format(i)
            setattr(self, attr_name, fixed_value_slot)

            var_box["fixed.box"].valueChanged.connect(getattr(self, attr_name))

            range_type_slot = _make_range_type_slot(
                self, param_name, param_type, self._var_id_to_title_map
            )

            attr_name = "range_type_slot_{}".format(i)
            setattr(self, attr_name, range_type_slot)

            var_box["range.box.type"].currentIndexChanged[str].connect(
                getattr(self, attr_name)
            )

            generic_range_slot = _make_generic_range_slot(
                self, param_name, param_type, self._var_id_to_title_map
            )

            attr_name = "generic_range_slot_{}".format(i)
            setattr(self, attr_name, generic_range_slot)

            var_box["range.box.var"].currentIndexChanged.connect(
                getattr(self, attr_name)
            )
            var_box["range.box.min"].valueChanged.connect(
                getattr(self, attr_name)
            )
            var_box["range.box.max"].valueChanged.connect(
                getattr(self, attr_name)
            )

            self._param_boxes[param_name] = var_box

            if i != len(param_names) - 1:
                line_name = "{} Line".format(param_name)
                line = QtWidgets.QFrame(self.paramsFrame)
                line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
                line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
                line.setObjectName(line_name)
                self.paramsFrameLayout.addWidget(line)

                self._param_lines.append(line)

        final_spacer = QtWidgets.QSpacerItem(
            20,
            20,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.paramsFrameLayout.addItem(final_spacer)

        ## RESULTS TAB

        self.tabWidget.setTabEnabled(3, False)

        self.simButtonGroup.setId(self.bestSimButton, 1)
        self.simButtonGroup.setId(self.worstSimButton, 2)
        self.simButtonGroup.setId(self.top5SimButton, 3)
        self.simButtonGroup.setId(self.bottom5SimButton, 4)
        self.simButtonGroup.setId(self.customSimButton, 5)

        # Data table

        self.dataTableWidget = DataTableWidget(
            self, edit_rows=False, edit_cols=False, edit_cells=False
        )

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        self.dataTableWidget.setSizePolicy(sizePolicy)
        self.dataTableWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.dataTableLayout.addWidget(self.dataTableWidget)

        # Signals

        self.deleteSimsBox.stateChanged.connect(self._update_delete_sims)
        self.protectDefaultBox.stateChanged.connect(
            self._update_protect_default
        )

        ## PLOTS TAB

        self.tabWidget.setTabEnabled(4, False)

        # Add spin boxes

        self.xAxisMinSpinBox = _init_sci_spin_box(self, "xAxisMinSpinBox")
        self.xAxisMinLayout.addWidget(self.xAxisMinSpinBox)
        self.xAxisMaxSpinBox = _init_sci_spin_box(self, "xAxisMaxSpinBox")
        self.xAxisMaxLayout.addWidget(self.xAxisMaxSpinBox)

        self.yAxisMinSpinBox = _init_sci_spin_box(self, "yAxisMinSpinBox")
        self.yAxisMinLayout.addWidget(self.yAxisMinSpinBox)
        self.yAxisMaxSpinBox = _init_sci_spin_box(self, "yAxisMaxSpinBox")
        self.yAxisMaxLayout.addWidget(self.yAxisMaxSpinBox)

        self.colorAxisMinSpinBox = _init_sci_spin_box(
            self, "colorAxisMinSpinBox"
        )
        self.colorAxisMinLayout.addWidget(self.colorAxisMinSpinBox)
        self.colorAxisMaxSpinBox = _init_sci_spin_box(
            self, "colorAxisMaxSpinBox"
        )
        self.colorAxisMaxLayout.addWidget(self.colorAxisMaxSpinBox)

        self.filterVarMinSpinBox = _init_sci_spin_box(
            self, "filterVarMinSpinBox"
        )
        self.filterVarMinLayout.addWidget(self.filterVarMinSpinBox)
        self.filterVarMaxSpinBox = _init_sci_spin_box(
            self, "filterVarMaxSpinBox"
        )
        self.filterVarMaxLayout.addWidget(self.filterVarMaxSpinBox)

        # Add plot widget holder
        self.plotWidget = None

        # Signals

        self.simButtonGroup.buttonClicked["int"].connect(
            self._select_sims_to_load
        )
        self.simSelectEdit.textEdited.connect(self._update_custom_sims)
        self.simLoadButton.clicked.connect(self._progress_load_sims)
        self.dataExportButton.clicked.connect(self._export_data_table)
        self.plotButton.clicked.connect(self._set_plot)
        self.plotExportButton.clicked.connect(self._get_export_details)

        ## DEBUG TAB

        # Signals

        self.importYAMLButton.clicked.connect(self._import_yaml)

        ## GLOBAL

        # Set up progress bar
        self._progress = ProgressBar(parent)
        self._progress.setModal(True)

        # Signals

        self._shell.project.sims_updated.connect(self._update_status)
        self._shell.strategy_selected.connect(self._update_status)
        self.destroyed.connect(
            partial(AdvancedPositionWidget._on_destroyed, self.plotWidget)
        )

        self._update_status(init=True)

    def _init_variables(self):
        self.costVarBox.clear()

        active_modules = self._shell.module_menu.get_active(
            self._shell.core, self._shell.project
        )
        active_themes = self._shell.theme_menu.get_active(
            self._shell.core, self._shell.project
        )
        active_interfaces = active_modules + active_themes

        if not active_interfaces:
            return

        if self._cost_var_box_to_var_id_map is None:
            cost_var_box_to_id_map = {}
            var_id_to_cost_var_box_map = {}
            var_id_to_title_map = deepcopy(TITLE_MAP)
            var_id_to_unit_map = deepcopy(UNIT_MAP)
        else:
            cost_var_box_to_id_map = self._cost_var_box_to_var_id_map
            var_id_to_cost_var_box_map = self._var_id_to_cost_var_box_map
            var_id_to_title_map = self._var_id_to_title_map
            var_id_to_unit_map = self._var_id_to_unit_map

        var_names = []
        tree = Tree()
        box_number = 0

        for interface_name in active_interfaces:
            branch = tree.get_branch(
                self._shell.core, self._shell.project, interface_name
            )

            var_inputs = branch.get_inputs(
                self._shell.core, self._shell.project
            )
            var_outputs = branch.get_outputs(
                self._shell.core, self._shell.project
            )

            unique_vars = OrderedSet(var_inputs + var_outputs)

            for var_id in unique_vars:
                var_meta = self._shell.core.get_metadata(var_id)

                if "SimpleData" not in var_meta.structure:
                    continue

                if var_meta.types is None:
                    errStr = (
                        "Variable {} with SimpleData structure requires "
                        "types meta data to be set"
                    ).format(var_id)
                    raise ValueError(errStr)

                var_type = var_meta.types[0]

                if var_type not in ["float", "int"]:
                    continue

                title = var_meta.title
                var_id_to_title_map[var_id] = title

                if var_meta.units is not None:
                    unit = var_meta.units[0]
                    title = "{} ({})".format(title, unit)
                    var_id_to_unit_map[var_id] = unit

                if var_id not in var_outputs or var_type == "int":
                    continue

                # Collect data for costVarBox
                var_names.append(title)
                cost_var_box_to_id_map[box_number] = var_id
                var_id_to_cost_var_box_map[var_id] = box_number
                box_number += 1

        self._var_id_to_title_map = var_id_to_title_map
        self._var_id_to_unit_map = var_id_to_unit_map
        self._cost_var_box_to_var_id_map = cost_var_box_to_id_map
        self._var_id_to_cost_var_box_map = var_id_to_cost_var_box_map
        self.costVarBox.addItems(var_names)
        self.costVarBox.setCurrentIndex(-1)

    def _init_manual_thread_message(self):
        thread_msg = "({} threads available)".format(self._max_threads)
        self.threadInfoLabel.setText(thread_msg)

    def _init_tab_control(self):
        if self._config["worker_dir"] is None:
            self.workDirLineEdit.clear()
        else:
            self.workDirLineEdit.setText(self._config["worker_dir"])

        if self._config["clean_existing_dir"] is not None:
            if self._config["clean_existing_dir"]:
                # I'm not sure if this can ever be triggered
                if not self.cleanDirCheckBox.isChecked():
                    self.cleanDirCheckBox.toggle()

            else:
                if self.cleanDirCheckBox.isChecked():
                    self.cleanDirCheckBox.toggle()

    def _init_tab_settings(self):
        if (
            self._config["objective"] is not None
            and self._config["objective"] in self._var_id_to_cost_var_box_map
        ):
            box_number = self._var_id_to_cost_var_box_map[
                self._config["objective"]
            ]
            self.costVarBox.setCurrentIndex(box_number)
        else:
            self.costVarBox.setCurrentIndex(-1)

        if self._config["maximise"] is None:
            self.costVarCheckBox.setChecked(False)
        else:
            self.costVarCheckBox.setChecked(self._config["maximise"])

        if self._config["base_penalty"] is None:
            self.penaltySpinBox.setValue(self._default_base_penalty)
        else:
            self.penaltySpinBox.setValue(self._config["base_penalty"])

        if self._config["tolfun"] is None:
            self.toleranceSpinBox.setValue(self._default_tolerance)
        else:
            self.toleranceSpinBox.setValue(self._config["tolfun"])

        if self._config["n_threads"] is None:
            self.nThreadSpinBox.setValue(self._default_n_threads)
        else:
            self.nThreadSpinBox.setValue(self._config["n_threads"])

        if self._config["max_simulations"] is None:
            self.abortXSpinBox.setValue(0)
        else:
            self.abortXSpinBox.setValue(self._config["max_simulations"])

        if self._config["timeout"] is None:
            self.abortTimeSpinBox.setValue(0)
        else:
            self.abortTimeSpinBox.setValue(self._config["timeout"])

        if self._config["min_evals"] is None:
            self.minNoiseCheckBox.setChecked(True)
        else:
            self.minNoiseSpinBox.setValue(self._config["min_evals"])
            self.minNoiseCheckBox.setChecked(False)

        if self._config["max_evals"] is None:
            self.maxNoiseSpinBox.setValue(self._default_max_evals)
        else:
            self.maxNoiseSpinBox.setValue(self._config["max_evals"])

        if self._config["popsize"] is None:
            self.populationCheckBox.setChecked(True)
        else:
            self.populationSpinBox.setValue(self._config["popsize"])
            self.populationCheckBox.setChecked(False)

        if self._config["max_resample_factor"] is None:
            self.maxResamplesComboBox.setCurrentIndex(
                self._default_max_resamples_algorithm
            )
            self.maxResamplesSpinBox.setValue(self._default_max_resamples)

        else:
            # Check for use of auto setting
            auto_match = re.match(
                r"auto([0-9]+)", str(self._config["max_resample_factor"]), re.I
            )

            if auto_match:
                items = auto_match.groups()
                auto_resample_iterations = int(items[0])
                self.maxResamplesComboBox.setCurrentIndex(1)
                self.maxResamplesSpinBox.setValue(auto_resample_iterations)
            else:
                max_resample_factor = self._config["max_resample_factor"]
                self.maxResamplesComboBox.setCurrentIndex(0)
                self.maxResamplesSpinBox.setValue(max_resample_factor)

    def _init_tab_parameters(self):
        parameters = self._config["parameters"]

        for param_name in parameters:
            if param_name not in self._param_boxes:
                continue

            param_settings = parameters[param_name]
            var_box = self._param_boxes[param_name]

            if "fixed" in param_settings and param_settings["fixed"]:
                var_box["fixed.check"].setChecked(True)
                var_box["fixed.box"].setValue(param_settings["fixed"])
                var_box["range.group"].setEnabled(False)

                continue

            if "range" in param_settings and param_settings["range"]:
                range_settings = param_settings["range"]

                if (
                    range_settings["type"] == "multiplier"
                    and range_settings["variable"]
                    not in self._var_id_to_title_map
                ):
                    continue

                var_box["fixed.check"].setChecked(False)
                var_box["range.group"].setEnabled(True)

                if range_settings["type"] == "multiplier":
                    var_box["range.box.type"].setCurrentIndex(1)

                    range_var_text = self._var_id_to_title_map[
                        range_settings["variable"]
                    ]
                    multi_var_idx = var_box["range.box.var"].findText(
                        range_var_text
                    )
                    var_box["range.box.var"].setCurrentIndex(multi_var_idx)
                    var_box["range.box.var"].setEnabled(True)

                    min_range = range_settings["min_multiplier"]
                    max_range = range_settings["max_multiplier"]

                elif range_settings["type"] == "fixed":
                    var_box["range.box.type"].setCurrentIndex(0)
                    var_box["range.box.var"].setCurrentIndex(0)
                    var_box["range.box.var"].setDisabled(True)

                    min_range = range_settings["min"]
                    max_range = range_settings["max"]

                else:
                    err_str = ("Unrecognised range type " "'{}'").format(
                        range_settings["type"]
                    )
                    raise ValueError(err_str)

                var_box["range.box.min"].setValue(min_range)
                var_box["range.box.max"].setValue(max_range)

    @QtCore.Slot()
    def _update_status(self, init=False, update_results=True):
        # Pick up the current tab to reload after update
        current_tab_idx = self.tabWidget.currentIndex()

        init |= self._update_status_control()
        assert self._worker_dir_status_code is not None

        if init:
            self._init_tab_control()
            self._init_tab_settings()
            self._init_tab_parameters()

        if self._worker_dir_status_code >= 1:
            self.tabWidget.setTabEnabled(1, True)
            self.tabWidget.setTabEnabled(2, True)
            self.tabWidget.setTabEnabled(3, False)
            self.tabWidget.setTabEnabled(4, False)
            self.settingsFrame.setEnabled(True)
            self.paramsFrame.setEnabled(True)
        else:
            self.tabWidget.setTabEnabled(1, False)
            self.tabWidget.setTabEnabled(2, False)
            self.tabWidget.setTabEnabled(3, False)
            self.tabWidget.setTabEnabled(4, False)

        if not update_results:
            self.tabWidget.setCurrentIndex(current_tab_idx)
            return

        if self._optimiser_status_code == 1:
            self.tabWidget.setTabEnabled(1, True)
            self.tabWidget.setTabEnabled(2, True)
            self.tabWidget.setTabEnabled(3, True)
            self.tabWidget.setTabEnabled(4, True)
            self.settingsFrame.setEnabled(False)
            self.paramsFrame.setEnabled(False)

            self._update_status_results()
            self._update_status_plots()

        elif self._optimiser_status_code == 2:
            self.tabWidget.setTabEnabled(1, True)
            self.tabWidget.setTabEnabled(2, True)
            self.tabWidget.setTabEnabled(3, False)
            self.tabWidget.setTabEnabled(4, False)
            self.settingsFrame.setEnabled(False)
            self.paramsFrame.setEnabled(False)

        self.tabWidget.setCurrentIndex(current_tab_idx)

    def _update_status_control(self):
        # True if the widget should be initialised
        init = False

        color_map = {0: "#aa0000", 1: "#00aa00", 2: "#ff8100"}

        (project_status_str, project_status_code) = (
            GUIAdvancedPosition.get_project_status(
                self._shell.core, self._shell.project, self._config
            )
        )
        project_status_strs = project_status_str.split("\n")

        (config_status_str, config_status_code) = (
            GUIAdvancedPosition.get_config_status(self._config)
        )

        optimiser_status_str = None
        optimiser_status_code = 0
        old_config = None

        if self._config["worker_dir"] is not None:
            (worker_dir_status_str, worker_dir_status_code) = (
                GUIAdvancedPosition.get_worker_directory_status(self._config)
            )

            if worker_dir_status_code == 0:
                (optimiser_status_str, optimiser_status_code) = (
                    GUIAdvancedPosition.get_optimiser_status(
                        self._shell.core, self._config
                    )
                )

                if optimiser_status_code >= 1:
                    # Pick up the old config
                    old_config_path = os.path.join(
                        self._config["worker_dir"],
                        GUIAdvancedPosition.get_config_fname(),
                    )
                    old_config = GUIAdvancedPosition.load_config(
                        old_config_path
                    )
                    old_config.pop("clean_existing_dir")

        else:
            worker_dir_status_str = "No worker directory set"
            worker_dir_status_code = 0

        self._worker_dir_status_code = worker_dir_status_code
        self._optimiser_status_code = optimiser_status_code

        # Replace the config with the saved version if the optimiser status
        # is completed or available for restart.
        has_stored_config = (
            self._shell.strategy is not None
            and self._shell.strategy.get_config() is not None
        )

        if optimiser_status_code >= 1:
            assert old_config is not None
            if has_stored_config:
                shell_config = self._shell.strategy.get_config()
                old_config["clean_existing_dir"] = shell_config[
                    "clean_existing_dir"
                ]
            self._config = _init_config(old_config)
            init = True

        # Determine if the configuration has changed against the config
        # in the active strategy
        copy_shell_config = None
        config_keys = self._config.keys()

        if has_stored_config:
            shell_config = self._shell.strategy.get_config()
            copy_shell_config = {}

            for key in config_keys:
                if key in shell_config:
                    copy_shell_config[key] = shell_config[key]

            if (
                "clean_existing_dir" in copy_shell_config
                and copy_shell_config["clean_existing_dir"] is None
            ):
                copy_shell_config["clean_existing_dir"] = False

        # Debug why configs don't match
        #        if copy_shell_config is not None:
        #            a = copy_shell_config
        #            b = self._config
        #            print set(a).symmetric_difference(set(b))
        #            print [(k, a[k], b[k]) for k in a if k in b and a[k]!=b[k]]

        # Test if configuration is new or modified
        cnom = (copy_shell_config is None) or (
            copy_shell_config is not None and copy_shell_config != self._config
        )

        #        print "c: {} p: {} w: {} o: {} cnom: {}".format(
        #            config_status_code,
        #            project_status_code,
        #            worker_dir_status_code,
        #            optimiser_status_code,
        #            cnom)

        # Start writing status and check if apply button enabled
        status_template = '<li style="color: {};">{}</li>'
        status_str = ""
        enable_apply = False

        if optimiser_status_code == 0:
            if config_status_code == 0:
                status_str += status_template.format(
                    color_map[config_status_code], config_status_str
                )

            if worker_dir_status_code == 0:
                status_str += status_template.format(
                    color_map[worker_dir_status_code], worker_dir_status_str
                )

            else:
                if worker_dir_status_str is not None:
                    status_str += status_template.format(
                        color_map[worker_dir_status_code], worker_dir_status_str
                    )

                for project_status_str in project_status_strs:
                    status_str += status_template.format(
                        color_map[project_status_code], project_status_str
                    )

        else:
            status_str += status_template.format(
                color_map[optimiser_status_code], optimiser_status_str
            )

        if (
            not (optimiser_status_code == 0 and config_status_code == 0)
            and cnom
        ):
            status_str += status_template.format(
                color_map[2], "Configuration modified"
            )
            enable_apply = True

        status_str_rich = (
            "<html><head/><body><p><span "
            'style="font-size: 10pt;">'
            "<ul>{}</ul>"
            "</span></p></body></html>"
        ).format(status_str)

        self.statusLabel.setText(status_str_rich)

        # Signals for apply button
        if enable_apply:
            self.config_set.emit()
        else:
            self.config_null.emit()

        return init

    @QtCore.Slot()
    def _import_config(self):
        msg = "Import Configuration"
        valid_exts = "Configuration files (*.yaml *.yml)"

        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            msg,
            HOME,
            valid_exts,
        )

        if not file_path:
            return

        config = GUIAdvancedPosition.load_config(str(file_path))
        self._config = _init_config(config)

        self._update_status(init=True)

    @QtCore.Slot()
    def _export_config(self):
        msg = "Export Configuration"
        valid_exts = "Configuration files (*.yaml *.yml)"

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            msg,
            HOME,
            valid_exts,
        )

        if not file_path:
            return

        dump_config(file_path, self._config)

    @QtCore.Slot()
    def _update_worker_dir(self):
        worker_dir = str(self.workDirLineEdit.text())
        if not worker_dir:
            worker_dir = None

        self._config["worker_dir"] = worker_dir
        self.workDirLineEdit.clearFocus()
        self._update_status()

    @QtCore.Slot()
    def _reset_worker_dir(self):
        worker_dir = self._config["worker_dir"]

        if worker_dir is None:
            self.workDirLineEdit.clear()
            return

        self.workDirLineEdit.setText(worker_dir)

    @QtCore.Slot()
    def _select_worker_dir(self):
        if self._config["worker_dir"]:
            start_dir = self._config["worker_dir"]
        else:
            start_dir = HOME

        title_str = "Select Directory for Worker Files"
        worker_dir = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            title_str,
            start_dir,
            QtWidgets.QFileDialog.Option.ShowDirsOnly,
        )

        if worker_dir:
            self._config["worker_dir"] = str(worker_dir)
            self.workDirLineEdit.setText(worker_dir)
            self._update_status(update_results=False)

    @QtCore.Slot(object)
    def _update_clean_existing_dir(self, checked_state):
        self._config["clean_existing_dir"] = bool(
            checked_state == Qt.CheckState.Checked
        )
        self._update_status()
        return

    @QtCore.Slot(int)
    def _update_objective(self, box_number):
        if box_number < 0:
            return

        assert self._cost_var_box_to_var_id_map is not None
        var_id = self._cost_var_box_to_var_id_map[box_number]
        var_meta = self._shell.core.get_metadata(var_id)

        self._config["objective"] = var_id
        self._update_status(update_results=False)

        if var_meta.units is None:
            self.penaltyUnitsLabel.clear()
            self.toleranceUnitsLabel.clear()
            return

        unit = var_meta.units[0]
        self.penaltyUnitsLabel.setText(unit)
        self.toleranceUnitsLabel.setText(unit)

    @QtCore.Slot(object)
    def _update_maximise(self, checked_state):
        self._config["maximise"] = bool(checked_state == Qt.CheckState.Checked)

    @QtCore.Slot(float)
    def _update_base_penalty(self, value):
        self._config["base_penalty"] = value
        self._update_status(update_results=False)
        return

    @QtCore.Slot(float)
    def _update_tolerance(self, value):
        self._config["tolfun"] = value
        return

    @QtCore.Slot(int)
    def _update_n_threads(self, n_threads):
        self._config["n_threads"] = n_threads
        self._update_status(update_results=False)
        return

    @QtCore.Slot(int)
    def _update_max_simulations(self, max_simulations):
        if max_simulations > 0:
            self._config["max_simulations"] = max_simulations
        else:
            self._config["max_simulations"] = None

    @QtCore.Slot(int)
    def _update_max_time(self, timeout):
        if timeout > 0:
            self._config["timeout"] = timeout
        else:
            self._config["timeout"] = None

    @QtCore.Slot(object)
    def _update_min_noise_auto(self, checked_state):
        if checked_state == Qt.CheckState.Checked:
            self._config["min_evals"] = None
            self.minNoiseSpinBox.setValue(self._default_min_evals)
            self.minNoiseSpinBox.setEnabled(False)
            self.maxNoiseSpinBox.setMinimum(1)
        else:
            value = int(self.minNoiseSpinBox.value())
            self._config["min_evals"] = value
            self.minNoiseSpinBox.setEnabled(True)

    @QtCore.Slot(int)
    def _update_min_noise(self, value):
        self._config["min_evals"] = value
        self.maxNoiseSpinBox.setMinimum(value)
        return

    @QtCore.Slot(int)
    def _update_max_noise(self, value):
        self._config["max_evals"] = value
        return

    @QtCore.Slot(object)
    def _update_population_auto(self, checked_state):
        if checked_state == Qt.CheckState.Checked:
            self._config["popsize"] = None
            self.populationSpinBox.setValue(self._default_popsize)
            self.populationSpinBox.setEnabled(False)
        else:
            value = int(self.populationSpinBox.value())
            self._config["popsize"] = value
            self.populationSpinBox.setEnabled(True)

    @QtCore.Slot(int)
    def _update_population(self, value):
        self._config["popsize"] = value
        return

    @QtCore.Slot(int)
    def _update_max_resamples_algorithm(self, box_number):
        if box_number < 0:
            return
        if box_number > 1:
            raise RuntimeError("Algorithm index is out of range")

        value = int(self.maxResamplesSpinBox.value())

        if box_number == 1:
            value = "auto{}".format(value)

        self._config["max_resample_factor"] = value

    @QtCore.Slot(int)
    def _update_max_resamples(self, value):
        algorithm = int(self.maxResamplesComboBox.currentIndex())

        if algorithm > 1:
            raise RuntimeError("Algorithm index is out of range")

        if algorithm == 1:
            value = "auto{}".format(value)

        self._config["max_resample_factor"] = value

    def _update_status_results(self):
        if "Default" not in self._shell.project.get_simulation_titles():
            self.protectDefaultBox.setEnabled(False)
            self._protect_default = False
        else:
            self.protectDefaultBox.setEnabled(True)
            self.protectDefaultBox.stateChanged.emit(
                self.protectDefaultBox.checkState()
            )

        if self._sims_to_load is None:
            self.simLoadButton.setDisabled(True)
        else:
            self.simLoadButton.setEnabled(True)

        df = GUIAdvancedPosition.get_all_results(self._config)

        if self._results_df is not None and df.equals(self._results_df):
            return

        new_columns = []

        for column in df.columns:
            for key in self._var_id_to_title_map.keys():
                if key in column:
                    column = column.replace(key, self._var_id_to_title_map[key])

                    if key in self._var_id_to_unit_map:
                        column += " ({})".format(self._var_id_to_unit_map[key])

                    break

            new_columns.append(column)

        df.columns = new_columns

        self._results_df = df
        model = DataFrameModel(self._results_df)
        self.dataTableWidget.setViewModel(model)

        # Update plots tab
        new_columns.insert(0, "")
        self._update_plot_comboboxes(new_columns)
        self._clear_plot_widget()

    @QtCore.Slot(object)
    def _update_delete_sims(self, checked_state):
        if checked_state == Qt.CheckState.Checked:
            self._delete_sims = True
            self.protectDefaultBox.setEnabled(True)
        else:
            self._delete_sims = False
            self.protectDefaultBox.setEnabled(False)

    @QtCore.Slot(object)
    def _update_protect_default(self, checked_state):
        self._protect_default = bool(checked_state == Qt.CheckState.Checked)

    @QtCore.Slot(int)
    def _select_sims_to_load(self, button_id):
        assert isinstance(self._results_df, pd.DataFrame)

        objective = self._results_df.columns[1]
        ascending = True

        if "maximise" in self._config and self._config["maximise"]:
            ascending = False

        if button_id == 1:
            check_df = self._results_df.sort_values(
                by=[objective], ascending=ascending
            )
            self._sims_to_load = check_df["Simulation #"][:1].tolist()

        elif button_id == 2:
            check_df = self._results_df.sort_values(
                by=[objective], ascending=not ascending
            )
            self._sims_to_load = check_df["Simulation #"][:1].tolist()

        elif button_id == 3:
            check_df = self._results_df.sort_values(
                by=[objective], ascending=ascending
            )
            self._sims_to_load = check_df["Simulation #"][:5].tolist()

        elif button_id == 4:
            check_df = self._results_df.sort_values(
                by=[objective], ascending=not ascending
            )
            self._sims_to_load = check_df["Simulation #"][:5].tolist()

        else:
            self._update_custom_sims()

        custom_enabled = bool(button_id == 5)
        self.simsLabel.setEnabled(custom_enabled)
        self.simSelectEdit.setEnabled(custom_enabled)
        self.simHelpLabel.setEnabled(custom_enabled)

        self._update_status()

    @QtCore.Slot()
    def _update_custom_sims(self, update_status=True):
        sims_to_load_str = str(self.simSelectEdit.text())
        sims_to_load = None

        if sims_to_load_str:
            sims_to_load_strs = sims_to_load_str.split(",")

            try:
                sims_to_load = [int(x) for x in sims_to_load_strs]
            except Exception:
                module_logger.debug(
                    "Failed to translate simSelectEdit", exc_info=True
                )

        self._sims_to_load = sims_to_load

        if update_status:
            self._update_status(update_status)

    @QtCore.Slot()
    def _progress_load_sims(self):
        self._progress.allow_close = False
        self._progress.set_pulsing()

        if self._load_sims_thread is not None:
            return

        self._load_sims_thread = ThreadLoadSimulations(
            self._shell,
            self._sims_to_load,
            self._delete_sims,
            self._protect_default,
        )

        self._load_sims_thread.start()
        self._load_sims_thread.error_detected.connect(self._display_error)
        self._load_sims_thread.taskFinished.connect(self._finish_load_sims)

        self._progress.show()

    @QtCore.Slot()
    def _finish_load_sims(self):
        assert isinstance(self._load_sims_thread, ThreadLoadSimulations)
        self._load_sims_thread.error_detected.disconnect()
        self._load_sims_thread.taskFinished.disconnect()
        self._load_sims_thread = None

        # Emit signals on project
        self._shell.project.sims_updated.emit()
        self._shell.project.set_active_index(index=0)

        # Update the interface status
        self._shell.core.set_interface_status(self._shell.project)

        self._progress.allow_close = True
        self._progress.close()

    @QtCore.Slot()
    def _export_data_table(self):
        extlist = ["comma-separated values (*.csv)"]
        extStr = ";;".join(extlist)

        fdialog_msg = "Save data"

        save_path = QtWidgets.QFileDialog.getSaveFileName(
            self, fdialog_msg, HOME, extStr
        )

        if not save_path:
            return

        assert self._results_df is not None
        self._results_df.to_csv(str(save_path), index=False)

    def _update_status_plots(self):
        if self.plotWidget is None:
            plot_export_enabled = False
        else:
            plot_export_enabled = True

        self.plotExportButton.setEnabled(plot_export_enabled)

    def _update_plot_comboboxes(self, plot_columns):
        self.xAxisVarBox.addItems(plot_columns)
        self.yAxisVarBox.addItems(plot_columns)
        self.colorAxisVarBox.addItems(plot_columns)
        self.filterVarBox.addItems(plot_columns)

    @QtCore.Slot()
    def _set_plot(self, set_widget=True):
        assert self._results_df is not None

        x_axis_str = str(self.xAxisVarBox.currentText())
        y_axis_str = str(self.yAxisVarBox.currentText())
        color_axis_str = str(self.colorAxisVarBox.currentText())

        if not (x_axis_str and y_axis_str):
            return

        x_axis_data = self._results_df[x_axis_str]
        y_axis_data = self._results_df[y_axis_str]

        data_filter = np.array([True] * len(self._results_df))
        filter_str = str(self.filterVarBox.currentText())

        if filter_str:
            filter_data = self._results_df[filter_str]

            if self.filterVarMinBox.checkState() == Qt.CheckState.Checked:
                filter_val = float(self.filterVarMinSpinBox.value())
                data_filter = data_filter & (filter_data >= filter_val)

            if self.filterVarMaxBox.checkState() == Qt.CheckState.Checked:
                filter_val = float(self.filterVarMaxSpinBox.value())
                data_filter = data_filter & (filter_data <= filter_val)

        if not data_filter.all():
            x_axis_data = x_axis_data[data_filter]
            y_axis_data = y_axis_data[data_filter]

        color_axis_data = None
        cmap = mpl.colormaps["brg"]
        norm = None
        vmin = None
        vmax = None
        xmin = None
        xmax = None
        ymin = None
        ymax = None

        if self.xAxisMinBox.checkState() == Qt.CheckState.Checked:
            xmin = float(self.xAxisMinSpinBox.value())

        if self.xAxisMaxBox.checkState() == Qt.CheckState.Checked:
            xmax = float(self.xAxisMaxSpinBox.value())

        if self.yAxisMinBox.checkState() == Qt.CheckState.Checked:
            ymin = float(self.yAxisMinSpinBox.value())

        if self.yAxisMaxBox.checkState() == Qt.CheckState.Checked:
            ymax = float(self.yAxisMaxSpinBox.value())

        if self.colorAxisMinBox.checkState() == Qt.CheckState.Checked:
            vmin = float(self.colorAxisMinSpinBox.value())

        if self.colorAxisMaxBox.checkState() == Qt.CheckState.Checked:
            vmax = float(self.colorAxisMaxSpinBox.value())

        if color_axis_str:
            color_axis_data = self._results_df[color_axis_str]

            if not data_filter.all():
                color_axis_data = color_axis_data[data_filter]

            if len(set(color_axis_data)) < 2:
                color_axis_data = None

        if color_axis_data is not None and color_axis_data.dtype == np.int64:
            cb_vals = list(set(color_axis_data))

            if vmin is None:
                color_axis_min = color_axis_data.min()
            else:
                color_axis_min = int(vmin)
                cb_vals = [x for x in cb_vals if x >= vmin]

            if vmax is None:
                color_axis_max = color_axis_data.max()
            else:
                color_axis_max = int(vmax)
                cb_vals = [x for x in cb_vals if x <= vmax]

            if len(cb_vals) < 2:
                color_axis_data = None

            else:
                # define the bins and normalize
                n_vals = color_axis_max - color_axis_min + 2

                bounds = np.linspace(color_axis_min, color_axis_max + 1, n_vals)

                norm = colors.BoundaryNorm(bounds, cmap.N)

        fig, ax = plt.subplots()

        im = ax.scatter(
            x_axis_data,
            y_axis_data,
            c=color_axis_data,
            cmap=cmap,
            norm=norm,
            vmin=vmin,
            vmax=vmax,
        )

        ax.set_xlim([xmin, xmax])
        ax.set_ylim([ymin, ymax])

        ax.set(xlabel=x_axis_str, ylabel=y_axis_str)

        # Add a colorbar
        if color_axis_data is not None:
            extend = "neither"

            if vmin is not None and vmax is not None:
                extend = "both"
            elif vmin is not None:
                extend = "min"
            elif vmax is not None:
                extend = "max"

            cb = fig.colorbar(im, ax=ax, extend=extend)
            cb.set_label(color_axis_str)

            if color_axis_data.dtype == np.int64:
                # Relabel to centre of intervals
                labels = np.arange(color_axis_min, color_axis_max + 1, 1)
                loc = labels + 0.5
                cb.set_ticks(loc.tolist())
                cb.set_ticklabels(labels.tolist())

        fig.subplots_adjust(0.2, 0.2, 0.8, 0.8)

        if not set_widget:
            return

        n_figs = len(plt.get_fignums())
        log_str = "Opening figure {} ({} open)".format(fig.number, n_figs)  # type: ignore
        module_logger.debug(log_str)

        self._clear_plot_widget()

        widget = MPLWidget(fig, self)
        widget.setMinimumSize(QtCore.QSize(0, 250))

        self.plotWidget = widget
        self.plotLayout.addWidget(widget)

        # Draw the widget
        widget.draw_idle()

        if len(plt.get_fignums()) > 3:
            num_strs = ["{}".format(x) for x in plt.get_fignums()]
            num_str = ", ".join(num_strs)
            err_msg = (
                "Too many matplotlib figures detected. " "Numbers: {}"
            ).format(num_str)

            raise RuntimeError(err_msg)

        self._update_status_plots()

    def _clear_plot_widget(self):
        if self.plotWidget is None:
            return

        self.plotLayout.removeWidget(self.plotWidget)
        self.plotWidget.setParent(None)

        _close_plot(self.plotWidget)
        Shiboken.delete(self.plotWidget)

        self.plotWidget = None

    @QtCore.Slot()
    def _get_export_details(self):
        if self.plotWidget is None:
            return

        plot_ext_types = get_current_filetypes()

        msg = "Save plot"
        extlist = ["{} (*.{})".format(v, k) for k, v in plot_ext_types.items()]
        extStr = ";;".join(extlist)

        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            msg,
            HOME,
            extStr,
        )

        if not save_path:
            return

        if self.customSizeBox.checkState() == Qt.CheckState.Checked:
            size = (
                float(self.customWidthSpinBox.value()),
                float(self.customHeightSpinBox.value()),
            )
        else:
            size = get_current_figure_size()

        self._export_plot(save_path, size)

    def _export_plot(self, file_path, size, dpi=220):
        if self.plotWidget is None:
            return

        self._set_plot(set_widget=False)
        fig_handle = plt.gcf()

        fig_handle.set_size_inches(*size)

        with plt.rc_context(rc={"font.size": 8, "font.sans-serif": "Verdana"}):
            fig_handle.savefig(str(file_path), dpi=dpi, bbox_inches="tight")

        plt.close(fig_handle)

        # Ensure DPI is saved
        try:
            im = Image.open(str(file_path))
            im.save(str(file_path), dpi=[dpi, dpi])
        except IOError:
            pass

    @QtCore.Slot()
    def _import_yaml(self):
        msg = "Import Simulation"
        valid_exts = "Output files (*.yaml)"

        yaml_file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            msg,
            HOME,
            valid_exts,
        )

        if not yaml_file_path:
            return

        self._shell.strategy.import_simulation_file(
            self._shell.core, self._shell.project, str(yaml_file_path)
        )

        self.reset.emit()

    @QtCore.Slot(object, object, object)
    def _display_error(self, etype, evalue, etraceback):
        type_str = str(etype)
        type_strs = type_str.split(".")
        sane_type_str = type_strs[-1].replace("'>", "")

        if sane_type_str[0].lower() in "aeiou":
            article = "An"
        else:
            article = "A"

        errMsg = "{} {} occurred: {!s}".format(article, sane_type_str, evalue)

        module_logger.critical(errMsg)
        module_logger.critical("".join(traceback.format_tb(etraceback)))
        QtWidgets.QMessageBox.critical(self, "ERROR", errMsg)

    @staticmethod
    def _on_destroyed(widget):
        _close_plot(widget)

    def get_configuration(self):
        """A method for getting the dictionary to configure the strategy.

        Returns:
          dict
        """

        return deepcopy(self._config)

    def set_configuration(self, config_dict=None):
        """A method for displaying the configuration in the gui.

        Arguments:
          config_dict (dict, optional)
        """

        if config_dict is None:
            return

        module_logger.debug("Setting configuration")

        safe_config = _init_config(config_dict)
        self._config = safe_config
        self._update_status(init=True)


def _init_config(config: dict[str, Any]):
    new_config = deepcopy(config)

    config_template = _load_config_template()
    all_keys = config_template.keys()

    for key in all_keys:
        if key not in config:
            new_config[key] = None

    new_config["root_project_path"] = "worker.prj"
    new_config["clean_existing_dir"] = False
    if new_config["parameters"] is None:
        new_config["parameters"] = {}

    return new_config


def _make_var_box(widget, parent, object_name, group_title, box_class):
    var_box_dict = {}

    var_box_dict["root"] = QtWidgets.QGroupBox(parent)
    var_box_dict["root"].setFlat(False)
    var_box_dict["root"].setCheckable(False)

    root_name = _get_obj_name(object_name, "root")
    var_box_dict["root"].setObjectName(root_name)

    root_style = "#{}".format(root_name) + " " + "{font-weight: bold;}" + "\n"
    new_style_sheet = parent.styleSheet().append(root_style)
    parent.setStyleSheet(new_style_sheet)

    var_box_dict["root.layout"] = QtWidgets.QVBoxLayout(var_box_dict["root"])
    var_box_dict["root.layout"].setObjectName(
        _get_obj_name(object_name, "root.layout")
    )

    var_box_dict["fixed.layout"] = QtWidgets.QHBoxLayout()
    var_box_dict["fixed.layout"].setObjectName(
        _get_obj_name(object_name, "fixed.layout")
    )

    var_box_dict["fixed.check"] = QtWidgets.QCheckBox(var_box_dict["root"])
    var_box_dict["fixed.check"].setObjectName(
        _get_obj_name(object_name, "fixed.check")
    )
    var_box_dict["fixed.layout"].addWidget(var_box_dict["fixed.check"])

    var_box_dict["fixed.box"] = box_class(var_box_dict["root"])

    sizePolicy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Policy.Fixed,
        QtWidgets.QSizePolicy.Policy.Preferred,
    )
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(
        var_box_dict["fixed.box"].sizePolicy().hasHeightForWidth()
    )

    var_box_dict["fixed.box"].setSizePolicy(sizePolicy)
    var_box_dict["fixed.box"].setMinimumSize(QtCore.QSize(75, 0))
    var_box_dict["fixed.box"].setObjectName(
        _get_obj_name(object_name, "fixed.box")
    )
    var_box_dict["fixed.layout"].addWidget(var_box_dict["fixed.box"])

    spacerItem6 = QtWidgets.QSpacerItem(
        40,
        20,
        QtWidgets.QSizePolicy.Policy.Expanding,
        QtWidgets.QSizePolicy.Policy.Minimum,
    )
    var_box_dict["fixed.layout"].addItem(spacerItem6)

    var_box_dict["root.layout"].addLayout(var_box_dict["fixed.layout"])

    var_box_dict["range.group"] = QtWidgets.QGroupBox(var_box_dict["root"])
    var_box_dict["range.group"].setFlat(True)
    var_box_dict["range.group"].setObjectName(
        _get_obj_name(object_name, "range.group")
    )

    var_box_dict["range.layout"] = QtWidgets.QVBoxLayout(
        var_box_dict["range.group"]
    )
    var_box_dict["range.layout"].setObjectName(
        _get_obj_name(object_name, "range.layout")
    )

    var_box_dict["range.grid"] = QtWidgets.QGridLayout()
    var_box_dict["range.grid"].setSpacing(10)
    var_box_dict["range.grid"].setObjectName(
        _get_obj_name(object_name, "range.grid")
    )

    var_box_dict["range.label.type"] = QtWidgets.QLabel(
        var_box_dict["range.group"]
    )

    sizePolicy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Policy.Fixed,
        QtWidgets.QSizePolicy.Policy.Preferred,
    )
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(
        var_box_dict["range.label.type"].sizePolicy().hasHeightForWidth()
    )

    var_box_dict["range.label.type"].setSizePolicy(sizePolicy)
    var_box_dict["range.label.type"].setLayoutDirection(
        Qt.LayoutDirection.RightToLeft
    )
    var_box_dict["range.label.type"].setAlignment(
        Qt.AlignmentFlag.AlignRight
        | Qt.AlignmentFlag.AlignTrailing
        | Qt.AlignmentFlag.AlignVCenter
    )
    var_box_dict["range.label.type"].setObjectName(
        _get_obj_name(object_name, "range.label.type")
    )

    var_box_dict["range.grid"].addWidget(
        var_box_dict["range.label.type"], 0, 0, 1, 1
    )

    var_box_dict["range.box.type"] = QtWidgets.QComboBox(
        var_box_dict["range.group"]
    )

    sizePolicy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Policy.Preferred,
        QtWidgets.QSizePolicy.Policy.Fixed,
    )
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(
        var_box_dict["range.box.type"].sizePolicy().hasHeightForWidth()
    )

    var_box_dict["range.box.type"].setSizePolicy(sizePolicy)
    var_box_dict["range.box.type"].setObjectName(
        _get_obj_name(object_name, "range.box.type")
    )

    var_box_dict["range.grid"].addWidget(
        var_box_dict["range.box.type"], 0, 1, 1, 1
    )

    var_box_dict["range.label.var"] = QtWidgets.QLabel(
        var_box_dict["range.group"]
    )

    sizePolicy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Policy.Fixed,
        QtWidgets.QSizePolicy.Policy.Preferred,
    )
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(
        var_box_dict["range.label.var"].sizePolicy().hasHeightForWidth()
    )

    var_box_dict["range.label.var"].setSizePolicy(sizePolicy)
    var_box_dict["range.label.var"].setLayoutDirection(
        Qt.LayoutDirection.RightToLeft
    )
    var_box_dict["range.label.var"].setAlignment(
        Qt.AlignmentFlag.AlignRight
        | Qt.AlignmentFlag.AlignTrailing
        | Qt.AlignmentFlag.AlignVCenter
    )
    var_box_dict["range.label.var"].setObjectName(
        _get_obj_name(object_name, "range.label.var")
    )

    var_box_dict["range.grid"].addWidget(
        var_box_dict["range.label.var"], 0, 2, 1, 1
    )

    var_box_dict["range.box.var"] = QtWidgets.QComboBox(
        var_box_dict["range.group"]
    )

    sizePolicy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Policy.Expanding,
        QtWidgets.QSizePolicy.Policy.Fixed,
    )
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(
        var_box_dict["range.box.var"].sizePolicy().hasHeightForWidth()
    )

    var_box_dict["range.box.var"].setSizePolicy(sizePolicy)
    var_box_dict["range.box.var"].setObjectName(
        _get_obj_name(object_name, "range.box.var")
    )

    var_box_dict["range.grid"].addWidget(
        var_box_dict["range.box.var"], 0, 3, 1, 1
    )

    var_box_dict["range.label.min"] = QtWidgets.QLabel(
        var_box_dict["range.group"]
    )

    sizePolicy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Policy.Fixed,
        QtWidgets.QSizePolicy.Policy.Preferred,
    )
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(
        var_box_dict["range.label.min"].sizePolicy().hasHeightForWidth()
    )

    var_box_dict["range.label.min"].setSizePolicy(sizePolicy)
    var_box_dict["range.label.min"].setLayoutDirection(
        Qt.LayoutDirection.RightToLeft
    )
    var_box_dict["range.label.min"].setAlignment(
        Qt.AlignmentFlag.AlignRight
        | Qt.AlignmentFlag.AlignTrailing
        | Qt.AlignmentFlag.AlignVCenter
    )
    var_box_dict["range.label.min"].setObjectName(
        _get_obj_name(object_name, "range.label.min")
    )

    var_box_dict["range.grid"].addWidget(
        var_box_dict["range.label.min"], 1, 0, 1, 1
    )

    var_box_dict["range.box.min"] = box_class(var_box_dict["range.group"])

    sizePolicy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
    )
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(
        var_box_dict["range.box.min"].sizePolicy().hasHeightForWidth()
    )

    var_box_dict["range.box.min"].setSizePolicy(sizePolicy)
    var_box_dict["range.box.min"].setMinimumSize(QtCore.QSize(75, 0))
    var_box_dict["range.box.min"].setObjectName(
        _get_obj_name(object_name, "range.box.min")
    )

    var_box_dict["range.grid"].addWidget(
        var_box_dict["range.box.min"], 1, 1, 1, 1
    )

    var_box_dict["range.label.max"] = QtWidgets.QLabel(
        var_box_dict["range.group"]
    )

    sizePolicy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Policy.Fixed,
        QtWidgets.QSizePolicy.Policy.Preferred,
    )
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(
        var_box_dict["range.label.max"].sizePolicy().hasHeightForWidth()
    )

    var_box_dict["range.label.max"].setSizePolicy(sizePolicy)
    var_box_dict["range.label.max"].setLayoutDirection(
        Qt.LayoutDirection.RightToLeft
    )
    var_box_dict["range.label.max"].setAlignment(
        Qt.AlignmentFlag.AlignRight
        | Qt.AlignmentFlag.AlignTrailing
        | Qt.AlignmentFlag.AlignVCenter
    )
    var_box_dict["range.label.max"].setObjectName(
        _get_obj_name(object_name, "range.label.max")
    )

    var_box_dict["range.grid"].addWidget(
        var_box_dict["range.label.max"], 1, 2, 1, 1
    )

    var_box_dict["range.box.max"] = box_class(var_box_dict["range.group"])

    sizePolicy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Policy.Fixed,
        QtWidgets.QSizePolicy.Policy.Fixed,
    )
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(
        var_box_dict["range.box.max"].sizePolicy().hasHeightForWidth()
    )

    var_box_dict["range.box.max"].setSizePolicy(sizePolicy)
    var_box_dict["range.box.max"].setMinimumSize(QtCore.QSize(75, 0))
    var_box_dict["range.box.max"].setObjectName(
        _get_obj_name(object_name, "range.box.max")
    )

    var_box_dict["range.grid"].addWidget(
        var_box_dict["range.box.max"], 1, 3, 1, 1
    )

    var_box_dict["range.layout"].addLayout(var_box_dict["range.grid"])
    var_box_dict["root.layout"].addWidget(var_box_dict["range.group"])

    widget_name = str(widget.objectName())

    var_box_dict["root"].setTitle(_get_translation(widget_name, group_title))
    var_box_dict["fixed.check"].setText(
        _get_translation(widget_name, "Fixed Value:")
    )
    var_box_dict["range.group"].setTitle(_get_translation(widget_name, "Range"))
    var_box_dict["range.label.type"].setText(
        _get_translation(widget_name, "Type:")
    )
    var_box_dict["range.label.var"].setText(
        _get_translation(widget_name, "Variable:")
    )
    var_box_dict["range.label.min"].setText(
        _get_translation(widget_name, "Min:")
    )
    var_box_dict["range.label.max"].setText(
        _get_translation(widget_name, "Max:")
    )

    return var_box_dict


def _get_obj_name(name, key):
    ext_key = "{}.{}".format(key, name)
    ext_key = ext_key.replace(".", "_")
    return ext_key


def _get_translation(widget_name, text):
    return QtWidgets.QApplication.translate(widget_name, text, None)


def _init_sci_spin_box(parent, name):
    sizePolicy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Policy.Expanding,
        QtWidgets.QSizePolicy.Policy.Fixed,
    )
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)

    sciSpinBox = ScientificDoubleSpinBox(parent)
    sciSpinBox.setSizePolicy(sizePolicy)
    sciSpinBox.setMinimumSize(QtCore.QSize(0, 0))
    sciSpinBox.setKeyboardTracking(False)
    sciSpinBox.setObjectName(name)

    return sciSpinBox


def _init_extended_combo_box(parent, name):
    sizePolicy = QtWidgets.QSizePolicy(
        QtWidgets.QSizePolicy.Policy.Expanding,
        QtWidgets.QSizePolicy.Policy.Fixed,
    )
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)

    eComboBox = ExtendedComboBox(parent)
    eComboBox.setSizePolicy(sizePolicy)
    eComboBox.setMinimumSize(QtCore.QSize(0, 0))
    eComboBox.setObjectName(name)

    return eComboBox


def _make_fixed_combo_slot(that, param_name, param_type, name_map):
    @QtCore.Slot(object)
    def slot_function(that, checked_state):
        range_group = that._param_boxes[param_name]["range.group"]

        if checked_state == Qt.CheckState.Checked:
            enabled = False
        else:
            enabled = True

        range_group.setEnabled(enabled)
        param_dict = {}
        var_box_dict = that._param_boxes[param_name]

        if checked_state == Qt.CheckState.Checked:
            value = param_type(var_box_dict["fixed.box"].value())
            param_dict["fixed"] = value

        else:
            var_box_values = _read_var_box_values(var_box_dict, param_type)
            param_dict["range"] = _get_range_config(var_box_values, name_map)

        that._config["parameters"][param_name] = param_dict

    return types.MethodType(slot_function, that)


def _make_fixed_value_slot(that, param_name, param_type):
    @QtCore.Slot(object)
    def slot_function(that, value):
        fixed_check_box = that._param_boxes[param_name]["fixed.check"]
        use_fixed = bool(fixed_check_box.isChecked())

        if not use_fixed:
            return

        that._config["parameters"][param_name]["fixed"] = param_type(value)

    return types.MethodType(slot_function, that)


def _make_range_type_slot(that, param_name, param_type, name_map):
    @QtCore.Slot(object)
    def slot_function(that, current_str):
        current_str = str(current_str)
        range_var_box = that._param_boxes[param_name]["range.box.var"]

        if current_str == "Fixed":
            enabled = False
        else:
            enabled = True

        range_var_box.setEnabled(enabled)

        var_box_dict = that._param_boxes[param_name]
        var_box_values = _read_var_box_values(var_box_dict, param_type)
        range_config = _get_range_config(var_box_values, name_map)

        if param_name in that._config["parameters"]:
            that._config["parameters"][param_name]["range"] = range_config
        else:
            that._config["parameters"][param_name] = {"range": range_config}

    return types.MethodType(slot_function, that)


def _make_generic_range_slot(that, param_name, param_type, name_map):
    @QtCore.Slot(object)
    def slot_function(that, *args):  # pylint: disable=unused-argument
        var_box_dict = that._param_boxes[param_name]
        var_box_values = _read_var_box_values(var_box_dict, param_type)
        range_config = _get_range_config(var_box_values, name_map)

        if param_name in that._config["parameters"]:
            that._config["parameters"][param_name]["range"] = range_config
        else:
            that._config["parameters"][param_name] = {"range": range_config}

    return types.MethodType(slot_function, that)


def _read_var_box_values(var_box_dict, var_type):
    var_box_values = {}

    var_name = "range.box.type"
    var_value = str(var_box_dict[var_name].currentText())
    var_box_values[var_name] = var_value

    var_name = "range.box.var"
    var_value = str(var_box_dict[var_name].currentText())
    if not var_value:
        var_value = None
    var_box_values[var_name] = var_value

    var_name = "range.box.min"
    var_value = var_type(var_box_dict[var_name].value())
    var_box_values[var_name] = var_value

    var_name = "range.box.max"
    var_value = var_type(var_box_dict[var_name].value())
    var_box_values[var_name] = var_value

    return var_box_values


def _get_range_config(var_box_values, name_map):
    range_config_dict = {}

    range_config_dict["type"] = var_box_values["range.box.type"].lower()

    if range_config_dict["type"] == "multiplier":
        reverse_name_map = {v: k for k, v in name_map.items()}
        range_var = reverse_name_map[var_box_values["range.box.var"]]
        range_config_dict["variable"] = range_var
        min_key = "min_multiplier"
        max_key = "max_multiplier"

    else:
        min_key = "min"
        max_key = "max"

    range_config_dict[min_key] = var_box_values["range.box.min"]
    range_config_dict[max_key] = var_box_values["range.box.max"]

    return range_config_dict


def _close_plot(plot_widget):
    if plot_widget is None:
        return

    fignum = plot_widget.figure.number
    n_figs = len(plt.get_fignums())

    log_msg = "Closing figure {} ({} open)".format(fignum, n_figs)
    module_logger.debug(log_msg)

    plt.close(fignum)
