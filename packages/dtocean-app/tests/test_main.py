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

# pylint: disable=redefined-outer-name,protected-access,no-self-use,unused-argument

import os
import logging
import contextlib

import numpy as np
import pytest
import matplotlib.pyplot as plt
from PyQt4 import QtCore, QtGui

from polite.paths import Directory
from dtocean_core.interfaces import ModuleInterface, ThemeInterface
from dtocean_core.tools import Tool
from dtocean_app.core import GUICore
from dtocean_app.main import DTOceanWindow, Shell
from dtocean_app.pipeline import (InputBranchControl,
                                  InputVarControl,
                                  SectionControl)
from dtocean_app.tools import GUITool
from dtocean_app.widgets.display import MPLWidget
from dtocean_app.widgets.input import FloatSelect, ListSelect


@contextlib.contextmanager
def caplog_for_logger(caplog, logger_name, level=logging.DEBUG):
    caplog.handler.records = []
    logger = logging.getLogger(logger_name)
    logger.addHandler(caplog.handler)
    logger.setLevel(level)
    yield
    logger.removeHandler(caplog.handler)


class MockModule(ModuleInterface):
    
    @classmethod
    def get_name(cls):
        
        return "Mock Module"
        
    @classmethod
    def declare_weight(cls):
        
        return 998

    @classmethod
    def declare_inputs(cls):
        
        input_list = ['bathymetry.layers',
                      'device.system_type',
                      'device.power_rating',
                      'device.cut_in_velocity',
                      'device.turbine_interdistance',
                      'project.annual_energy_per_device']
        
        return input_list

    @classmethod
    def declare_outputs(cls):
        
        output_list = ['project.layout',
                       'project.annual_energy',
                       'project.number_of_devices']
        
        return output_list
        
    @classmethod
    def declare_optional(cls):
        
        return None
        
    @classmethod
    def declare_id_map(self):
        
        id_map = {"dummy1": "bathymetry.layers",
                  "dummy2": "device.cut_in_velocity",
                  "dummy3": "device.system_type",
                  "dummy4": "device.power_rating",
                  "dummy5": "project.layout",
                  "dummy6": "project.annual_energy",
                  "dummy7": "project.number_of_devices",
                  "dummy8": "device.turbine_interdistance",
                  "dummy9": 'project.annual_energy_per_device'}
                  
        return id_map
                 
    def connect(self, debug_entry=False,
                      export_data=True):
        
        return


class MockTheme(ThemeInterface):
    
    @classmethod
    def get_name(cls):
        
        return "Mock Theme"
        
    @classmethod
    def declare_weight(cls):
        
        return 998

    @classmethod
    def declare_inputs(cls):
        
        input_list = ['bathymetry.layers',
                      'device.system_type',
                      'device.power_rating',
                      'device.cut_in_velocity',
                      'device.turbine_interdistance']
        
        return input_list

    @classmethod
    def declare_outputs(cls):
        
        output_list = ['project.layout',
                       'project.annual_energy',
                       'project.number_of_devices']
        
        return output_list
        
    @classmethod
    def declare_optional(cls):
        
        return None
        
    @classmethod
    def declare_id_map(self):
        
        id_map = {"dummy1": "bathymetry.layers",
                  "dummy2": "device.cut_in_velocity",
                  "dummy3": "device.system_type",
                  "dummy4": "device.power_rating",
                  "dummy5": "project.layout",
                  "dummy6": "project.annual_energy",
                  "dummy7": "project.number_of_devices",
                  "dummy8": "device.turbine_interdistance"}
                  
        return id_map
                 
    def connect(self, debug_entry=False,
                      export_data=True):
        
        return


class MockTool(GUITool, Tool):
    
    def __init__(self):
        Tool.__init__(self)
        GUITool.__init__(self)
        self._fig = None
    
    @classmethod
    def get_name(cls):
        return "Mock Tool"
        
    @classmethod
    def declare_inputs(cls):
        return ["device.system_type"]
    
    @classmethod
    def declare_outputs(cls):
        return None

    @classmethod
    def declare_optional(cls):
        return None
    
    @classmethod
    def declare_id_map(cls):
        return {'system_type': "device.system_type"}
    
    def get_weight(self):
        return 999
    
    def has_widget(self):
        return True
    
    def get_widget(self):
        
        # Data for plotting
        t = np.arange(0.0, 2.0, 0.01)
        s = 1 + np.sin(2 * np.pi * t)
        
        fig, ax = plt.subplots()
        ax.plot(t, s)
        
        ax.set(xlabel='time (s)', ylabel='voltage (mV)',
               title='About as simple as it gets, folks')
        ax.grid()
        
        widget = MPLWidget(fig, self.parent)
        self._fig = fig
        
        return widget
    
    def destroy_widget(self):
        plt.close(self._fig)
        self._fig = None
        return
    
    def configure(self, kwargs=None):
        return
    
    def connect(self, **kwargs):
        return


@pytest.fixture
def core(mocker):
    
    mocker.patch('dtocean_core.extensions.ToolManager._discover_classes',
                 return_value={"MockTool": MockTool},
                 autospec=True)
    
    mocker.patch('dtocean_core.extensions.ToolManager._discover_names',
                 return_value={"Mock Tool": "MockTool"},
                 autospec=True)
    
    core = GUICore()
    core._create_data_catalog()
    core._create_control()
    core._create_sockets()
    core._init_plots()
    
    return core


@pytest.fixture
def window(mocker, qtbot, tmp_path, core):
    
    
    mocker.patch('dtocean_core.utils.database.UserDataDirectory',
                 return_value=Directory(str(tmp_path)),
                 autospec=True)
    
    mocker.patch('dtocean_app.main.Shell.get_available_modules',
                 return_value=["Mock Module"],
                 autospec=True)
    
    mocker.patch('dtocean_app.main.Shell.get_available_themes',
                 return_value=["Mock Theme"],
                 autospec=True)
    
    mocker.patch('dtocean_app.main.DTOceanWindow._project_close_warning',
                 return_value=QtGui.QMessageBox.Discard,
                 autospec=True)
    
    
    shell = Shell(core)
    
    socket = shell.core.control._sequencer.get_socket("ModuleInterface")
    socket.add_interface(MockModule)
    
    socket = shell.core.control._sequencer.get_socket("ThemeInterface")
    socket.add_interface(MockTheme)
    
    window = DTOceanWindow(shell)
    window.show()
    qtbot.addWidget(window)
    
    yield window
    
    def no_active_thread():
        assert shell._active_thread is None
    
    qtbot.waitUntil(no_active_thread)


def test_window(window):
    assert window.windowTitle() == "DTOcean"


def test_close_open_dock(qtbot, window):
    
    # Close the system dock
    window._system_dock.close()
    
    def dock_is_closed(): assert window._system_dock.isHidden()

    qtbot.waitUntil(dock_is_closed)
    
    # Reopen the system dock
    menu_click(qtbot,
               window,
               window.menuView,
               "actionSystem_Log")
    
    def dock_is_open(): assert window._system_dock.isVisible()

    qtbot.waitUntil(dock_is_open)
    
    assert window._system_dock.isVisible()


