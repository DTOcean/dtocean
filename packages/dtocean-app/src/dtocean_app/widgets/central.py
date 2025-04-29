# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2022 Mathew Topper
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
Created on Thu Apr 23 12:51:14 2015

.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import os

from PyQt4 import QtCore, QtGui

from aneris.utilities.misc import OrderedSet
from dtocean_core.pipeline import Tree

from .display import (get_current_filetypes,
                      get_current_figure_size)
from .extendedcombobox import ExtendedComboBox
from ..utils.display import is_high_dpi

if is_high_dpi():

    from ..designer.high.details import Ui_DetailsWidget
    from ..designer.high.filemanager import Ui_FileManagerWidget
    from ..designer.high.plotmanager import Ui_PlotManagerWidget
    from ..designer.high.levelcomparison import Ui_LevelComparisonWidget
    from ..designer.high.simcomparison import Ui_SimComparisonWidget
    
else:
    
    from ..designer.low.details import Ui_DetailsWidget
    from ..designer.low.filemanager import Ui_FileManagerWidget
    from ..designer.low.plotmanager import Ui_PlotManagerWidget
    from ..designer.low.levelcomparison import Ui_LevelComparisonWidget
    from ..designer.low.simcomparison import Ui_SimComparisonWidget

# User home directory
HOME = os.path.expanduser("~")


class SelectForSaveFileDialog(QtGui.QFileDialog):
    
    def __init__(self, *args, **kwargs):
        
        super(SelectForSaveFileDialog, self).__init__(*args, **kwargs)
        self.setFileMode(QtGui.QFileDialog.AnyFile)
        self.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        self.setLabelText(QtGui.QFileDialog.Accept,
                          "Select")
        
        fileNameEdit = self.findChild(QtGui.QWidget, "fileNameEdit")
        fileNameEdit.textChanged.connect(self._check_exts)
        
        return
    
    def _get_valid_exts(self):
        
        filter_str = str(self.selectedNameFilter())
        
        if "(" in filter_str:
            idx_after_open_par = filter_str.find("(") + 1
            idx_before_close_par = filter_str.find(")")
            star_ext_str = filter_str[idx_after_open_par:idx_before_close_par]
        else:
            star_ext_str = filter_str
        
        star_exts = star_ext_str.split()
        
        # Check for "all files" wildcards
        if any(x in star_exts for x in ["*", "*.*"]): return None
        
        valid_exts = [x.replace("*", "") for x in star_exts]

        return valid_exts

    @QtCore.pyqtSlot(str)
    def _check_exts(self, file_path):
        
        valid_exts = self._get_valid_exts()
        
        if valid_exts is None: return

        _, file_ext = os.path.splitext(str(file_path))

        if file_ext not in valid_exts:
            
            button_box = self.findChild(QtGui.QDialogButtonBox)
            save_button = button_box.button(QtGui.QDialogButtonBox.Save)
            save_button.setEnabled(False)

        return


