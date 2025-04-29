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

from collections import OrderedDict

import os
import glob
import platform
from itertools import cycle

import sip
import yaml
import pandas as pd
from PyQt4 import QtGui, QtCore

from ..utils.config import get_software_version # pylint: disable=no-name-in-module
from ..utils.display import is_high_dpi

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

if is_high_dpi():

    from ..designer.high.projectproperties import Ui_ProjectProperties
    from ..designer.high.shuttle import Ui_ShuttleDialog
    from ..designer.high.datacheck import Ui_DataCheckDialog
    from ..designer.high.mainwindow import Ui_MainWindow
    from ..designer.high.listtableeditor import Ui_ListTableEditor
    from ..designer.high.testdatapicker import Ui_TestDataPicker
    from ..designer.high.progress import Ui_ProgressBar
    from ..designer.high.listframeeditor import  Ui_ListFrameEditor
    from ..designer.high.about import  Ui_AboutDialog
    
else:
    
    from ..designer.low.projectproperties import Ui_ProjectProperties
    from ..designer.low.shuttle import Ui_ShuttleDialog
    from ..designer.low.datacheck import Ui_DataCheckDialog
    from ..designer.low.mainwindow import Ui_MainWindow
    from ..designer.low.listtableeditor import Ui_ListTableEditor
    from ..designer.low.testdatapicker import Ui_TestDataPicker
    from ..designer.low.progress import Ui_ProgressBar
    from ..designer.low.listframeeditor import  Ui_ListFrameEditor
    from ..designer.low.about import  Ui_AboutDialog

HOME = os.path.expanduser("~")
DIR_PATH = os.path.dirname(__file__)


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    
    def __init__(self):
        
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self._dynamic_actions = {}
        
        return
    
    def _add_dynamic_action(self, action_name, menu_name):
        
        action_id = "action{}".format(action_name.replace(" ", "_"))
        
        new_action = QtGui.QAction(self)
        new_action.setCheckable(False)
        new_action.setEnabled(False)
        new_action.setShortcutContext(QtCore.Qt.WindowShortcut)
        new_action.setSoftKeyRole(QtGui.QAction.PositiveSoftKey)
        new_action.setObjectName(_fromUtf8(action_id))
        new_action.setText(action_name)
        
        menu = getattr(self, menu_name)
        menu.addAction(new_action)
        
        return new_action
    