@pytest.fixture
def window_debug(mocker, qtbot, tmp_path, core):
    
    mocker.patch('dtocean_core.utils.database.UserDataDirectory',
                 return_value=Directory(str(tmp_path)),
                 autospec=True)
    
    mocker.patch('dtocean_app.main.Shell.get_available_modules',
                 return_value=["Mock Module"],
                 autospec=True)
    
    mocker.patch('dtocean_app.main.Shell.get_available_themes',
                 return_value=["Mock Theme"],
                 autospec=True)
    
    mocker.patch('dtocean_app.main.DTOceanWindow._project_close_warning',
                 return_value=QtGui.QMessageBox.Discard,
                 autospec=True)
    
    shell = Shell(core)
    socket = shell.core.control._sequencer.get_socket("ModuleInterface")
    socket.add_interface(MockModule)
    
    socket = shell.core.control._sequencer.get_socket("ThemeInterface")
    socket.add_interface(MockTheme)
    
    window = DTOceanWindow(shell, debug=True)
    window.show()
    qtbot.addWidget(window)
    
    yield window
    
    def no_active_thread():
        assert shell._active_thread is None
    
    qtbot.waitUntil(no_active_thread)


def test_window_debug(window_debug):
    assert window_debug.windowTitle() == "DTOcean"


def test_project_open_error(mocker, qtbot, tmp_path, window_debug):
    
    dto_file = tmp_path / "test.dto"
    dto_file_path = str(dto_file)
    
    mocker.patch.object(QtGui.QFileDialog,
                        'getOpenFileName',
                        return_value=dto_file_path)
    
    mock = mocker.patch.object(QtGui.QMessageBox,
                               'critical')
    
    # Open the project
    open_button = window_debug.fileToolBar.widgetForAction(
                                                    window_debug.actionOpen)
    qtbot.mouseClick(open_button, QtCore.Qt.LeftButton)
    
    def mock_called(): assert mock.call_count == 1
    
    qtbot.waitUntil(mock_called)
    
    assert mock.call_args.args[1] == "ERROR"
    assert "No such file or directory" in mock.call_args.args[2]
    assert window_debug._shell._active_thread is None


def test_tool_unvailable(window_debug):
    action = window_debug.menuTools.actions()[1]
    assert str(action.text()) == "Mock Tool"
    assert not action.isEnabled()


@pytest.fixture
def window_new_project(mocker, qtbot, window_debug):
    
    # Get the new project button and click it
    new_project_button = window_debug.fileToolBar.widgetForAction(
                                                        window_debug.actionNew)
    qtbot.mouseClick(new_project_button, QtCore.Qt.LeftButton)
    
    assert window_debug.windowTitle() == "DTOcean: Untitled project*"
    
    return window_debug


def test_new_project(window_new_project):
    
    # Pick up the available pipeline item
    test_var = window_new_project._pipeline_dock._find_controller(
                                    controller_title="Device Technology Type",
                                    controller_class=InputVarControl)
    
    assert test_var._id == "device.system_type"


def test_click_section_twice(qtbot, window_new_project):
    
    # Pick up the available pipeline item
    test_var = window_new_project._pipeline_dock._find_controller(
                                    controller_title="Configuration",
                                    controller_class=SectionControl)
    
    # obtain the rectangular coordinates of the child item
    tree_view = window_new_project._pipeline_dock.treeView
    index = test_var._get_index_from_address()
    proxy_index = test_var._proxy.mapFromSource(index)
    rect = tree_view.visualRect(proxy_index)
    
    # simulate the mouse click within the button coordinates
    qtbot.mouseClick(tree_view.viewport(),
                     QtCore.Qt.LeftButton,
                     pos=rect.topLeft())
    
    # simulate the mouse click within the button coordinates
    qtbot.mouseClick(tree_view.viewport(),
                     QtCore.Qt.LeftButton,
                     pos=rect.topLeft())
    
    assert True


@pytest.fixture
def db_selector(qtbot, window_new_project):
    
    # Get the select database button and click it
    database_button = \
        window_new_project.scenarioToolBar.widgetForAction(
                window_new_project.actionSelect_Database)
    qtbot.mouseClick(database_button, QtCore.Qt.LeftButton)
    
    db_selector = window_new_project._db_selector
    
    def db_selector_visible(): assert db_selector.isVisible()
    
    qtbot.waitUntil(db_selector_visible)
    
    n_creds = db_selector.listWidget.count()
    
    # Press the add button
    qtbot.mouseClick(db_selector.addButton,
                     QtCore.Qt.LeftButton)
    
    def added_cred(): assert db_selector.listWidget.count() == n_creds + 1
    
    qtbot.waitUntil(added_cred)
    
    assert n_creds == 1
    
    return db_selector


def test_credentials_add_delete(qtbot, mocker, db_selector):
    
    mocker.patch.object(QtGui.QMessageBox,
                        'question',
                        return_value=QtGui.QMessageBox.Yes)
    
    n_creds = db_selector.listWidget.count()
    
    # Add another credential
    qtbot.mouseClick(db_selector.addButton,
                     QtCore.Qt.LeftButton)
    
    def added_cred(): assert db_selector.listWidget.count() == n_creds + 1
    
    qtbot.waitUntil(added_cred)
    
    assert "unnamed-1" in db_selector._data_menu.get_available_databases()
    
    # Delete all credentials
    while db_selector.listWidget.count() > 0:
        
        # Select the last in the list and select
        item = db_selector.listWidget.item(db_selector.listWidget.count() - 1)
        rect = db_selector.listWidget.visualItemRect(item)
        qtbot.mouseClick(db_selector.listWidget.viewport(),
                         QtCore.Qt.LeftButton,
                         pos=rect.center())
                    
        qtbot.mouseClick(db_selector.deleteButton,
                         QtCore.Qt.LeftButton)
        
        def deleted_cred():
            assert db_selector.listWidget.count() == n_creds
        
        qtbot.waitUntil(deleted_cred)
        
        n_creds -= 1
    
    db_selector.close()


def test_select_database(qtbot, mocker, db_selector):
    
    mocker.patch('dtocean_app.main.DataMenu.select_database',
                 autospec=True)
    
    # Select the first in the list and apply
    db_selector.listWidget.setCurrentRow(0)
    
    item = db_selector.listWidget.item(0)
    rect = db_selector.listWidget.visualItemRect(item)
    qtbot.mouseClick(db_selector.listWidget.viewport(),
                     QtCore.Qt.LeftButton,
                     pos=rect.center())
    
    qtbot.mouseClick(
            db_selector.buttonBox.button(QtGui.QDialogButtonBox.Apply),
            QtCore.Qt.LeftButton)
    
    # Check for credentials
    def has_credentials():
        assert db_selector.topDynamicLabel.text() == item.text()
    
    qtbot.waitUntil(has_credentials)
    
    db_selector.close()


