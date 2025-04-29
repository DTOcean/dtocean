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

# Set up logging
import logging

module_logger = logging.getLogger(__name__)

from PyQt4 import QtGui, QtCore

from dtocean_core.extensions import StrategyManager, ToolManager

from . import strategies, tools
from .widgets.dialogs import ListFrameEditor, Message
from .widgets.display import MPLWidget
from .widgets.output import OutputDataTable


class GUIStrategyManager(ListFrameEditor, StrategyManager):
    
    strategy_selected = QtCore.pyqtSignal(object)
    
    """Strategy discovery"""
    
    def __init__(self, shell, parent=None):
        
        StrategyManager.__init__(self, strategies, "GUIStrategy")
        ListFrameEditor.__init__(self, parent, "Strategy Manager")
        self._shell = shell
        self._strategy = None
        self._last_df = None
        self._last_selected = None
        
        # Store widget handles
        self._strategy_widget = None
        
        return
        
    def _init_ui(self, title=None):
        
        super(GUIStrategyManager, self)._init_ui(title)
                
        self._init_labels("Current Strategy:",
                          "Available strategies:",
                          "Configuration:")
        self._set_dynamic_label("None")
        self._init_list()
        
        self.listWidget.itemClicked.connect(self._update_configuration)
        self.resetButton.clicked.connect(self._reset_strategy)
        self.applyButton.clicked.connect(self._configure_strategy)
        
        self.applyButton.setDisabled(True)
        
        return
        
    def _init_list(self):
        
        available_strategies = self.get_available()
        super(GUIStrategyManager, self)._update_list(available_strategies)
        
        return
        
    @QtCore.pyqtSlot()
    def _config_set_ui_switch(self):
        
        self.applyButton.setEnabled(True)
        
        return
        
    @QtCore.pyqtSlot()
    def _config_null_ui_switch(self):
        
        self.applyButton.setDisabled(True)
        
        return
    
    def get_available(self):
        
        strategy_names = super(GUIStrategyManager,
                               self).get_available()
        
        strategy_weights = []

        for strategy_name in strategy_names:
            
            cls_name = self._plugin_names[strategy_name]
            StrategyCls = self._plugin_classes[cls_name]
            strategy_obj = StrategyCls()
            
            strategy_weights.append(strategy_obj.get_weight())
            
        sorted_lists = sorted(zip(strategy_names, strategy_weights),
                              key=lambda x: x[1])
        
        (sorted_names,
         sorted_weights) = [[x[i] for x in sorted_lists] for i in range(2)]
         
        monotonic = all(x<y for x, y in zip(sorted_weights,
                                            sorted_weights[1:]))
                                                
        if not monotonic:
            
            errStr = ("Interface weights are not monotonic. Found "
                      "weights: {}").format(sorted_weights)
            raise ValueError(errStr)
            
        return sorted_names
        
    def get_level_values_df(self, shell, var_id, scope, ignore_strategy):
        
        if ignore_strategy or shell.strategy is None:
            strategy = None
        else:
            strategy = shell.strategy
            
        # Get the table widget
        df = super(GUIStrategyManager, self).get_level_values_df(shell.core,
                                                                 shell.project,
                                                                 var_id,
                                                                 strategy,
                                                                 scope=scope)
        widget = OutputDataTable(shell.core._input_parent,
                                 df.columns)
        widget._set_value(df)
        
        self._last_df = df
        
        return widget
        
    def get_level_values_plot(self, shell,
                                    var_id,
                                    scope,
                                    ignore_strategy,
                                    sim_titles):
        
        # Either use the strategy or the list of sim titles
        if ignore_strategy or shell.strategy is None:
            strategy = None
        else:
            strategy = shell.strategy
            sim_titles = None
        
        fig_handle = super(GUIStrategyManager,
                           self).get_level_values_plot(shell.core,
                                                       shell.project,
                                                       var_id,
                                                       strategy,
                                                       sim_titles,
                                                       scope)
        
        widget = MPLWidget(fig_handle, shell.core._input_parent)
        
        return widget
        
    def get_comparison_values_df(self, shell, 
                                       var_one_id,
                                       var_two_id,
                                       module,
                                       scope,
                                       ignore_strategy):
        
        if ignore_strategy or shell.strategy is None:
            strategy = None
        else:
            strategy = shell.strategy
    
        df = super(GUIStrategyManager,
                   self).get_comparison_values_df(shell.core,
                                                  shell.project,
                                                  var_one_id,
                                                  var_two_id,
                                                  module,
                                                  strategy,
                                                  scope)
        
        widget = OutputDataTable(shell.core._input_parent,
                                 df.columns)
        widget._set_value(df)
        
        self._last_df = df
        
        return widget
        
    def get_comparison_values_plot(self, shell, 
                                         var_one_id,
                                         var_two_id,
                                         module,
                                         scope,
                                         ignore_strategy):
        
        if ignore_strategy or shell.strategy is None:
            strategy = None
        else:
            strategy = shell.strategy
    
        fig_handle = super(GUIStrategyManager,
                           self).get_comparison_values_plot(shell.core,
                                                            shell.project,
                                                            var_one_id,
                                                            var_two_id,
                                                            module,
                                                            strategy,
                                                            scope)
        
        widget = MPLWidget(fig_handle, shell.core._input_parent)
        
        return widget
        
    @QtCore.pyqtSlot(object)
    def _load_strategy(self, strategy):
        
        strategy_name = strategy.get_name()
        
        self._strategy = strategy
        self._last_selected = strategy_name
        
        if strategy.allow_run(self._shell.core, self._shell.project):
            self._set_strategy_name()
        else:
            self._set_strategy_name_unavailable()
        
        return
    
    def _set_strategy_name(self):
        self._set_dynamic_label(self._last_selected)
        return

    @QtCore.pyqtSlot()
    def _set_strategy_name_unavailable(self):
        
        strategy_name = "{} (unavailable)".format(self._last_selected)
        self._set_dynamic_label(strategy_name)
        
        return
    
    @QtCore.pyqtSlot(object)
    def _update_configuration(self, item=None):
        
        if item is None:
            if self._last_selected is None:
                selected = None
            else:
                selected = self._last_selected
        elif isinstance(item, basestring):
            selected = item
            if selected == self._last_selected: return
        elif isinstance(item, QtGui.QListWidgetItem):
            selected = str(item.text())
            if selected == self._last_selected: return
        else:
            raise TypeError
            
        self._last_selected = selected
        
        self.applyButton.setDisabled(True)
        
        if selected is None:
            
            self._strategy_widget = Message(self,
                                            "No Strategy Selected")
            self._set_main_widget(self._strategy_widget)
            
            return
            
        current_strategy = self.get_strategy(selected)
            
        self._strategy_widget = current_strategy.get_widget(self,
                                                            self._shell)
        self._strategy_widget.config_set.connect(self._config_set_ui_switch)
        self._strategy_widget.config_null.connect(self._config_null_ui_switch)
        self._strategy_widget.reset.connect(self._reset_strategy)
        self._set_main_widget(self._strategy_widget)

        if (self._strategy is not None and
            current_strategy.get_name() == self._strategy.get_name()):
            
            self.mainWidget.set_configuration(self._strategy.get_config())
            
        return
        
    @QtCore.pyqtSlot(object)
    def _reset_strategy(self):
        
        self.listWidget.clearSelection()
        
        self._last_selected = None
        self._strategy = None
        
        if self._strategy_widget is not None:
            self._strategy_widget.reset.disconnect()
            self._strategy_widget.config_set.disconnect()
            self._strategy_widget.config_null.disconnect()
        
        self._strategy_widget = None
        
        self._update_configuration()
        self._set_dynamic_label("None")
        
        self.strategy_selected.emit(self._strategy)
        
        return
    
    @QtCore.pyqtSlot(object)
    def _configure_strategy(self):
        
        self._strategy = self.get_strategy(self._last_selected)
        
        config = self.mainWidget.get_configuration()
        self._strategy.configure(**config)
        
        if self._strategy.allow_run(self._shell.core, self._shell.project):
            self._set_strategy_name()
        else:
            self._set_strategy_name_unavailable()
        
        self.strategy_selected.emit(self._strategy)
        
        return
    
    @QtCore.pyqtSlot(object)
    def show(self):
        self._update_configuration()
        super(GUIStrategyManager, self).show()
        return
        
class GUIToolManager(ToolManager):
        
    """Tool discovery and execution"""
        
    def __init__(self):
        
        ToolManager.__init__(self, tools, "GUITool")
        
        return
    
    def get_available(self):
        
        tool_names = super(GUIToolManager, self).get_available()
        
        tool_weights = []

        for tool_name in tool_names:
            
            cls_name = self._plugin_names[tool_name]
            ToolCls = self._plugin_classes[cls_name]
            tool_obj = ToolCls()
            
            tool_weights.append(tool_obj.get_weight())
            
        sorted_lists = sorted(zip(tool_names, tool_weights),
                              key=lambda x: x[1])
        
        (sorted_names,
         sorted_weights) = [[x[i] for x in sorted_lists] for i in range(2)]
         
        monotonic = all(x<y for x, y in zip(sorted_weights,
                                            sorted_weights[1:]))
                                                
        if not monotonic:
            
            errStr = ("Interface weights are not monotonic. Found "
                      "weights: {}").format(sorted_weights)
            raise ValueError(errStr)
            
        return sorted_names