class Shuttle(QtGui.QDialog, Ui_ShuttleDialog):
    
    list_updated = QtCore.pyqtSignal(list)

    def __init__(self, parent,
                       title,
                       left_label="Available:",
                       right_label="Selected:",
                       left_item_dict=None,
                       right_item_dict=None,
                       item_icon=None):

        super(Shuttle, self).__init__(parent)
        self._left_model = QtGui.QStandardItemModel(self)
        self._right_model = QtGui.QStandardItemModel(self)
        self._left_index = None
        self._right_index = None
        self._result = None

        if (left_item_dict is not None or
            right_item_dict is not None):

                self._add_items(left_item_dict, right_item_dict);

        self._init_ui(title, left_label, right_label)

        return

    def _add_items(self, left_item_dict=None,
                         right_item_dict=None):

        if left_item_dict is not None:
            self._make_left_items(left_item_dict)

        if right_item_dict is not None:
            self._make_right_items(right_item_dict)

        return
        
    def _add_items_from_lists(self, left_item_list=None,
                                    right_item_list=None):
        
        if left_item_list is not None:
            
            left_item_tuples = [(x, None) for x in left_item_list]
            left_item_dict = OrderedDict(left_item_tuples)

        if right_item_list is not None:
            
            right_item_tuples = [(x, None) for x in right_item_list]
            right_item_dict = OrderedDict(right_item_tuples)
            
        if left_item_list is not None and right_item_list is not None:

            for key in right_item_dict.keys(): left_item_dict.pop(key, None)

        self._add_items(left_item_dict, right_item_dict)
        
        return

    def _get_right_data(self):

        data = []

        for row in range(self._right_model.rowCount()):

            index = self._right_model.index(row, 0)

            # We suppose data are strings
            data.append(str(self._right_model.data(index).toString()))

        return data

    def _init_ui(self, title,
                       left_label,
                       right_label):

        self.setupUi(self)

        self.setWindowTitle(title)
        styleStr = ('<html><head/><body><p><span style=" '
                    'font-weight:600; color:#303030;">{}'
                    '</span></p></body></html>')
        self.leftLabel.setText(styleStr.format(left_label))
        self.rightLabel.setText(styleStr.format(right_label))

        self.addButton.clicked.connect(self.left_to_right)
        self.removeButton.clicked.connect(self.right_to_left)
        
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(
                                                             self._update_list)

        self._init_lists()

        return

    def _init_lists(self):

        self.leftListView.setModel(self._left_model)
        self.leftListView.clicked.connect(self.on_leftView_clicked)
        self.leftListView.show()

        self.rightListView.setModel(self._right_model)
        self.rightListView.clicked.connect(self.on_rightView_clicked)
        self.rightListView.show()

        return

    def _make_left_items(self, item_dict):

        self._left_model.clear()

        for item_text, icon in item_dict.iteritems():

            item = QtGui.QStandardItem(item_text)

            if icon is not None: item.icon = icon;

            self._left_model.appendRow(item)

        return

    def _make_right_items(self, item_dict):

        self._right_model.clear()

        for item_text, icon in item_dict.iteritems():

            item = QtGui.QStandardItem(item_text)

            if icon is not None: item.icon = icon;

            self._right_model.appendRow(item)

        return
        
    @QtCore.pyqtSlot()
    def _update_list(self):
        
        updated_list = self._get_right_data()
        self.list_updated.emit(updated_list)
        
        return

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_leftView_clicked(self, index):

        self._left_index = index.row()

        return

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_rightView_clicked(self, index):

        self._right_index = index.row()

        return

    @QtCore.pyqtSlot()
    def left_to_right(self):

        if (self._left_index is not None and
                self._left_index < self._left_model.rowCount()):

            item = self._left_model.takeRow(self._left_index)
            self._right_model.appendRow(item)

        return

    @QtCore.pyqtSlot()
    def right_to_left(self):

        if (self._right_index is not None and
                self._right_index < self._right_model.rowCount()):

            item = self._right_model.takeRow(self._right_index)
            self._left_model.appendRow(item)

        return


class DataCheck(QtGui.QDialog, Ui_DataCheckDialog):

    def __init__(self, parent=None):

        super(DataCheck, self).__init__(parent)

        self._init_ui()

        return

    def _init_ui(self):

        self.setupUi(self)

        self.provideLabel.hide()
        self.buttonBox.button(
                         QtGui.QDialogButtonBox.Ok).setEnabled(False)

        return

    def _set_passed(self, label="PASSED"):

        passStr = ('<html><head/><body><p><span '
                   'style=" font-size:11pt; color:#00aa00;">'
                   '{}</span></p></body></html>').format(label)
        self.resultLabel.setText(passStr)
        self.provideLabel.hide()
        self.tableWidget.setEnabled(False)
        self.tableWidget.setRowCount(0)
        self.buttonBox.button(
                         QtGui.QDialogButtonBox.Ok).setEnabled(True)
        self.buttonBox.button(
                         QtGui.QDialogButtonBox.Ok).setDefault(True)

        return

    def _set_failed(self, address_df, label="FAILED"):

        passStr = ('<html><head/><body><p><span '
                   'style=" font-size:11pt; color:#aa0000;">'
                   '{}</span></p></body></html>').format(label)
        self.resultLabel.setText(passStr)
        self.provideLabel.show()

        if address_df is None: return;

        self.tableWidget.setEnabled(True)

        self.tableWidget.setRowCount(len(address_df))

        for index, row in address_df.iterrows():

            item = QtGui.QTableWidgetItem(row["Section"])
            item.setTextAlignment(QtCore.Qt.AlignVCenter |
                                                    QtCore.Qt.AlignHCenter)
            self.tableWidget.setItem(index, 0, item)

            item = QtGui.QTableWidgetItem(row["Branch"])
            item.setTextAlignment(QtCore.Qt.AlignVCenter |
                                                    QtCore.Qt.AlignHCenter)
            self.tableWidget.setItem(index, 1, item)

            item = QtGui.QTableWidgetItem(row["Item"])
            item.setTextAlignment(QtCore.Qt.AlignVCenter |
                                                    QtCore.Qt.AlignHCenter)
            self.tableWidget.setItem(index, 2, item)
            
        self.buttonBox.button(
                         QtGui.QDialogButtonBox.Ok).setEnabled(False)

        return
        
    def show(self, address_df, title="Checking data requirements..."):

        self.setWindowTitle(title)
        
        if address_df is None:
            self._set_passed()
        else:
            self._set_failed(address_df)

        super(DataCheck, self).show()

        return