def test_deselect_database(qtbot, mocker, db_selector):
    
    mocker.patch('dtocean_app.main.DataMenu.select_database',
                 autospec=True)
    
    # Select the first in the list and apply
    db_selector.listWidget.setCurrentRow(0)
    
    item = db_selector.listWidget.item(0)
    rect = db_selector.listWidget.visualItemRect(item)
    qtbot.mouseClick(db_selector.listWidget.viewport(),
                     QtCore.Qt.LeftButton,
                     pos=rect.center())
    
    qtbot.mouseClick(
            db_selector.buttonBox.button(QtGui.QDialogButtonBox.Apply),
            QtCore.Qt.LeftButton)
    
    # Check for credentials
    def has_credentials():
        assert db_selector.topDynamicLabel.text() == item.text()
        
    qtbot.waitUntil(has_credentials)
    
    # Press reset button
    qtbot.mouseClick(
            db_selector.buttonBox.button(QtGui.QDialogButtonBox.Reset),
            QtCore.Qt.LeftButton)
    
    # Check for credentials
    def has_not_credentials():
        assert db_selector.topDynamicLabel.text() == "None"
        
    qtbot.waitUntil(has_not_credentials)
    
    db_selector.close()


def test_credentials_rename(qtbot, mocker, db_selector):
    
    n_creds = db_selector.listWidget.count()
    
    # Press the add button
    qtbot.mouseClick(db_selector.addButton,
                     QtCore.Qt.LeftButton)
    
    def added_cred(): assert db_selector.listWidget.count() == n_creds + 1
    
    qtbot.waitUntil(added_cred)
    
    # Select the last in the list and chnage its name
    db_selector.listWidget.setCurrentRow(db_selector.listWidget.count() - 1)
    
    editor = mocker.Mock()
    editor.text.return_value = "bob"
    
    db_selector._rename_database(editor, None)
    
    def check_name():
        assert "bob" in db_selector._data_menu.get_available_databases()
    
    qtbot.waitUntil(check_name)
    
    # Press the add button
    n_creds += 1
    
    qtbot.mouseClick(db_selector.addButton,
                     QtCore.Qt.LeftButton)
    
    def added_cred(): assert db_selector.listWidget.count() == n_creds + 1
    
    qtbot.waitUntil(added_cred)
    
    # Select the last in the list and change its name
    db_selector.listWidget.setCurrentRow(db_selector.listWidget.count() - 1)
    
    editor = mocker.Mock()
    editor.text.return_value = "bob"
    
    db_selector._rename_database(editor, None)
    
    def check_one_bob():
        assert db_selector._data_menu.get_available_databases(
                                                            ).count("bob") == 1
    
    qtbot.waitUntil(check_one_bob)
    
    db_selector.close()


def test_credentials_save(qtbot, mocker, db_selector):
    
    mocker.patch('dtocean_core.utils.database.UserDataDirectory',
                 autospec=True)
    
    old_count = db_selector.listWidget.count()
    
    # Press the add button
    qtbot.mouseClick(db_selector.addButton,
                     QtCore.Qt.LeftButton)
    
    def added_cred(): assert db_selector.listWidget.count() == old_count + 1
    
    qtbot.waitUntil(added_cred)
    
    # Select the last in the list and chnage its name
    test_cred = db_selector.listWidget.item(
                                            db_selector.listWidget.count() - 1)
    
    test_cred.setText("bob")
    editor = mocker.Mock()
    editor.text.return_value = "bob"
    
    db_selector._rename_database(editor, None)
    
    def check_name():
        assert "bob" in db_selector._data_menu.get_available_databases()
    
    qtbot.waitUntil(check_name)
    
    item = QtGui.QTableWidgetItem(str("bob"))
    db_selector.tableWidget.setItem(0, 1, item)
    
    def can_save(): assert db_selector.saveButton.isEnabled()
    
    qtbot.waitUntil(can_save)
    
    # Press the save button
    qtbot.mouseClick(db_selector.saveButton,
                     QtCore.Qt.LeftButton)
    
    def can_not_save(): assert not db_selector.saveButton.isEnabled()
    
    qtbot.waitUntil(can_not_save)
    
    db_selector.close()


def test_dump_load_database(mocker,
                            qtbot,
                            tmpdir,
                            window_new_project,
                            db_selector):
        
    mocker.patch('dtocean_core.utils.database.UserDataDirectory',
                 autospec=True)
    
    mocker.patch("dtocean_core.menu.check_host_port",
                 return_value=(True, "Mock connection returned"))
    
    mocker.patch('dtocean_app.menu.QtGui.QFileDialog.getExistingDirectory',
                 return_value=str(tmpdir))
    
    mocker.patch('dtocean_app.main.database_to_files',
                 autospec=True)
    
    mocker.patch('dtocean_app.main.database_from_files',
                 autospec=True)
    
    mocker.patch.object(QtGui.QMessageBox,
                        'warning',
                        return_value=QtGui.QMessageBox.Yes)
    
    # Select the first in the list and apply
    db_selector.listWidget.setCurrentRow(0)
    
    item = db_selector.listWidget.item(0)
    rect = db_selector.listWidget.visualItemRect(item)
    qtbot.mouseClick(db_selector.listWidget.viewport(),
                     QtCore.Qt.LeftButton,
                     pos=rect.center())
    
    qtbot.mouseClick(
            db_selector.buttonBox.button(QtGui.QDialogButtonBox.Apply),
            QtCore.Qt.LeftButton)
    
    shell = window_new_project._shell
    
    # Check for credentials
    def has_credentials():
        assert shell.project.get_database_credentials() is not None
        
    qtbot.waitUntil(has_credentials)
    
    # Activate dump
    qtbot.mouseClick(db_selector.dumpButton,
                     QtCore.Qt.LeftButton)
    
    qtbot.waitSignal(shell.database_convert_complete)
    
    def dump_enabled(): assert db_selector.dumpButton.isEnabled()
    
    qtbot.waitUntil(dump_enabled)
    
    # Activate load
    qtbot.mouseClick(db_selector.loadButton,
                     QtCore.Qt.LeftButton)
    
    qtbot.waitSignal(shell.database_convert_complete)
    
    def load_enabled(): assert db_selector.loadButton.isEnabled()
    
    qtbot.waitUntil(load_enabled)
    
    db_selector.close()


@pytest.fixture
def window_floating_wave(qtbot, window_new_project):
    
    # Pick up the available pipeline item
    test_var = window_new_project._pipeline_dock._find_controller(
                                    controller_title="Device Technology Type",
                                    controller_class=InputVarControl)
    
    # obtain the rectangular coordinates of the child item
    tree_view = window_new_project._pipeline_dock.treeView
    index = test_var._get_index_from_address()
    proxy_index = test_var._proxy.mapFromSource(index)
    rect = tree_view.visualRect(proxy_index)
    
    # simulate the mouse click within the button coordinates
    qtbot.mouseClick(tree_view.viewport(),
                     QtCore.Qt.LeftButton,
                     pos=rect.topLeft())
    
    selected_index = tree_view.selectedIndexes()[0]
    
    assert selected_index == proxy_index
    assert window_new_project._data_context._bottom_contents is not None
    assert isinstance(window_new_project._data_context._bottom_contents,
                      ListSelect)
                                  
    list_select = window_new_project._data_context._bottom_contents
    
    # Set the combo box to "Wave Floating" anc click OK
    idx = list_select.comboBox.findText("Wave Floating",
                                        QtCore.Qt.MatchFixedString)
    list_select.comboBox.setCurrentIndex(idx)

    qtbot.mouseClick(
                list_select.buttonBox.button(QtGui.QDialogButtonBox.Ok),
                QtCore.Qt.LeftButton)
    
    def check_status():
        
        # Pick up pipeline item again as it's been rebuilt
        test_var = window_new_project._pipeline_dock._find_controller(
                                    controller_title="Device Technology Type",
                                    controller_class=InputVarControl)
        
        assert test_var._status == "satisfied"
    
    qtbot.waitUntil(check_status)
    
    return window_new_project


