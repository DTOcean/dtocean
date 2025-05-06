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

from __future__ import unicode_literals

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

plt.style.use("ggplot")
plt.rcParams["svg.fonttype"] = "none"


class ImageLabel(QtWidgets.QLabel):
    def __init__(self, parent, img=None):
        super(ImageLabel, self).__init__(parent)
        self.setFrameStyle(QtWidgets.QFrame.Shape.StyledPanel)
        self._pixmap = None
        self._display_window = parent
        self._img_path = None

        if img is not None:
            self._img_path = img
            self._pixmap = QtGui.QPixmap(img)

    def _init_ui(self):
        self._display_window._add_display(self)

    def paintEvent(self, event):
        if self._pixmap is not None:
            size = self.size()
            painter = QtGui.QPainter(self)
            point = QtCore.QPoint(0, 0)
            scaledPix = self._pixmap.scaled(
                size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            # start painting the label from left upper corner
            point.setX((size.width() - scaledPix.width()) // 2)
            point.setY((size.height() - scaledPix.height()) // 2)
            painter.drawPixmap(point, scaledPix)

    def _update_display(self, img, *args, **kwargs):
        self._img_path = img

        if self._img_path is None:
            self._pixmap = None

        else:
            self._pixmap = QtGui.QPixmap(img)

        self.repaint()

    def _clear_display(self):
        self._update_display(None)


class ImageDictLabel(ImageLabel):
    def __init__(self, parent, image_dict):
        super(ImageDictLabel, self).__init__(parent)
        self._image_dict = image_dict

    def _update_display(self, result, *args, **kwargs):
        key = result.values()[0]
        img = self._image_dict[key]
        super(ImageDictLabel, self)._update_display(img)

    def _clear_display(self):
        super(ImageDictLabel, self)._update_display(None)


class MPLWidget(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    closing = QtCore.Signal()

    def __init__(self, figure, parent=None):
        FigureCanvas.__init__(self, figure)
        FigureCanvas.setSizePolicy(
            self,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        FigureCanvas.updateGeometry(self)

    def closeEvent(self, event):
        self.closing.emit()
        event.accept()


def get_current_filetypes():
    if not plt.get_fignums():
        return {}

    fig = plt.gcf()
    filetypes = fig.canvas.get_supported_filetypes()

    return filetypes


def save_current_figure(figure_path):
    if not plt.get_fignums():
        return

    fig = plt.gcf()
    fig.savefig(figure_path)


def get_current_figure_size():
    if not plt.get_fignums():
        raise RuntimeError("No open plots")

    fig = plt.gcf()
    size_inches = fig.get_size_inches()

    return size_inches