class ProjProperties(QtGui.QDialog, Ui_ProjectProperties):

    def __init__(self, parent=None):
    
        super(ProjProperties, self).__init__(parent)

        self._init_ui()

        return

    def _init_ui(self):

        self.setupUi(self)

        return


class TestDataPicker(QtGui.QDialog, Ui_TestDataPicker):
    
    __test__ = False
    path_set = QtCore.pyqtSignal(str)
    
    def __init__(self, parent=None):
        super(TestDataPicker, self).__init__(parent)
        self.browseButton = None
        self._init_ui()
    
    def _init_ui(self):
        self.setupUi(self)
        self.browseButton = self.buttonBox.addButton("Browse...",
                                          QtGui.QDialogButtonBox.ActionRole)
        self.browseButton.clicked.connect(self._write_path)
    
    @QtCore.pyqtSlot()
    def _write_path(self):
        test_file_path = QtGui.QFileDialog.getOpenFileName(self,
                                                           directory=HOME)
        self.pathLineEdit.setText(test_file_path)


class ListTableEditor(QtGui.QDialog, Ui_ListTableEditor):
    
    def __init__(self, parent=None):
        
        QtGui.QDialog.__init__(self, parent)
        Ui_ListTableEditor.__init__(self)
        self.setupUi(self)
                
        return

    def _update_list(self, names):
        
        self.listWidget.clear()
        self.listWidget.addItems(names)
            
        return
    
    def _add_item(self, name):
        
        item = QtGui.QListWidgetItem(name)
        self.listWidget.addItem(item)
        
        return item
    
    def _delete_selected(self):
        
        self.listWidget.takeItem(self.listWidget.currentRow())
        self.tableWidget.clear()
        
        return
        
    def _update_table(self, dataframe, freeze_cols=None):
        
        self.tableWidget.clear()
        self.tableWidget.setRowCount(len(dataframe))
        self.tableWidget.setColumnCount(len(dataframe.columns))
        self.tableWidget.setHorizontalHeaderLabels(dataframe.columns)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.verticalHeader().hide()
        
        for j, column in enumerate(dataframe):
            
            series = dataframe[column]
            
            for i, value in enumerate(series):
                
                if value is None: value = ""
                item = QtGui.QTableWidgetItem(value)
                
                if freeze_cols is not None and column in freeze_cols:
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                
                self.tableWidget.setItem(i, j, item)
                
        return
        
    def _read_table(self):
        
        n_cols = self.tableWidget.columnCount()
        n_rows = self.tableWidget.rowCount()

        frame_dict = {}

        for j in xrange(n_cols):
            
            header = str(self.tableWidget.horizontalHeaderItem(j).text())
            row_values = []
            
            for i in xrange(n_rows):
                row_values.append(str(self.tableWidget.item(i,j).text()))
                
            frame_dict[header] = row_values
            
        df = pd.DataFrame(frame_dict)
        
        return df