def test_set_device_type(window_floating_wave):
    
    test_var = window_floating_wave._pipeline_dock._find_controller(
                                    controller_title="Device Technology Type",
                                    controller_class=InputVarControl)
    
    assert test_var._status == "satisfied"


def test_export_data(qtbot, mocker, tmpdir, window_floating_wave):
    
    # File path
    datastate_file_name = "my_datastate.dts"
    datastate_file_path = os.path.join(str(tmpdir), datastate_file_name)
                      
    mocker.patch.object(QtGui.QFileDialog,
                        'getSaveFileName',
                        return_value=datastate_file_path)
    
    # Export data
    menu_click(qtbot,
               window_floating_wave,
               window_floating_wave.menuData,
               "actionExport")
    
    def file_saved(): assert os.path.isfile(datastate_file_path)
    
    qtbot.waitUntil(file_saved)
    
    assert os.path.isfile(datastate_file_path)


def test_export_data_mask(qtbot, mocker, tmpdir, window_floating_wave):
    
    # File path
    datastate_file_name = "my_datastate.dts"
    datastate_file_path = os.path.join(str(tmpdir), datastate_file_name)
                      
    mocker.patch.object(QtGui.QFileDialog,
                        'getSaveFileName',
                        return_value=datastate_file_path)
    
    # Export data
    menu_click(qtbot,
               window_floating_wave,
               window_floating_wave.menuData,
               "actionExport_mask")
    
    def file_saved(): assert os.path.isfile(datastate_file_path)
    
    qtbot.waitUntil(file_saved)
    
    assert os.path.isfile(datastate_file_path)


def test_import_data(qtbot, mocker, tmpdir, window_floating_wave):

    # File path
    datastate_file_name = "my_datastate.dts"
    datastate_file_path = os.path.join(str(tmpdir), datastate_file_name)
    
    mocker.patch.object(QtGui.QFileDialog,
                        'getSaveFileName',
                        return_value=datastate_file_path)
    
    mocker.patch.object(QtGui.QFileDialog,
                        'getOpenFileName',
                        return_value=datastate_file_path)
    
    # Export data
    menu_click(qtbot,
               window_floating_wave,
               window_floating_wave.menuData,
               "actionExport")
    
    def file_saved(): assert os.path.isfile(datastate_file_path)
    
    qtbot.waitUntil(file_saved)
    
    # Open a new project
    new_project_button = window_floating_wave.fileToolBar.widgetForAction(
                                            window_floating_wave.actionNew)
    qtbot.mouseClick(new_project_button, QtCore.Qt.LeftButton)
    
    # Import data
    menu_click(qtbot,
               window_floating_wave,
               window_floating_wave.menuData,
               "actionImport")
    
    def check_status():
        
        # Pick up pipeline item again as it's been rebuilt
        test_var = window_floating_wave._pipeline_dock._find_controller(
                                    controller_title="Device Technology Type",
                                    controller_class=InputVarControl)
        
        assert test_var._status == "satisfied"
    
    # Check the test variable
    qtbot.waitUntil(check_status)
    
    assert True


def test_import_data_skip(qtbot, mocker, tmpdir, window_floating_wave):

    # File path
    datastate_file_name = "my_datastate.dts"
    datastate_file_path = os.path.join(str(tmpdir), datastate_file_name)
    
    mocker.patch.object(QtGui.QFileDialog,
                        'getSaveFileName',
                        return_value=datastate_file_path)
    
    mocker.patch.object(QtGui.QFileDialog,
                        'getOpenFileName',
                        return_value=datastate_file_path)
    
    # Export data
    menu_click(qtbot,
               window_floating_wave,
               window_floating_wave.menuData,
               "actionExport")
    
    def file_saved(): assert os.path.isfile(datastate_file_path)
    
    qtbot.waitUntil(file_saved)
    
    # Open a new project
    new_project_button = window_floating_wave.fileToolBar.widgetForAction(
                                            window_floating_wave.actionNew)
    qtbot.mouseClick(new_project_button, QtCore.Qt.LeftButton)
    
    # Import data
    menu_click(qtbot,
               window_floating_wave,
               window_floating_wave.menuData,
               "actionImport_skip")
    
    def check_status():
        
        # Pick up pipeline item again as it's been rebuilt
        test_var = window_floating_wave._pipeline_dock._find_controller(
                                    controller_title="Device Technology Type",
                                    controller_class=InputVarControl)
        
        assert test_var._status == "satisfied"
    
    # Check the test variable
    qtbot.waitUntil(check_status)
    
    assert True


def test_tool_connect(mocker, qtbot, window_floating_wave):
    
    spy = mocker.spy(MockTool, "destroy_widget")
    
    def handle_dialog():
        window_floating_wave._tool_widget.close()
    
    action = window_floating_wave.menuTools.actions()[1]
    assert str(action.text()) == "Mock Tool"
    assert action.isEnabled()
    
    QtCore.QTimer.singleShot(500, handle_dialog)
    menu_click(qtbot,
               window_floating_wave,
               window_floating_wave.menuTools,
               action.objectName())
    
    def no_thread_tool():
        assert window_floating_wave._thread_tool is None
    
    qtbot.waitUntil(no_thread_tool)
    
    def no_tool_widget():
        assert  window_floating_wave._tool_widget is None
    
    qtbot.waitUntil(no_tool_widget)
    
    assert window_floating_wave._tool_widget is None
    assert spy.call_count == 1


@pytest.fixture
def window_with_pipeline(qtbot, window_floating_wave):
    
    # Initiate the pipeline
    init_pipeline_button = \
        window_floating_wave.scenarioToolBar.widgetForAction(
                window_floating_wave.actionInitiate_Pipeline)
    qtbot.mouseClick(init_pipeline_button, QtCore.Qt.LeftButton)
    
    data_check = window_floating_wave._data_check
    
    def data_check_visible(): assert data_check.isVisible()
    
    qtbot.waitUntil(data_check_visible)
    
    qtbot.mouseClick(data_check.buttonBox.button(QtGui.QDialogButtonBox.Ok),
                     QtCore.Qt.LeftButton)
    
    def check_dataflow():
        assert window_floating_wave.actionInitiate_Dataflow.isEnabled()
    
    qtbot.waitUntil(check_dataflow)
    
    return window_floating_wave


def test_initiate_pipeline(window_with_pipeline):
    assert window_with_pipeline.actionInitiate_Dataflow.isEnabled()


@pytest.fixture
def window_dataflow_empty(qtbot, window_with_pipeline):
    
    # Initiate the dataflow
    init_pipeline_button = \
        window_with_pipeline.scenarioToolBar.widgetForAction(
                            window_with_pipeline.actionInitiate_Dataflow)
    qtbot.mouseClick(init_pipeline_button, QtCore.Qt.LeftButton)
    
    data_check = window_with_pipeline._data_check
    
    def data_check_visible(): assert data_check.isVisible()
    
    qtbot.waitUntil(data_check_visible)
    
    qtbot.mouseClick(data_check.buttonBox.button(QtGui.QDialogButtonBox.Ok),
                     QtCore.Qt.LeftButton)
    
    def save_enabled():
        assert window_with_pipeline.actionSave.isEnabled()
    
    qtbot.waitUntil(save_enabled)
    
    return window_with_pipeline


