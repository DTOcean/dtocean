# -*- coding: utf-8 -*-

#    Copyright (C) 2016-2018 Mathew Topper
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


from PySide6 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:

    def _fromUtf8(s):
        return s


from .display import is_high_dpi

if is_high_dpi():
    pass
else:
    pass


def make_redicon_pixmap():
    pixmap = QtGui.QPixmap(_fromUtf8(":/icons/icons/square-rounded-128.png"))

    return pixmap


def make_greenicon_pixmap():
    pixmap = QtGui.QPixmap(_fromUtf8(":/icons/icons/circle-128.png"))

    return pixmap


def make_blueicon_pixmap():
    pixmap = QtGui.QPixmap(_fromUtf8(":/icons/icons/diamond-rounded-128.png"))

    return pixmap


def make_buttoncancel_pixmap():
    pixmap = QtGui.QPixmap(_fromUtf8(":/icons/icons/button_cancel-128.png"))

    return pixmap