class ListFrameEditor(QtGui.QDialog, Ui_ListFrameEditor):
    
    """Dialog for selecting and configuring strategies."""
    
    def __init__(self, parent=None,
                       title=None):
        
        QtGui.QDialog.__init__(self, parent)
        Ui_ListFrameEditor.__init__(self)
        
        self._init_ui(title)

        return
        
    def _init_ui(self, title=None):
        
        self.setupUi(self)
        
        if title is not None: self.setWindowTitle(title)
        
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainFrame.setLayout(self.mainLayout)
        self.mainWidget = None
        
        self.closeButton.clicked.connect(self.close)
        
        return
        
    def _init_labels(self, top_label=None,
                           list_label=None,
                           main_label=None):
        
        if top_label is None: top_label = ""        
        if list_label is None: list_label = ""
        if main_label is None: main_label = ""
        
        self.listLabel.setText(list_label)
        self.mainLabel.setText(main_label)
        self.topStaticLabel.setText(top_label)
        
        return

    def _update_list(self, names):
        
        self.listWidget.clear()
        self.listWidget.addItems(names)
            
        return
        
    def _set_dynamic_label(self, text=None):

        if text is None: text = ""
        self.topDynamicLabel.setText(text)
        
        return
        
    def _set_main_widget(self, widget):
        
        if self.mainWidget is not None:
        
            self.mainLayout.removeWidget(self.mainWidget)
            self.mainWidget.deleteLater()
            sip.delete(self.mainWidget)
            self.mainWidget = None
            
        self.mainWidget = widget
        self.mainLayout.addWidget(self.mainWidget)
        
        return


class ProgressBar(QtGui.QDialog, Ui_ProgressBar):
    
    force_quit = QtCore.pyqtSignal()
    
    def __init__(self, parent=None, allow_close=False):
        
        flags = (QtCore.Qt.WindowMinimizeButtonHint |
                 QtCore.Qt.WindowMaximizeButtonHint)
        
        super(ProgressBar, self).__init__(parent, flags=flags)
        self.setupUi(self)
        
        self.allow_close = allow_close
                
        return
        
    def set_pulsing(self):
        
        self.progressBar.setRange(0,0)
        
        return
        
    def closeEvent(self, event):
        
        if self.allow_close:
            event.accept() 
        else:
            self.force_quit.emit()
            event.ignore()
            
        return
    
    def changeEvent(self, event):
        
        if event.type() == QtCore.QEvent.WindowStateChange:
            
            if self.windowState() & QtCore.Qt.WindowMinimized:
                self.parent().showMinimized()
            else:
                self.parent().showMaximized()
        
    def keyPressEvent(self, event):
        
        if not event.key() == QtCore.Qt.Key_Escape:
            super(ProgressBar, self).keyPressEvent(event)