class ContextArea(QtGui.QWidget):
    
    def __init__(self, parent=None):
        
        super(ContextArea, self).__init__(parent)
        self._init_ui()
        
        return
        
    def _init_ui(self):
        
        self._topbox = QtGui.QHBoxLayout()
        self._hbox = QtGui.QHBoxLayout()
        self._top = QtGui.QWidget()
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                                       QtGui.QSizePolicy.Preferred)
        		
        self._top_left = QtGui.QFrame()
        self._top_left.setFrameShape(QtGui.QFrame.StyledPanel)
        
        if is_high_dpi():
            self._top_left.setMinimumWidth(375)
            self._top_left.setMaximumWidth(500)                            
            self._top_left.setMinimumHeight(175)
        else:
            self._top_left.setMinimumWidth(290)
            self._top_left.setMaximumWidth(450)                            
            self._top_left.setMinimumHeight(150)
                        
        self._top_left.setSizePolicy(sizePolicy)
        
        self._top_left_box = QtGui.QHBoxLayout()
        self._top_left.setLayout(self._top_left_box)
        self._top_left_contents = None
        self._top_left_box.setContentsMargins(2, 2, 2, 2)
        
        self._top_right = QtGui.QFrame()
        self._top_right.setFrameShape(QtGui.QFrame.StyledPanel)

        if is_high_dpi():
            self._top_right.setMinimumWidth(425)
        else:
            self._top_right.setMinimumWidth(360)
            
        self._top_right_box = QtGui.QHBoxLayout()
        self._top_right.setLayout(self._top_right_box)
        self._top_right_contents = None
        self._top_right_box.setContentsMargins(2, 2, 2, 2)
        
        self._bottom = QtGui.QFrame()
        self._bottom.setFrameShape(QtGui.QFrame.StyledPanel)
        self._bottom_box = QtGui.QHBoxLayout()
        self._bottom.setLayout(self._bottom_box)
        self._bottom_contents = None
          
        self._topbox.addWidget(self._top_left)
        self._topbox.addWidget(self._top_right)
        self._top.setLayout(self._topbox)
        self._topbox.setContentsMargins(0, 0, 0, 2)
        		
        self._splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self._splitter.addWidget(self._top)
        self._splitter.addWidget(self._bottom)
        self._splitter.setStretchFactor(1, 2)
        
        self._hbox.addWidget(self._splitter)
        self.setLayout(self._hbox)
        self._hbox.setContentsMargins(0, 0, 2, 0)
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)
        
        return


class DetailsWidget(QtGui.QWidget, Ui_DetailsWidget):

    def __init__(self, parent):

        QtGui.QWidget.__init__(self, parent)
        Ui_DetailsWidget.__init__(self)
        
        self.setupUi(self)
        self._set_details(None, None)

        return
        
    def _set_details(self, title, description):
        
        if title is None: title = ""
        if description is None: description = ""
        
        titleStr = title.encode('utf-8')
        descriptionStr = description.encode('utf-8')

        self.titleLabel.setText(titleStr)
        self.descriptionLabel.setText(descriptionStr)

        return


