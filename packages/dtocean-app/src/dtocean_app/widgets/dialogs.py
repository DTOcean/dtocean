# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2025 Mathew Topper
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

.. moduleauthor:: Mathew Topper <damm_horse@yahoo.co.uk>
"""

import glob
import os
import platform
from collections import OrderedDict
from itertools import cycle
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pandas as pd
import yaml
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QEasingCurve, QEvent, QPropertyAnimation, Qt
from shiboken6 import Shiboken

from ..utils.config import (
    get_software_version,
)
from ..utils.display import is_high_dpi

if is_high_dpi() or TYPE_CHECKING:
    from ..designer.high.about import Ui_AboutDialog
    from ..designer.high.datacheck import Ui_DataCheckDialog
    from ..designer.high.listframeeditor import Ui_ListFrameEditor
    from ..designer.high.listtableeditor import Ui_ListTableEditor
    from ..designer.high.mainwindow import Ui_MainWindow
    from ..designer.high.progress import Ui_ProgressBar
    from ..designer.high.projectproperties import Ui_ProjectProperties
    from ..designer.high.shuttle import Ui_ShuttleDialog
    from ..designer.high.testdatapicker import Ui_TestDataPicker

else:
    from ..designer.low.about import Ui_AboutDialog
    from ..designer.low.datacheck import Ui_DataCheckDialog
    from ..designer.low.listframeeditor import Ui_ListFrameEditor
    from ..designer.low.listtableeditor import Ui_ListTableEditor
    from ..designer.low.mainwindow import Ui_MainWindow
    from ..designer.low.progress import Ui_ProgressBar
    from ..designer.low.projectproperties import Ui_ProjectProperties
    from ..designer.low.shuttle import Ui_ShuttleDialog
    from ..designer.low.testdatapicker import Ui_TestDataPicker

HOME = os.path.expanduser("~")
PARENT_PATH = Path(__file__).parent


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._dynamic_actions = {}

    def _add_dynamic_action(self, action_name, menu_name):
        action_id = "action{}".format(action_name.replace(" ", "_"))

        new_action = QtGui.QAction(self)
        new_action.setCheckable(False)
        new_action.setEnabled(False)
        new_action.setShortcutContext(Qt.ShortcutContext.WindowShortcut)
        new_action.setObjectName(action_id)
        new_action.setText(action_name)

        menu = getattr(self, menu_name)
        menu.addAction(new_action)

        return new_action


class Shuttle(QtWidgets.QDialog, Ui_ShuttleDialog):
    list_updated = QtCore.Signal(list)

    def __init__(
        self,
        parent,
        title,
        left_label="Available:",
        right_label="Selected:",
        left_item_dict=None,
        right_item_dict=None,
        item_icon=None,
    ):
        super().__init__(parent)
        self._left_model = QtGui.QStandardItemModel(self)
        self._right_model = QtGui.QStandardItemModel(self)
        self._left_index = None
        self._right_index = None
        self._result = None

        if left_item_dict is not None or right_item_dict is not None:
            self._add_items(left_item_dict, right_item_dict)

        self._init_ui(title, left_label, right_label)

    def _add_items(self, left_item_dict=None, right_item_dict=None):
        if left_item_dict is not None:
            self._make_left_items(left_item_dict)

        if right_item_dict is not None:
            self._make_right_items(right_item_dict)

    def _add_items_from_lists(self, left_item_list=None, right_item_list=None):
        if left_item_list is not None:
            left_item_tuples = [(x, None) for x in left_item_list]
            left_item_dict = OrderedDict(left_item_tuples)

        if right_item_list is not None:
            right_item_tuples = [(x, None) for x in right_item_list]
            right_item_dict = OrderedDict(right_item_tuples)

        if left_item_list is not None and right_item_list is not None:
            for key in right_item_dict.keys():
                left_item_dict.pop(key, None)

        self._add_items(left_item_dict, right_item_dict)

    def _get_right_data(self):
        data = []

        for row in range(self._right_model.rowCount()):
            index = self._right_model.index(row, 0)

            # We suppose data are strings
            data.append(self._right_model.data(index))

        return data

    def _init_ui(self, title, left_label, right_label):
        self.setupUi(self)

        self.setWindowTitle(title)
        styleStr = (
            '<html><head/><body><p><span style=" '
            'font-weight:600; color:#303030;">{}'
            "</span></p></body></html>"
        )
        self.leftLabel.setText(styleStr.format(left_label))
        self.rightLabel.setText(styleStr.format(right_label))

        self.addButton.clicked.connect(self.left_to_right)
        self.removeButton.clicked.connect(self.right_to_left)

        self.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).clicked.connect(self._update_list)

        self._init_lists()

    def _init_lists(self):
        self.leftListView.setModel(self._left_model)
        self.leftListView.clicked.connect(self.on_leftView_clicked)
        self.leftListView.show()

        self.rightListView.setModel(self._right_model)
        self.rightListView.clicked.connect(self.on_rightView_clicked)
        self.rightListView.show()

    def _make_left_items(self, item_dict):
        self._left_model.clear()

        for item_text, icon in item_dict.items():
            item = QtGui.QStandardItem(item_text)

            if icon is not None:
                item.icon = icon

            self._left_model.appendRow(item)

    def _make_right_items(self, item_dict):
        self._right_model.clear()

        for item_text, icon in item_dict.items():
            item = QtGui.QStandardItem(item_text)

            if icon is not None:
                item.icon = icon

            self._right_model.appendRow(item)

    @QtCore.Slot()
    def _update_list(self):
        updated_list = self._get_right_data()
        self.list_updated.emit(updated_list)

    @QtCore.Slot(QtCore.QModelIndex)
    def on_leftView_clicked(self, index):
        self._left_index = index.row()

    @QtCore.Slot(QtCore.QModelIndex)
    def on_rightView_clicked(self, index):
        self._right_index = index.row()

    @QtCore.Slot()
    def left_to_right(self):
        if (
            self._left_index is not None
            and self._left_index < self._left_model.rowCount()
        ):
            item = self._left_model.takeRow(self._left_index)
            self._right_model.appendRow(item)

    @QtCore.Slot()
    def right_to_left(self):
        if (
            self._right_index is not None
            and self._right_index < self._right_model.rowCount()
        ):
            item = self._right_model.takeRow(self._right_index)
            self._left_model.appendRow(item)


class DataCheck(QtWidgets.QDialog, Ui_DataCheckDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._init_ui()

    def _init_ui(self):
        self.setupUi(self)

        self.provideLabel.hide()
        self.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).setEnabled(False)

    def _set_passed(self, label="PASSED"):
        passStr = (
            "<html><head/><body><p><span "
            'style=" font-size:11pt; color:#00aa00;">'
            "{}</span></p></body></html>"
        ).format(label)
        self.resultLabel.setText(passStr)
        self.provideLabel.hide()
        self.tableWidget.setEnabled(False)
        self.tableWidget.setRowCount(0)
        self.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).setEnabled(True)
        self.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).setDefault(True)

    def _set_failed(self, address_df, label="FAILED"):
        passStr = (
            "<html><head/><body><p><span "
            'style=" font-size:11pt; color:#aa0000;">'
            "{}</span></p></body></html>"
        ).format(label)
        self.resultLabel.setText(passStr)
        self.provideLabel.show()

        if address_df is None:
            return

        self.tableWidget.setEnabled(True)

        self.tableWidget.setRowCount(len(address_df))

        for index, row in address_df.iterrows():
            item = QtWidgets.QTableWidgetItem(row["Section"])
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter
            )
            self.tableWidget.setItem(index, 0, item)

            item = QtWidgets.QTableWidgetItem(row["Branch"])
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter
            )
            self.tableWidget.setItem(index, 1, item)

            item = QtWidgets.QTableWidgetItem(row["Item"])
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter
            )
            self.tableWidget.setItem(index, 2, item)

        self.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        ).setEnabled(False)

    def show(self, address_df, title="Checking data requirements..."):
        self.setWindowTitle(title)

        if address_df is None:
            self._set_passed()
        else:
            self._set_failed(address_df)

        super().show()


class ProjProperties(QtWidgets.QDialog, Ui_ProjectProperties):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._init_ui()

    def _init_ui(self):
        self.setupUi(self)


class TestDataPicker(QtWidgets.QDialog, Ui_TestDataPicker):
    __test__ = False
    path_set = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.browseButton = None
        self._init_ui()

    def _init_ui(self):
        self.setupUi(self)
        self.browseButton = self.buttonBox.addButton(
            "Browse...",
            QtWidgets.QDialogButtonBox.ButtonRole.ActionRole,
        )
        self.browseButton.clicked.connect(self._write_path)

    @QtCore.Slot()
    def _write_path(self):
        test_file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            dir=HOME,
        )
        self.pathLineEdit.setText(test_file_path)


class ListTableEditor(QtWidgets.QDialog, Ui_ListTableEditor):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        Ui_ListTableEditor.__init__(self)
        self.setupUi(self)

    def _update_list(self, names):
        self.listWidget.clear()
        self.listWidget.addItems(names)

    def _add_item(self, name):
        item = QtWidgets.QListWidgetItem(name)
        self.listWidget.addItem(item)

        return item

    def _delete_selected(self):
        self.listWidget.takeItem(self.listWidget.currentRow())
        self.tableWidget.clear()

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
                if value is None:
                    value = ""
                item = QtWidgets.QTableWidgetItem(value)

                if freeze_cols is not None and column in freeze_cols:
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled)

                self.tableWidget.setItem(i, j, item)

    def _read_table(self):
        n_cols = self.tableWidget.columnCount()
        n_rows = self.tableWidget.rowCount()

        frame_dict = {}

        for j in range(n_cols):
            j_item = self.tableWidget.horizontalHeaderItem(j)
            assert j_item is not None
            header = j_item.text()
            row_values = []

            for i in range(n_rows):
                i_item = self.tableWidget.item(i, j)
                assert i_item is not None
                row_values.append(i_item.text())

            frame_dict[header] = row_values

        df = pd.DataFrame(frame_dict)

        return df


class ListFrameEditor(QtWidgets.QDialog, Ui_ListFrameEditor):
    """Dialog for selecting and configuring strategies."""

    def __init__(self, parent=None, title=None):
        QtWidgets.QDialog.__init__(self, parent)
        Ui_ListFrameEditor.__init__(self)

        self._init_ui(title)

    def _init_ui(self, title=None):
        self.setupUi(self)

        if title is not None:
            self.setWindowTitle(title)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainFrame.setLayout(self.mainLayout)
        self.mainWidget = None

        self.closeButton.clicked.connect(self.close)

    def _init_labels(self, top_label=None, list_label=None, main_label=None):
        if top_label is None:
            top_label = ""
        if list_label is None:
            list_label = ""
        if main_label is None:
            main_label = ""

        self.listLabel.setText(list_label)
        self.mainLabel.setText(main_label)
        self.topStaticLabel.setText(top_label)

    def _update_list(self, names):
        self.listWidget.clear()
        self.listWidget.addItems(names)

    def _set_dynamic_label(self, text=None):
        if text is None:
            text = ""
        self.topDynamicLabel.setText(text)

    def _set_main_widget(self, widget):
        if self.mainWidget is not None:
            self.mainLayout.removeWidget(self.mainWidget)
            self.mainWidget.deleteLater()
            Shiboken.delete(self.mainWidget)
            self.mainWidget = None

        self.mainWidget = widget
        self.mainLayout.addWidget(self.mainWidget)


class ProgressBar(QtWidgets.QDialog, Ui_ProgressBar):
    force_quit = QtCore.Signal()

    def __init__(self, parent=None, allow_close=False):
        if not isinstance(parent, (QtWidgets.QMainWindow, QtWidgets.QWidget)):
            raise ValueError("parent must derive from QMainWindow or QWidget")

        flags = (
            Qt.WindowType.WindowMinimizeButtonHint
            | Qt.WindowType.WindowMaximizeButtonHint
        )
        super().__init__(parent, f=flags)
        self.setupUi(self)
        self.allow_close = allow_close

    def set_pulsing(self):
        self.progressBar.setRange(0, 0)

    def closeEvent(self, event):
        if self.allow_close:
            event.accept()
        else:
            self.force_quit.emit()
            event.ignore()

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            parent = self.parent()
            assert isinstance(
                parent, (QtWidgets.QMainWindow, QtWidgets.QWidget)
            )
            if self.windowState() & Qt.WindowState.WindowMinimized:
                parent.showMinimized()
            else:
                parent.showMaximized()

    def keyPressEvent(self, event):
        if not event.key() == Qt.Key.Key_Escape:
            super().keyPressEvent(event)


class About(QtWidgets.QDialog, Ui_AboutDialog):
    def __init__(self, parent=None, image_delay=5000, fade_duration=2000):
        QtWidgets.QDialog.__init__(self, parent)
        Ui_AboutDialog.__init__(self)

        self._delay = image_delay
        self._image_files = None
        self._timer = None
        self._fade_in = None
        self._fade_out = None
        self._effect = None

        self._init_ui(fade_duration)

    def _init_ui(self, fade_duration):
        self.setupUi(self)

        assert isinstance(self.frame, QtWidgets.QFrame)
        assert isinstance(self.insitutionIntroLabel, QtWidgets.QLabel)
        assert isinstance(self.institutionLabel, QtWidgets.QLabel)
        assert isinstance(self.line, QtWidgets.QFrame)
        assert isinstance(self.line_3, QtWidgets.QFrame)
        assert isinstance(self.peopleIntroLabel, QtWidgets.QLabel)
        assert isinstance(self.peopleLabel, QtWidgets.QLabel)

        software_version = get_software_version()
        arch_str = " ".join(platform.architecture())
        software_str = "{} ({})".format(software_version, arch_str)

        self.versionLabel.setText(software_str)

        resources_path = PARENT_PATH.parent / "resources" / "about"
        names_path = resources_path / "people.yaml"

        with open(names_path, "r") as stream:
            names = yaml.load(stream, Loader=yaml.FullLoader)

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

        pix_search_str = str(resources_path / "beneficiary*.png")
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

            self.verticalLayout_3.removeWidget(self.line_3)
            self.line_3.deleteLater()
            self.line_3 = None

        if self._n_pix > 1:
            self._timer = QtCore.QTimer(self)
            self._effect = QtWidgets.QGraphicsOpacityEffect()
            self._fade_in = self._init_fade_in(fade_duration)
            self._fade_out = self._init_fade_out(fade_duration)
            self.institutionLabel.setGraphicsEffect(self._effect)

            self._fade_in.finished.connect(self._start_timer)
            self._fade_out.finished.connect(self._start_image)
            self.scrollArea.verticalScrollBar().valueChanged.connect(
                self.institutionLabel.repaint
            )
        else:
            assert self.insitutionIntroLabel is not None
            self.verticalLayout_3.removeWidget(self.insitutionIntroLabel)
            self.institutionLabel.deleteLater()
            self.institutionLabel = None

    def _init_fade_in(self, duration):
        assert self._effect is not None
        fade_in = QPropertyAnimation(
            self._effect,
            QtCore.QByteArray(b"opacity"),
        )
        fade_in.setDuration(duration)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.OutQuad)

        return fade_in

    def _init_fade_out(self, duration):
        assert self._effect is not None
        fade_out = QPropertyAnimation(
            self._effect,
            QtCore.QByteArray(b"opacity"),
        )
        fade_out.setDuration(duration)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.Type.OutQuad)

        return fade_out

    @QtCore.Slot()
    def _start_image(self):
        assert self._image_files is not None
        assert self._fade_in is not None

        image_path = next(self._image_files)
        image = QtGui.QPixmap(image_path)

        label = cast(QtWidgets.QLabel, self.institutionLabel)
        label.setPixmap(image)

        if self._n_pix > 1:
            self._fade_in.start()

    @QtCore.Slot()
    def _start_timer(self):
        assert self._timer is not None
        self._timer.start(self._delay)

    @QtCore.Slot()
    def _end_image(self):
        assert self._timer is not None
        assert self._fade_out is not None

        self._timer.stop()
        self._fade_out.start()

    @QtCore.Slot()
    def show(self):
        super().show()

        if self._n_pix > 1:
            assert self._timer is not None
            assert self._effect is not None
            self._timer.timeout.connect(self._end_image)
            self._effect.setOpacity(0.0)

        if self._n_pix > 0:
            self._start_image()

    def closeEvent(self, evnt):
        super().closeEvent(evnt)

        if self._n_pix > 1:
            assert self._timer is not None
            self._timer.timeout.disconnect()
            self._timer.stop()


class Message(QtWidgets.QWidget):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.text = text

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(QtGui.QColor(25, 25, 25))
        qp.setFont(QtGui.QFont("Decorative", 10))
        qp.drawText(event.rect(), Qt.AlignmentFlag.AlignCenter, self.text)