class About(QtGui.QDialog, Ui_AboutDialog):
    
    def __init__(self, parent=None, image_delay=5000, fade_duration=2000):
        
        QtGui.QDialog.__init__(self, parent)
        Ui_AboutDialog.__init__(self)
        
        self._delay = image_delay
        self._image_files = None
        self._timer = None
        self._fade_in = None
        self._fade_out = None
        self._effect = None
        
        self._init_ui(fade_duration)
        
        return
    
    def _init_ui(self, fade_duration):
        
        self.setupUi(self)
        
        software_version = get_software_version()
        arch_str = " ".join(platform.architecture())
        software_str = "{} ({})".format(software_version, arch_str)
        
        self.versionLabel.setText(software_str)
        
        resources_path = os.path.join(DIR_PATH, "..", "resources")
        names_path = os.path.join(resources_path, "people.yaml")
        
        with open(names_path, 'r') as stream:
            names = yaml.load(stream, Loader=yaml.FullLoader) # nosec B506
        
        if names is None:
            
            self.verticalLayout_3.removeWidget(self.peopleIntroLabel)
            self.peopleIntroLabel.deleteLater()
            self.peopleIntroLabel = None
            
            self.verticalLayout_3.removeWidget(self.peopleLabel)
            self.peopleLabel.deleteLater()
            self.peopleLabel = None
            
            self.verticalLayout_3.removeWidget(self.line)
            self.line.deleteLater()
            self.line = None
        
        elif len(names) == 1:
            
            names_str = names[0]
            self.peopleLabel.setText(names_str)
        
        else:
            
            names_str = ", ".join(names[:-1])
            names_str += " and {}".format(names[-1])
            
            self.peopleLabel.setText(names_str)
        
        pix_search_str = os.path.join(resources_path, "beneficiary*.png")
        pix_list = glob.glob(pix_search_str)
        
        self._n_pix = len(pix_list)
        
        if self._n_pix > 0:
            
            self._image_files = cycle(pix_list)
        
        else:
            
            self.verticalLayout_3.removeWidget(self.insitutionIntroLabel)
            self.insitutionIntroLabel.deleteLater()
            self.insitutionIntroLabel = None
            
            self.horizontalLayout.removeWidget(self.frame)
            self.frame.deleteLater()
            self.frame = None
            
            self.verticalLayout_4.removeWidget(self.insitutionIntroLabel)
            self.institutionLabel.deleteLater()
            self.institutionLabel = None
            
            self.verticalLayout_3.removeWidget(self.line_3)
            self.line_3.deleteLater()
            self.line_3 = None
        
        if self._n_pix > 1:
            
            self._timer = QtCore.QTimer(self)
            self._effect = QtGui.QGraphicsOpacityEffect()
            self._fade_in = self._init_fade_in(fade_duration)
            self._fade_out = self._init_fade_out(fade_duration)
            self.institutionLabel.setGraphicsEffect(self._effect)
            
            self._fade_in.finished.connect(self._start_timer)
            self._fade_out.finished.connect(self._start_image)
            self.scrollArea.verticalScrollBar().valueChanged.connect(
                                                self.institutionLabel.repaint)
        
        return
    
    def _init_fade_in(self, duration):
        
        fade_in = QtCore.QPropertyAnimation(self._effect, "opacity")
        fade_in.setDuration(duration)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QtCore.QEasingCurve.OutQuad)
        
        return fade_in
    
    def _init_fade_out(self, duration):
        
        fade_out = QtCore.QPropertyAnimation(self._effect, "opacity")
        fade_out.setDuration(duration)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QtCore.QEasingCurve.OutQuad)
        
        return fade_out
    
    @QtCore.pyqtSlot()
    def _start_image(self):
        
        image_path = self._image_files.next()
        image = QtGui.QPixmap(image_path)
        self.institutionLabel.setPixmap(image)
        
        if self._n_pix > 1:
            self._fade_in.start()
        
        return
    
    @QtCore.pyqtSlot()
    def _start_timer(self):
        
        self._timer.start(self._delay)
        
        return
    
    @QtCore.pyqtSlot()
    def _end_image(self):
        
        self._timer.stop()
        self._fade_out.start()
       
        return
    
    @QtCore.pyqtSlot()
    def show(self):
        
        super(About, self).show()
        
        if self._n_pix > 1:
            self._timer.timeout.connect(self._end_image)
            self._effect.setOpacity(0.)
        
        if self._n_pix > 0:
            self._start_image()
        
        return
    
    def closeEvent(self, evnt):
        
        super(About, self).closeEvent(evnt)
        
        if self._n_pix > 1:
            self._timer.timeout.disconnect()
            self._timer.stop()
        
        return


class Message(QtGui.QWidget):
    
    def __init__(self, parent, text):
        
        super(Message, self).__init__(parent)
        
        self.text = text
        
        return
    
    def paintEvent(self, event):
        
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()
        
        return
    
    def drawText(self, event, qp):
        
        qp.setPen(QtGui.QColor(25, 25, 25))
        qp.setFont(QtGui.QFont('Decorative', 10))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.text)
        
        return