class FileManagerWidget(QtGui.QWidget, Ui_FileManagerWidget):
    
    load_file = QtCore.pyqtSignal(object, str, str)
    save_file = QtCore.pyqtSignal(object, str, str)
    
    def __init__(self, parent=None):
        
        QtGui.QWidget.__init__(self, parent)
        Ui_FileManagerWidget.__init__(self)
        self._load_ext_dict = None
        self._save_ext_dict = None
        self._file_mode = None
        self._variable = None
        self._load_connected = False
        self._save_connected = False
        
        self._init_ui()
        
        return
    
    def _init_ui(self):
        
        self.setupUi(self)
        
        self.loadButton.clicked.connect(
                            lambda: self._set_file_mode("load"))
        self.saveButton.clicked.connect(
                            lambda: self._set_file_mode("save"))
        
        self.getPathButton.clicked.connect(self._set_path)
        self.pathEdit.textChanged.connect(self._set_okay)
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(
                                                        self._emit_file_signal)
        
        return
    
    def _set_files(self, variable, load_ext_dict=None, save_ext_dict=None):
        
        self._variable = variable
        
        self.pathEdit.clear()
        self.saveButton.setDisabled(True)
        self.loadButton.setDisabled(True)
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setDisabled(True)
        
        self._load_ext_dict = None
        self._save_ext_dict = None
        self._file_mode = None
        
        if variable is None or (load_ext_dict is None and
                                save_ext_dict is None):
            
            self.setDisabled(True)
            return
        
        else:
            
            self.setEnabled(True)
        
        if load_ext_dict is not None:
            
            self.loadButton.setEnabled(True)
            self._load_ext_dict = load_ext_dict
        
        if save_ext_dict is not None:
            
            self.saveButton.setEnabled(True)
            self._save_ext_dict = save_ext_dict
        
        if load_ext_dict is not None:
            self.loadButton.setChecked(True)
            self._set_file_mode("load")
        else:
            self.saveButton.setChecked(True)
            self._set_file_mode("save")
        
        return
    
    @QtCore.pyqtSlot(str)
    def _set_file_mode(self, file_mode):
        
        self.pathEdit.clear()
        
        if file_mode == "load":
            self._file_mode = "load"
        elif file_mode == "save":
            self._file_mode = "save"
        else:
            errStr = "Argument file_mode may only have values 'load' or 'save'"
            raise ValueError(errStr)
        
        return
    
    @QtCore.pyqtSlot()
    def _set_path(self):
        
        valid_exts = self._get_valid_exts()
        valid_ext_strs = ["*{}".format(file_ext) for file_ext in valid_exts]
        file_ext_str = " ".join(valid_ext_strs)
        name_filter =  "Supported formats ({})".format(file_ext_str)
        file_path = ""
        
        if self._file_mode == "load":
            
            msg = "Select path to load"
            dialog = QtGui.QFileDialog(self, msg, HOME)
            dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
            dialog.setOption(QtGui.QFileDialog.DontConfirmOverwrite, True)
            dialog.setNameFilter(name_filter)
            dialog.setLabelText(QtGui.QFileDialog.Accept,
                                "Select")
            dialog.selectFile(self.pathEdit.text())
            
            if dialog.exec_():
                file_path = str(dialog.selectedFiles()[0])
        
        elif self._file_mode == "save":
            
            msg = "Select path for save"
            dialog = SelectForSaveFileDialog(self, msg, HOME)
            dialog.setNameFilter(name_filter)
            dialog.selectFile(self.pathEdit.text())
            
            if dialog.exec_():
                file_path = str(dialog.selectedFiles()[0])
        
        else: # pragma: no cover
            
            errStr = "There are children here somewhere. I can smell them."
            raise SystemError(errStr)
        
        self.pathEdit.setText(file_path)
        
        return
    
    @QtCore.pyqtSlot()
    def _set_okay(self):
        
        valid_exts = self._get_valid_exts()
        file_path = str(self.pathEdit.text())
        _, file_ext = os.path.splitext(str(file_path))
        
        if file_ext in valid_exts:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setDisabled(True)
            
        return
    
    @QtCore.pyqtSlot()
    def _emit_file_signal(self):
        
        file_mode = self._file_mode
        file_path = str(self.pathEdit.text())
        file_ext = os.path.splitext(file_path)[1]
        
        if file_mode == "load":
            
            if file_ext not in self._load_ext_dict.keys():
                err_msg = "{} is not a valid extension".format(file_ext)
                raise ValueError(err_msg)
            
            interface_name = self._load_ext_dict[file_ext]
            self.load_file.emit(self._variable, interface_name, file_path)
        
        elif file_mode == "save":
            
            if file_ext not in self._save_ext_dict.keys():
                err_msg = "{} is not a valid extension".format(file_ext)
                raise ValueError(err_msg)
            
            interface_name = self._save_ext_dict[file_ext]
            self.save_file.emit(self._variable, interface_name, file_path)
        
        else:
            
            errStr = "Don't cross the streams!"
            raise SystemError(errStr)
        
        self.pathEdit.clear()
        
        return
    
    def _get_valid_exts(self):
        
        if self._file_mode == "load":
            valid_exts = self._load_ext_dict.keys()
        elif self._file_mode == "save":
            valid_exts = self._save_ext_dict.keys()
        else: # pragma: no cover
            errStr = "It must be one of those unidentified flying cupcakes"
            raise SystemError(errStr)
        
        return valid_exts