def test_empty_project_reload(qtbot, 
                              mocker,
                              tmp_path,
                              window_dataflow_empty):
    
    dto_file = tmp_path / "test.dto"
    dto_file_path = str(dto_file)
    
    mocker.patch.object(QtGui.QFileDialog,
                        'getSaveFileName',
                        return_value=dto_file_path)
    
    mocker.patch.object(QtGui.QFileDialog,
                        'getOpenFileName',
                        return_value=dto_file_path)
    
    # Save the simulation
    save_button = window_dataflow_empty.fileToolBar.widgetForAction(
                                            window_dataflow_empty.actionSave)
    qtbot.mouseClick(save_button, QtCore.Qt.LeftButton)
    
    def dto_file_saved():
        assert dto_file.is_file()
    
    qtbot.waitUntil(dto_file_saved)
    
    # Close the project
    close_button = window_dataflow_empty.fileToolBar.widgetForAction(
                                            window_dataflow_empty.actionClose)
    qtbot.mouseClick(close_button, QtCore.Qt.LeftButton)
    
    def close_button_not_enabled(): assert not close_button.isEnabled()
    
    qtbot.waitUntil(close_button_not_enabled)
    
    # Open the project
    open_button = window_dataflow_empty.fileToolBar.widgetForAction(
                                            window_dataflow_empty.actionOpen)
    qtbot.mouseClick(open_button, QtCore.Qt.LeftButton)
    
    def close_button_enabled(): assert close_button.isEnabled()
    
    qtbot.waitUntil(close_button_enabled)
    
    assert close_button.isEnabled()


@pytest.fixture
def window_dataflow_module(qtbot, window_with_pipeline):
    
    # Add a module
    add_modules_button = \
        window_with_pipeline.simulationToolBar.widgetForAction(
                                    window_with_pipeline.actionAdd_Modules)
    qtbot.mouseClick(add_modules_button, QtCore.Qt.LeftButton)
    
    module_shuttle = window_with_pipeline._module_shuttle
    
    def add_modules_visible(): assert module_shuttle.isVisible()
    
    qtbot.waitUntil(add_modules_visible)
    
    # Fake click on last left item
    module_shuttle._left_index = module_shuttle._left_model.rowCount() - 1
    
    # Click "Add" then "OK"
    qtbot.mouseClick(module_shuttle.addButton,
                     QtCore.Qt.LeftButton)
    
    def module_on_right(): assert module_shuttle._get_right_data()
    
    qtbot.waitUntil(module_on_right)
    
    mod_ok_button = module_shuttle.buttonBox.button(QtGui.QDialogButtonBox.Ok)
    qtbot.mouseClick(mod_ok_button, QtCore.Qt.LeftButton)
    
    def add_modules_not_visible(): assert not module_shuttle.isVisible()
    
    qtbot.waitUntil(add_modules_not_visible)
    
    # Reopen module shuttle and check module is still selected
    qtbot.mouseClick(add_modules_button, QtCore.Qt.LeftButton)
    qtbot.waitUntil(add_modules_visible)
    qtbot.waitUntil(module_on_right)
    qtbot.mouseClick(mod_ok_button, QtCore.Qt.LeftButton)
    qtbot.waitUntil(add_modules_not_visible)
    
    # Initiate the dataflow
    init_pipeline_button = \
        window_with_pipeline.scenarioToolBar.widgetForAction(
                            window_with_pipeline.actionInitiate_Dataflow)
    qtbot.mouseClick(init_pipeline_button, QtCore.Qt.LeftButton)
    
    data_check = window_with_pipeline._data_check
    
    def data_check_visible(): assert data_check.isVisible()
    
    qtbot.waitUntil(data_check_visible)
    
    qtbot.mouseClick(data_check.buttonBox.button(QtGui.QDialogButtonBox.Ok),
                     QtCore.Qt.LeftButton)
    
    def check_run_current():
        assert window_with_pipeline.actionRun_Current.isEnabled()
    
    qtbot.waitUntil(check_run_current)
    
    def check_module_active():
        
        # Pick up pipeline item again as it's been rebuilt
        test_control = window_with_pipeline._pipeline_dock._find_controller(
                                            controller_title="Mock Module")
        
        assert test_control is not None
    
    qtbot.waitUntil(check_module_active)
    
    return window_with_pipeline


def test_dataflow_module(window_dataflow_module):
    test_control = window_dataflow_module._pipeline_dock._find_controller(
                                            controller_title="Mock Module")
    assert test_control is not None


# These dock tests below should probably be split into a separate files, with 
# the shell mocked to a useful state.


def test_pipeline_context_menu(mocker, qtbot, window_dataflow_module):
    
    menu = mocker.MagicMock()
    mocker.patch('dtocean_app.pipeline.QtGui.QMenu',
                 return_value=menu)
    
    pipeline_dock = window_dataflow_module._pipeline_dock
    mod_control = pipeline_dock._find_controller(
                                    controller_title="Mock Module",
                                    controller_class=InputBranchControl)
    
    index = mod_control._get_index_from_address()
    proxy_index = mod_control._proxy.mapFromSource(index)
    rect = pipeline_dock.treeView.visualRect(proxy_index)
    event = QtGui.QContextMenuEvent(QtGui.QContextMenuEvent.Mouse, 
                                    rect.center())
    QtGui.QApplication.postEvent(pipeline_dock.treeView.viewport(),
                                 event)
    
    def menu_exec_called():
        assert menu.exec_.called
    
    qtbot.waitUntil(menu_exec_called)
    
    expected_actions = ['Inspect', 'Reset', 'Load test data...']
    actions = [x.args[0] for x in menu.addAction.call_args_list]
    
    assert actions == expected_actions


def test_set_simulation_title(mocker, qtbot, window_dataflow_module):
    
    # Close the pipeline
    window_dataflow_module._pipeline_dock.close()
    
    def pipeline_not_visible():
        assert not window_dataflow_module._pipeline_dock.isVisible()
    
    qtbot.waitUntil(pipeline_not_visible)
    
    # Fake change of simulation name
    window_dataflow_module._simulation_dock.listWidget.setCurrentRow(0)
    editor = mocker.Mock()
    editor.text.return_value = "bob"
    
    window_dataflow_module._simulation_dock._catch_edit(editor, None)
    
    def check_name():
    
        # Pick up the default simulation
        test_sim = window_dataflow_module._simulation_dock.listWidget.item(0)
        
        assert test_sim._title == "bob"
    
    qtbot.waitUntil(check_name)
    
    assert window_dataflow_module._shell.project.get_simulation_title() == "bob"


