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

from __future__ import unicode_literals

import os

from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import (
                                        FigureCanvasQTAgg as FigureCanvas)
import matplotlib.pyplot as plt

plt.style.use('ggplot')
plt.rcParams['svg.fonttype'] = 'none'

module_path = os.path.realpath(__file__)
test_image_path = os.path.join(module_path, '..', 'test_images')


class ImageLabel(QtGui.QLabel):

    def __init__(self, parent, img=None):

        super(ImageLabel, self).__init__(parent)
        self.setFrameStyle(QtGui.QFrame.StyledPanel)
        self._pixmap = None
        self._display_window = parent
        self._img_path = None

        if img is not None:
            self._img_path = img
            self._pixmap = QtGui.QPixmap(img);

        return

    def _init_ui(self, state=None):

        self._display_window._add_display(self)
        self._set_state(state)

        return

    def paintEvent(self, event):

        if self._pixmap is not None:

            size = self.size()
            painter = QtGui.QPainter(self)
            point = QtCore.QPoint(0,0)
            scaledPix = self._pixmap.scaled(
                                size,
                                QtCore.Qt.KeepAspectRatio,
                                transformMode=QtCore.Qt.SmoothTransformation)
            # start painting the label from left upper corner
            point.setX((size.width() - scaledPix.width())/2.)
            point.setY((size.height() - scaledPix.height())/2.)
            painter.drawPixmap(point, scaledPix)

        return

    def _update_display(self, img, *args, **kwargs):

        self._img_path = img

        if self._img_path is None:

            self._pixmap = None

        else:

            self._pixmap = QtGui.QPixmap(img)

        self.repaint()

        return

    def _clear_display(self):

        self._update_display(None)

        return


class ImageDictLabel(ImageLabel):

    def __init__(self, parent, image_dict):

        super(ImageDictLabel, self).__init__(parent)
        self._image_dict = image_dict

        return

    def _update_display(self, result, *args, **kwargs):

        key = result.values()[0]
        img = self._image_dict[key]
        abs_path = os.path.join(test_image_path, img)
        super(ImageDictLabel, self)._update_display(abs_path)

        return

    def _clear_display(self):

        super(ImageDictLabel, self)._update_display(None)

        return



class MPLWidget(FigureCanvas):
    
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    
    closing = QtCore.pyqtSignal()
    
    def __init__(self, figure, parent=None):
        
        FigureCanvas.__init__(self, figure)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
        return
    
    def closeEvent(self, event):
        
        self.closing.emit()
        event.accept()
        
        return


def get_current_filetypes():
    
    if not plt.get_fignums(): return {}
    
    fig = plt.gcf()
    filetypes = fig.canvas.get_supported_filetypes()
    
    return filetypes


def save_current_figure(figure_path):
    
    if not plt.get_fignums(): return
    
    fig = plt.gcf()
    fig.savefig(figure_path)
    
    return


def get_current_figure_size():
    
    if not plt.get_fignums():
        raise RuntimeError("No open plots")
    
    fig = plt.gcf()
    size_inches = fig.get_size_inches()
    
    return size_inches