class PlotManagerWidget(QtGui.QWidget, Ui_PlotManagerWidget):
    
    plot = QtCore.pyqtSignal(object, object)
    save = QtCore.pyqtSignal(object, str, object, object)
    
    def __init__(self, parent=None):
        
        QtGui.QWidget.__init__(self, parent)
        Ui_PlotManagerWidget.__init__(self)
        self._controller = None
        self._ext_types = None
        self._plot_connected = False
        self._current_plot = None
        
        self._init_ui()
        
        return
    
    def _init_ui(self):
        
        self.setupUi(self)
        
        # Add buttons
        self.plotButton = QtGui.QPushButton("Plot")
        self.saveButton = QtGui.QPushButton("Save")
        self.defaultButton = QtGui.QPushButton("Default")
        
        self.buttonBox.addButton(self.plotButton,
                                 QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.saveButton,
                                 QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.defaultButton,
                                 QtGui.QDialogButtonBox.ResetRole)
        
        self.getPathButton.clicked.connect(self._set_path)
        self.pathEdit.textChanged.connect(self._set_save)
        self.checkBox.stateChanged.connect(self._set_custom_size)
        self.plotButton.clicked.connect(self._emit_named_plot)
        self.saveButton.clicked.connect(self._emit_save)
        self.defaultButton.clicked.connect(self._emit_default_plot)
        
        return
    
    def _set_plots(self, controller, plot_list=None, plot_auto=False):
        
        self._controller = None
        self._ext_types = None
        self._current_plot = None
        
        if controller is None or (plot_list is None and not plot_auto):
            
            self.setDisabled(True)
            return
        
        self.setEnabled(True)
        
        self._controller = controller
        self._ext_types = get_current_filetypes()
        
        if not self._ext_types:
            
            self.saveButton.setDisabled(True)
            self.pathEdit.setDisabled(True)
        
        else:
            
            self.saveButton.setEnabled(True)
            self.pathEdit.setEnabled(True)
        
        self._set_plot_list(plot_list, plot_auto)
        self._set_save()
        
        return
    
    def _set_plot_list(self, plot_list=None, plot_auto=False):
        
        self.plotBox.clear()
        
        if plot_list is None:
            
            self.plotBox.setDisabled(True)
            self.plotButton.setDisabled(True)
        
        else:
            
            self.plotBox.setEnabled(True)
            self.plotButton.setEnabled(True)
            
            for item in plot_list:
                self.plotBox.addItem(item)
        
        if plot_auto:
            self.defaultButton.setEnabled(True)
        else:
            self.defaultButton.setDisabled(True)
        
        return
    
    @QtCore.pyqtSlot()
    def _set_path(self):
        
        if self._ext_types is None: return
        
        extlist = ["{} (*.{})".format(v, k) for k, v in
                                               self._ext_types.iteritems()]
        name_filter = ";;".join(extlist)
        file_path = ""
        
        msg = "Select path for save"
        dialog = SelectForSaveFileDialog(self, msg, HOME)
        dialog.setNameFilter(name_filter)
        dialog.selectFile(self.pathEdit.text())
        
        if dialog.exec_():
            file_path = str(dialog.selectedFiles()[0])
        
        self.pathEdit.setText(file_path)
        
        return
    
    @QtCore.pyqtSlot()
    def _set_save(self):
        
        if self._ext_types is None: return
        
        valid_exts = [".{}".format(k) for k in self._ext_types.keys()]
        file_path = str(self.pathEdit.text())
        _, file_ext = os.path.splitext(str(file_path))
        
        if file_ext in valid_exts:
            self.saveButton.setEnabled(True)
        else:
            self.saveButton.setDisabled(True)
        
        return
    
    @QtCore.pyqtSlot()
    def _set_custom_size(self):
        
        size = get_current_figure_size()
        
        if self.checkBox.isChecked():
            
            self.widthSpinBox.setValue(size[0])
            self.heightSpinBox.setValue(size[1])
            
            self.widthSpinBox.setEnabled(True)
            self.heightSpinBox.setEnabled(True)
        
        else:
            
            self.widthSpinBox.setDisabled(True)
            self.heightSpinBox.setDisabled(True)
        
        return
    
    @QtCore.pyqtSlot()
    def _emit_named_plot(self):
        
        plot_name = str(self.plotBox.currentText())
        self.plot.emit(self._controller, plot_name)
        self._current_plot = plot_name
        
        return
    
    @QtCore.pyqtSlot()
    def _emit_default_plot(self):
        
        self.plot.emit(self._controller, "auto")
        self._current_plot = None
    
    @QtCore.pyqtSlot()
    def _emit_save(self):
        
        figure_path = str(self.pathEdit.text())
        
        if self.checkBox.isChecked():
            size = (float(self.widthSpinBox.value()),
                    float(self.heightSpinBox.value()))
        else:
            size = get_current_figure_size()
        
        self.save.emit(self._controller,
                       figure_path,
                       size,
                       self._current_plot)
        
        self.pathEdit.clear()
        
        return