def test_simulation_context_menu(mocker, qtbot, window_dataflow_module):
    
    menu = mocker.MagicMock()
    mocker.patch('dtocean_app.simulation.QtGui.QMenu',
                 return_value=menu)
    
    # Close the pipeline
    window_dataflow_module._pipeline_dock.close()
    
    def pipeline_not_visible():
        assert not window_dataflow_module._pipeline_dock.isVisible()
    
    qtbot.waitUntil(pipeline_not_visible)
    
    # Clone the simulation
    simulation_dock = window_dataflow_module._simulation_dock
    default_sim = simulation_dock.listWidget.item(0)
    
    rect = simulation_dock.listWidget.visualItemRect(default_sim)
    event = QtGui.QContextMenuEvent(QtGui.QContextMenuEvent.Mouse, 
                                    rect.center())
    QtGui.QApplication.postEvent(simulation_dock.listWidget.viewport(),
                                 event)
    
    def menu_exec_called():
        assert menu.exec_.called
    
    qtbot.waitUntil(menu_exec_called)
    
    expected_actions = ['Clone', 'Delete']
    actions = [x.args[0] for x in menu.addAction.call_args_list]
    
    assert actions == expected_actions


@pytest.fixture
def window_plot_context(qtbot, window_dataflow_module):
    
    controller = window_dataflow_module._pipeline_dock._find_controller(
                    controller_title="Annual Energy Production Per Device",
                    controller_class=InputVarControl)
    
    values = {"a": 5,
              "b": 10}
    window_dataflow_module._read_raw(controller._variable, values)
    
    # obtain the rectangular coordinates of the child item
    tree_view = window_dataflow_module._pipeline_dock.treeView
    index = controller._get_index_from_address()
    proxy_index = controller._proxy.mapFromSource(index)
    rect = tree_view.visualRect(proxy_index)
    
    # simulate the mouse click within the button coordinates
    qtbot.mouseClick(tree_view.viewport(),
                     QtCore.Qt.LeftButton,
                     pos=rect.topLeft())
    
    def has_data_bottom_contents():
        bottom_contents = window_dataflow_module._data_context._bottom_contents
        assert bottom_contents is not None
    
    qtbot.waitUntil(has_data_bottom_contents)
    
    window_dataflow_module.actionPlots.trigger()
    
    def has_plot_bottom_contents():
        bottom_contents = window_dataflow_module._plot_context._bottom_contents
        assert bottom_contents is not None
    
    qtbot.waitUntil(has_plot_bottom_contents)
    
    return window_dataflow_module


def test_plot_context_visible(window_plot_context):
    assert window_plot_context._plot_context._bottom_contents is not None


def test_plot_context_clear(qtbot, window_plot_context):
    
    controller = window_plot_context._pipeline_dock._find_controller(
                    controller_title="Bathymetry",
                    controller_class=InputVarControl)
    
    # obtain the rectangular coordinates of the child item
    tree_view = window_plot_context._pipeline_dock.treeView
    index = controller._get_index_from_address()
    proxy_index = controller._proxy.mapFromSource(index)
    rect = tree_view.visualRect(proxy_index)
    
    # simulate the mouse click within the button coordinates
    qtbot.mouseClick(tree_view.viewport(),
                     QtCore.Qt.LeftButton,
                     pos=rect.topLeft())
    
    def clear_plot_bottom_contents():
        assert window_plot_context._plot_context._bottom_contents is None
    
    qtbot.waitUntil(clear_plot_bottom_contents)
    
    assert window_plot_context._plot_context._bottom_contents is None


@pytest.fixture
def window_dataflow_theme(qtbot, window_with_pipeline):
    
    # Add a theme
    add_themes_button = \
        window_with_pipeline.simulationToolBar.widgetForAction(
                                window_with_pipeline.actionAdd_Assessment)
    qtbot.mouseClick(add_themes_button, QtCore.Qt.LeftButton)
    
    assessment_shuttle = window_with_pipeline._assessment_shuttle
    
    def add_themes_visible(): assert assessment_shuttle.isVisible()
    
    qtbot.waitUntil(add_themes_visible)
    
    # Fake click on last left item
    assessment_shuttle._left_index = \
                                assessment_shuttle._left_model.rowCount() - 1
    
    # Click "Add" then "OK"
    qtbot.mouseClick(assessment_shuttle.addButton,
                     QtCore.Qt.LeftButton)
    
    def module_on_right(): assert assessment_shuttle._get_right_data()
    
    qtbot.waitUntil(module_on_right)
    
    mod_ok_button = assessment_shuttle.buttonBox.button(
                                                    QtGui.QDialogButtonBox.Ok)
    qtbot.mouseClick(mod_ok_button, QtCore.Qt.LeftButton)
    
    def add_themes_not_visible(): assert not assessment_shuttle.isVisible()
    
    qtbot.waitUntil(add_themes_not_visible)
    
    # Reopen module shuttle and check module is still selected
    qtbot.mouseClick(add_themes_button, QtCore.Qt.LeftButton)
    qtbot.waitUntil(add_themes_visible)
    qtbot.waitUntil(module_on_right)
    qtbot.mouseClick(mod_ok_button, QtCore.Qt.LeftButton)
    qtbot.waitUntil(add_themes_not_visible)
    
    # Initiate the dataflow
    init_pipeline_button = \
        window_with_pipeline.scenarioToolBar.widgetForAction(
                            window_with_pipeline.actionInitiate_Dataflow)
    qtbot.mouseClick(init_pipeline_button, QtCore.Qt.LeftButton)
    
    data_check = window_with_pipeline._data_check
    
    def data_check_visible(): assert data_check.isVisible()
    
    qtbot.waitUntil(data_check_visible)
    
    qtbot.mouseClick(data_check.buttonBox.button(QtGui.QDialogButtonBox.Ok),
                     QtCore.Qt.LeftButton)
    
    def check_run_themes():
        assert window_with_pipeline.actionRun_Themes.isEnabled()
    
    qtbot.waitUntil(check_run_themes)
    
    def check_theme_active():
        
        # Pick up pipeline item again as it's been rebuilt
        test_control = window_with_pipeline._pipeline_dock._find_controller(
                                            controller_title="Mock Theme")
        
        assert test_control is not None
    
    qtbot.waitUntil(check_theme_active)
    
    return window_with_pipeline


def test_dataflow_theme(window_dataflow_theme):
    test_control = window_dataflow_theme._pipeline_dock._find_controller(
                                            controller_title="Mock Theme")
    assert test_control is not None


@pytest.fixture
def window_two_simulations(qtbot, window_dataflow_module):
    
    # Close the pipeline
    window_dataflow_module._pipeline_dock.close()
    
    def pipeline_not_visible():
        assert not window_dataflow_module._pipeline_dock.isVisible()
    
    qtbot.waitUntil(pipeline_not_visible)
    
    # Fake clone the simulation
    simulation_dock = window_dataflow_module._simulation_dock
    simulation_dock._clone_current(window_dataflow_module._shell)
    
    def has_two_simulations():
        assert simulation_dock.listWidget.count() == 2
    
    qtbot.waitUntil(has_two_simulations)
    
    return window_dataflow_module


def test_simulation_clone(qtbot, window_two_simulations):
    
    # Check the new simulation name
    project = window_two_simulations._shell.project
    
    assert project.get_simulation_title() == "Default Clone 1"


def test_simulation_clone_set_title_fail(mocker,
                                         qtbot,
                                         window_two_simulations):
    
    simulation_dock = window_two_simulations._simulation_dock
    test_sim = simulation_dock.listWidget.item(1)
    
    # Try (and fail) to set the new simulation title to Default
    editor = mocker.Mock()
    editor.text.return_value = "Default"
    
    simulation_dock.listWidget.setCurrentRow(1)
    simulation_dock._catch_edit(editor, None)
    
    def check_name():
        assert test_sim._title == "Default Clone 1"
    
    qtbot.waitUntil(check_name)
    
    assert test_sim._title == "Default Clone 1"