class ComparisonWidget(object):
        
    def __init__(self):

        self._var_ids = None
        self._mod_names = None

        self._init_ui()

        return
        
    def _init_ui(self):
        
        self.setupUi(self)
        
        # Buttons
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setDisabled(True)
        self.buttonBox.button(QtGui.QDialogButtonBox.Save).setDisabled(True)
        
        return
        
    def _get_var_id(self, var_name):
        
        return self._var_ids[var_name]
        
    def _set_interfaces(self, shell, include_str=False):
        
        self.varBox.clear()
                
        active_modules = shell.module_menu.get_active(shell.core,
                                                      shell.project)
        
        active_themes = shell.theme_menu.get_active(shell.core,
                                                    shell.project)
        
        active_interfaces = active_modules + active_themes
        
        self._mod_names = active_modules
        self._set_variables(shell, active_interfaces, include_str)
            
        return
        
    def _set_variables(self, shell, active_interfaces, include_str=False):
        
        self.varBox.clear()
        
        tree = Tree()
        
        all_var_names = []
        var_id_dict = {}
        
        for interface_name in active_interfaces:
            
            branch = tree.get_branch(shell.core,
                                     shell.project,
                                     interface_name)
            
            var_inputs = branch.get_inputs(shell.core, shell.project)
            var_outputs = branch.get_outputs(shell.core, shell.project)
            
            unique_vars = OrderedSet(var_inputs + var_outputs)
            
            var_names = []
            var_names = []

            for var_id in unique_vars:
                
                var_meta = shell.core.get_metadata(var_id)

                if "SimpleData" in var_meta.structure:
                    
                    if var_meta.types is None:
                        
                        errStr = ("Variable {} with SimpleData structure "
                                  "requires types meta data to be "
                                  "set").format(var_id)
                        raise ValueError(errStr)
                        
                    if "int" in var_meta.types or "float" in var_meta.types:
                        var_names.append(var_meta.title)
                        
                    if include_str and "str" in var_meta.types:
                        var_names.append(var_meta.title)
                    
                    if var_meta.title not in var_id_dict:
                        var_id_dict[var_meta.title] = var_id
            
            all_var_names.extend(var_names)
            
        self._var_ids = var_id_dict
        
        self.varBox.addItems(all_var_names)
        self.varBox.setCurrentIndex(-1)
        
        return
        
    def _get_mode(self):
        
        # Collect the current mode
        if self.plotButton.isChecked():
            mode = "plot"
        elif self.dataButton.isChecked():
            mode = "data"
        else:
            errStr = "Hairy Japanese Bastards!"
            raise SystemError(errStr)
            
        return mode
        