def test_simulation_clone_select(qtbot, window_two_simulations):
    
    simulation_dock = window_two_simulations._simulation_dock
    
    # Select the default simulation
    item = simulation_dock.listWidget.item(0)
    rect = simulation_dock.listWidget.visualItemRect(item)
    
    qtbot.mouseClick(simulation_dock.listWidget.viewport(),
                     QtCore.Qt.LeftButton,
                     pos=rect.center())
    
    project = window_two_simulations._shell.project
    
    def is_active_simulation():
        assert project.get_simulation_title() == "Default"
    
    qtbot.waitUntil(is_active_simulation)
    
    assert project.get_simulation_title() == "Default"


def test_simulation_clone_delete(qtbot, window_two_simulations):
    
    simulation_dock = window_two_simulations._simulation_dock
    simulation_dock.listWidget.setCurrentRow(1)
    simulation_dock._delete_current(window_two_simulations._shell)
    
    def has_one_simulation():
        assert simulation_dock.listWidget.count() == 1
    
    qtbot.waitUntil(has_one_simulation)
    
    project = window_two_simulations._shell.project
    
    assert project.get_simulation_title() == "Default"


def test_simulation_clone_again(qtbot, window_two_simulations):
    
    simulation_dock = window_two_simulations._simulation_dock
    simulation_dock.listWidget.setCurrentRow(1)
    simulation_dock._clone_current(window_two_simulations._shell)
    
    def has_three_simulations():
        assert simulation_dock.listWidget.count() == 3
    
    qtbot.waitUntil(has_three_simulations)
    
    test_sim = simulation_dock.listWidget.item(2)
    
    assert test_sim._title == "Default Clone 2"


def test_simulation_active_mods_warn(caplog,
                                     mocker,
                                     qtbot,
                                     window_two_simulations):
    
    mocker.patch("dtocean_app.main.ModuleMenu.get_active",
                 return_value=["mock"],
                 autospec=True)
    
    simulation_dock = window_two_simulations._simulation_dock
    
    # Select the default simulation
    item = simulation_dock.listWidget.item(0)
    rect = simulation_dock.listWidget.visualItemRect(item)
    
    with caplog_for_logger(caplog, 'dtocean_app'):
        
        qtbot.mouseClick(simulation_dock.listWidget.viewport(),
                         QtCore.Qt.LeftButton,
                         pos=rect.center())
        
        project = window_two_simulations._shell.project
        
        def is_active_simulation():
            assert project.get_simulation_title() == "Default"
        
        qtbot.waitUntil(is_active_simulation)
    
    assert "differ from those originally selected" in caplog.text


@pytest.fixture
def window_two_theme_simulations(qtbot, window_dataflow_theme):
    
    # Close the pipeline
    window_dataflow_theme._pipeline_dock.close()
    
    def pipeline_not_visible():
        assert not window_dataflow_theme._pipeline_dock.isVisible()
    
    qtbot.waitUntil(pipeline_not_visible)
    
    # Fake clone the simulation
    simulation_dock = window_dataflow_theme._simulation_dock
    simulation_dock._clone_current(window_dataflow_theme._shell)
    
    def has_two_simulations():
        assert simulation_dock.listWidget.count() == 2
    
    qtbot.waitUntil(has_two_simulations)
    
    return window_dataflow_theme


def test_theme_simulation_clone_select(qtbot,
                                       window_two_theme_simulations):
    
    simulation_dock = window_two_theme_simulations._simulation_dock
    
    # Select the default simulation
    item = simulation_dock.listWidget.item(0)
    rect = simulation_dock.listWidget.visualItemRect(item)
    
    qtbot.mouseClick(simulation_dock.listWidget.viewport(),
                     QtCore.Qt.LeftButton,
                     pos=rect.center())
    
    project = window_two_theme_simulations._shell.project
    
    def is_active_simulation():
        assert project.get_simulation_title() == "Default"
    
    qtbot.waitUntil(is_active_simulation)
    
    assert project.get_simulation_title() == "Default"


def test_simulation_active_themes_warn(caplog,
                                       mocker,
                                       qtbot,
                                       window_two_theme_simulations):
    
    mocker.patch("dtocean_app.main.ThemeMenu.get_active",
                 return_value=["mock"],
                 autospec=True)
    
    simulation_dock = window_two_theme_simulations._simulation_dock
    
    # Select the default simulation
    item = simulation_dock.listWidget.item(0)
    rect = simulation_dock.listWidget.visualItemRect(item)
    
    with caplog_for_logger(caplog, 'dtocean_app'):
        
        qtbot.mouseClick(simulation_dock.listWidget.viewport(),
                         QtCore.Qt.LeftButton,
                         pos=rect.center())
        
        project = window_two_theme_simulations._shell.project
        
        def is_active_simulation():
            assert project.get_simulation_title() == "Default"
        
        qtbot.waitUntil(is_active_simulation)
    
    assert "differ from those originally selected" in caplog.text


@pytest.mark.parametrize("ext", ["dto", "prj"])
def test_project_save(qtbot, mocker, tmp_path, window_dataflow_module, ext):
    
    dto_file = tmp_path / "test.{}".format(ext)
    mocker.patch.object(QtGui.QFileDialog,
                        'getSaveFileName',
                        return_value=str(dto_file))
    
    # Save the simulation
    save_button = window_dataflow_module.fileToolBar.widgetForAction(
                                            window_dataflow_module.actionSave)
    qtbot.mouseClick(save_button, QtCore.Qt.LeftButton)

    def dto_file_saved():
        assert dto_file.is_file()
    
    qtbot.waitUntil(dto_file_saved)
    
    assert dto_file.is_file()


def test_project_close(qtbot, window_dataflow_module):
    
    # Close the project
    close_button = window_dataflow_module.fileToolBar.widgetForAction(
                                            window_dataflow_module.actionClose)
    qtbot.mouseClick(close_button, QtCore.Qt.LeftButton)
    
    def close_button_not_enabled(): assert not close_button.isEnabled()
    
    qtbot.waitUntil(close_button_not_enabled)
    
    assert not close_button.isEnabled()


def test_modify_variable(qtbot, window_dataflow_module):
    
    # Modify a variable
    test_var = window_dataflow_module._pipeline_dock._find_controller(
                                    controller_title="Device Rated Power",
                                    controller_class=InputVarControl)
    
    # obtain the rectangular coordinates of the child item
    tree_view = window_dataflow_module._pipeline_dock.treeView
    index = test_var._get_index_from_address()
    proxy_index = test_var._proxy.mapFromSource(index)
    rect = tree_view.visualRect(proxy_index)
    
    # simulate the mouse click within the button coordinates
    qtbot.mouseClick(tree_view.viewport(),
                     QtCore.Qt.LeftButton,
                     pos=rect.topLeft())
    
    def is_float_select():
        assert isinstance(window_dataflow_module._data_context._bottom_contents,
                          FloatSelect)
    
    qtbot.waitUntil(is_float_select)
    
    float_select = window_dataflow_module._data_context._bottom_contents
    
    # Set the value to 1 and click OK
    float_select.doubleSpinBox.setValue(1)

    qtbot.mouseClick(
                float_select.buttonBox.button(QtGui.QDialogButtonBox.Ok),
                QtCore.Qt.LeftButton)
    
    def check_status_two():
        
        # Pick up pipeline item again as it's been rebuilt
        test_var = window_dataflow_module._pipeline_dock._find_controller(
                                    controller_title="Device Rated Power",
                                    controller_class=InputVarControl)
        
        assert test_var._status == "satisfied"
    
    qtbot.waitUntil(check_status_two)
    
    def title_unsaved(): assert "*" in window_dataflow_module.windowTitle()
    
    qtbot.waitUntil(title_unsaved)
    
    assert "*" in window_dataflow_module.windowTitle()