class LevelComparison(QtGui.QWidget,
                      Ui_LevelComparisonWidget,
                      ComparisonWidget):
    
    plot_levels = QtCore.pyqtSignal(str, bool)
    tab_levels = QtCore.pyqtSignal(str, bool)
    save_plot = QtCore.pyqtSignal()
    save_data = QtCore.pyqtSignal()
    
    def __init__(self, parent):
        
        QtGui.QWidget.__init__(self, parent)
        Ui_LevelComparisonWidget.__init__(self)
        ComparisonWidget.__init__(self)
        
        return
        
    def _init_ui(self):
        
        super(LevelComparison, self)._init_ui()
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(
                                                self._emit_widget_request)
        self.buttonBox.button(QtGui.QDialogButtonBox.Save).clicked.connect(
                                                self._save)
        
        # Custom var box
        self.varBox = ExtendedComboBox(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
                                self.varBox.sizePolicy().hasHeightForWidth())
        self.varBox.setSizePolicy(sizePolicy)
        self.varBox.setObjectName("varBox")
        self.bottomHorizontalLayout.addWidget(self.varBox)
        
        # Signals
        self.varBox.currentIndexChanged.connect(self._ok_button_ui_switch)
        
        return
        
    def _emit_widget_request(self):
                
        current_var = str(self.varBox.currentText())
        var_id = self._get_var_id(current_var)

        ignore_strategy = self.strategyBox.isChecked()
        
        if self._get_mode() == "plot":
            self.plot_levels.emit(var_id, ignore_strategy)
        elif self._get_mode() == "data":
            self.tab_levels.emit(var_id, ignore_strategy)
        else:
            errStr = "Down with this sort of thing"
            raise SystemError(errStr)
        
        return
        
    @QtCore.pyqtSlot()    
    def _save(self):
        
        if self._get_mode() == "plot":
            self.save_plot.emit()
        elif self._get_mode() == "data":
            self.save_data.emit()
        else:
            raise SystemError("We're hit! We took a hit!")
        
        return
        
    @QtCore.pyqtSlot(int)
    def _ok_button_ui_switch(self, box_number):
        
        if box_number == -1:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setDisabled(True)
        else:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        
        return


class SimulationComparison(QtGui.QWidget,
                           Ui_SimComparisonWidget,
                           ComparisonWidget):
    
    plot_levels = QtCore.pyqtSignal(str, str, bool)
    tab_levels = QtCore.pyqtSignal(str, str, bool)
    save_plot = QtCore.pyqtSignal()
    save_data = QtCore.pyqtSignal()
    
    def __init__(self, parent):
        
        QtGui.QWidget.__init__(self, parent)
        Ui_SimComparisonWidget.__init__(self)
        ComparisonWidget.__init__(self)
        
        return
        
    def _init_ui(self):
        
        super(SimulationComparison, self)._init_ui()
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(
                                                    self._emit_widget_request)
        self.buttonBox.button(QtGui.QDialogButtonBox.Save).clicked.connect(
                                                    self._save)
        
        # Custom var boxes
        self.varBox = ExtendedComboBox(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
                                self.varBox.sizePolicy().hasHeightForWidth())
        self.varBox.setSizePolicy(sizePolicy)
        self.varBox.setObjectName("varBox")
        self.bottomHorizontalLayout.addWidget(self.varBox)
        
        self.modBox = ExtendedComboBox(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
                                self.modBox.sizePolicy().hasHeightForWidth())
        self.modBox.setSizePolicy(sizePolicy)
        self.modBox.setObjectName("modBox")
        self.middleHorizontalLayout.addWidget(self.modBox)
        
        # Signals
        self.varBox.currentIndexChanged.connect(self._set_modules)
        self.modBox.currentIndexChanged.connect(self._ok_button_ui_switch)
        
        return
        
    @QtCore.pyqtSlot(int)
    def _set_modules(self, box_number):
        
        self.modBox.clear()
                
        if box_number != -1: self.modBox.addItems(self._mod_names)
        
        self.modBox.setCurrentIndex(-1)
                
        return

    @QtCore.pyqtSlot()
    def _emit_widget_request(self):
        
        current_var = str(self.varBox.currentText())
        var_id = self._get_var_id(current_var)

        current_mod = str(self.modBox.currentText())

        ignore_strategy = self.strategyBox.isChecked()

        if self._get_mode() == "plot":
            self.plot_levels.emit(var_id, current_mod, ignore_strategy)
        elif self._get_mode() == "data":
            self.tab_levels.emit(var_id, current_mod, ignore_strategy)
        else:
            errStr = "Careful now"
            raise SystemError(errStr)
        
        return
        
    @QtCore.pyqtSlot()    
    def _save(self):
        
        if self._get_mode() == "plot":
            self.save_plot.emit()
        elif self._get_mode() == "data":
            self.save_data.emit()
        else:
            raise SystemError("Shut up, shut up, shut up!")
        
        return
        
    @QtCore.pyqtSlot(int)
    def _ok_button_ui_switch(self, box_number):
        
        if box_number == -1:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setDisabled(True)
        else:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        
        return