def test_strategy_select(qtbot, window_dataflow_module):
    
    # Add a strategy
    add_strategy_button = \
                window_dataflow_module.simulationToolBar.widgetForAction(
                                    window_dataflow_module.actionAdd_Strategy)
    qtbot.mouseClick(add_strategy_button, QtCore.Qt.LeftButton)
    
    strategy_manager = window_dataflow_module._strategy_manager
    
    def strategy_manager_visible(): assert strategy_manager.isVisible()
    
    qtbot.waitUntil(strategy_manager_visible)
    
    assert strategy_manager.isVisible()


def test_strategy_no_modules(qtbot, window_dataflow_theme):
    
    strategy_manager = window_dataflow_theme._strategy_manager
    
    if "Basic" not in strategy_manager.get_available():
        pytest.skip("Test requires Basic strategy")
    
    # Add a strategy
    add_strategy_button = \
                window_dataflow_theme.simulationToolBar.widgetForAction(
                                    window_dataflow_theme.actionAdd_Strategy)
    qtbot.mouseClick(add_strategy_button, QtCore.Qt.LeftButton)
    
    def strategy_manager_visible(): assert strategy_manager.isVisible()
    
    qtbot.waitUntil(strategy_manager_visible)
    
    # Click on first strategy and apply
    item = strategy_manager.listWidget.item(0)
    rect = strategy_manager.listWidget.visualItemRect(item)
    qtbot.mouseClick(strategy_manager.listWidget.viewport(),
                     QtCore.Qt.LeftButton,
                     pos=rect.center())
    
    def apply_enabled():
        assert strategy_manager.applyButton.isEnabled()
        
    qtbot.waitUntil(apply_enabled)
    
    qtbot.mouseClick(strategy_manager.applyButton,
                     QtCore.Qt.LeftButton)
    
    def strategy_set():
        assert str(strategy_manager.topDynamicLabel.text()) == str(item.text())
    
    qtbot.waitUntil(strategy_set)
    
    # Close the dialog
    qtbot.mouseClick(strategy_manager.closeButton,
                     QtCore.Qt.LeftButton)
    
    assert not window_dataflow_theme.actionRun_Strategy.isEnabled()


@pytest.fixture
def strategy_manager_basic(qtbot, window_dataflow_module):
    
    strategy_manager = window_dataflow_module._strategy_manager
    
    if "Basic" not in strategy_manager.get_available():
        pytest.skip("Test requires Basic strategy")
    
    # Add a strategy
    add_strategy_button = \
                window_dataflow_module.simulationToolBar.widgetForAction(
                                    window_dataflow_module.actionAdd_Strategy)
    qtbot.mouseClick(add_strategy_button, QtCore.Qt.LeftButton)
    
    def strategy_manager_visible(): assert strategy_manager.isVisible()
    
    qtbot.waitUntil(strategy_manager_visible)
    
    # Click on first strategy and apply
    item = strategy_manager.listWidget.item(0)
    rect = strategy_manager.listWidget.visualItemRect(item)
    qtbot.mouseClick(strategy_manager.listWidget.viewport(),
                     QtCore.Qt.LeftButton,
                     pos=rect.center())
    
    def apply_enabled():
        assert strategy_manager.applyButton.isEnabled()
        
    qtbot.waitUntil(apply_enabled)
    
    qtbot.mouseClick(strategy_manager.applyButton,
                     QtCore.Qt.LeftButton)
    
    def strategy_set():
        assert str(strategy_manager.topDynamicLabel.text()) == str(item.text())
    
    qtbot.waitUntil(strategy_set)
    
    yield strategy_manager
    
    # Close the dialog
    qtbot.mouseClick(strategy_manager.closeButton,
                     QtCore.Qt.LeftButton)


def test_strategy_reload(qtbot, 
                         mocker,
                         tmp_path,
                         window_dataflow_module,
                         strategy_manager_basic):
    
    dto_file = tmp_path / "test.dto"
    dto_file_path = str(dto_file)
    
    mocker.patch.object(QtGui.QFileDialog,
                        'getSaveFileName',
                        return_value=dto_file_path)
    
    mocker.patch.object(QtGui.QFileDialog,
                        'getOpenFileName',
                        return_value=dto_file_path)
    
    # Close the dialog
    qtbot.mouseClick(strategy_manager_basic.closeButton,
                     QtCore.Qt.LeftButton)
    
    # Save the simulation
    save_button = window_dataflow_module.fileToolBar.widgetForAction(
                                            window_dataflow_module.actionSave)
    qtbot.mouseClick(save_button, QtCore.Qt.LeftButton)
    
    def dto_file_saved():
        assert dto_file.is_file()
    
    qtbot.waitUntil(dto_file_saved)
    
    # Close the project
    close_button = window_dataflow_module.fileToolBar.widgetForAction(
                                            window_dataflow_module.actionClose)
    qtbot.mouseClick(close_button, QtCore.Qt.LeftButton)
    
    def close_button_not_enabled(): assert not close_button.isEnabled()
    
    qtbot.waitUntil(close_button_not_enabled)
    
    # Open the project
    open_button = window_dataflow_module.fileToolBar.widgetForAction(
                                            window_dataflow_module.actionOpen)
    qtbot.mouseClick(open_button, QtCore.Qt.LeftButton)
    
    def close_button_enabled(): assert close_button.isEnabled()
    
    qtbot.waitUntil(close_button_enabled)
    
    # Reopen strategy manager and check value
    add_strategy_button = \
                window_dataflow_module.simulationToolBar.widgetForAction(
                                    window_dataflow_module.actionAdd_Strategy)
    qtbot.mouseClick(add_strategy_button, QtCore.Qt.LeftButton)
    
    def strategy_manager_visible():
        assert strategy_manager_basic.isVisible()
    
    qtbot.waitUntil(strategy_manager_visible)
    
    assert str(strategy_manager_basic.topDynamicLabel.text()) == "Basic"


def menu_click(qtbot, main_window, menu, action_name):
        
    qtbot.keyClick(main_window, menu.title().at(1).toLatin1(),
                   QtCore.Qt.AltModifier)
                
    for action in menu.actions():
        
        if not action.objectName(): continue
            
        if action.objectName() and action.objectName() == action_name:
            qtbot.keyClick(menu, QtCore.Qt.Key_Enter)
            return
        
        qtbot.wait(200)
        qtbot.keyClick(menu, QtCore.Qt.Key_Down)
        
    errStr = "Action '{}' not found in menu '{}'".format(action_name,
                                                         menu.objectName())
    raise ValueError(errStr)
