# -*- coding: utf-8 -*-

#    Copyright (C) 2022 Mathew Topper
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

# pylint: disable=redefined-outer-name,protected-access

import pytest
from PyQt4 import QtCore, QtGui

from dtocean_app.widgets.dialogs import TestDataPicker, About


@pytest.fixture
def picker_widget(qtbot):
    
    widget = TestDataPicker()
    widget.show()
    qtbot.addWidget(widget)
    
    return widget


def test_TestDataPicker_init(picker_widget):
    assert picker_widget.isVisible()


def test_TestDataPicker_write_path(mocker, qtbot, picker_widget):
    
    expected = "mock.pkl"
    mocker.patch.object(QtGui.QFileDialog,
                        'getOpenFileName',
                        return_value=expected)
    
    qtbot.mouseClick(picker_widget.browseButton, QtCore.Qt.LeftButton)
    
    def has_path():
        assert str(picker_widget.pathLineEdit.text())
    
    qtbot.waitUntil(has_path)
    
    assert str(picker_widget.pathLineEdit.text()) == expected


def test_About_init(qtbot):
    
    widget = About()
    widget.show()
    qtbot.addWidget(widget)
    
    assert widget.isVisible()


def test_About_names_none(qtbot, mocker):
    
    from dtocean_app.widgets.dialogs import yaml
    
    mocker.patch.object(yaml, 'load', return_value=None)
    
    widget = About()
    widget.show()
    qtbot.addWidget(widget)
    
    assert widget.peopleIntroLabel is None
    assert widget.line is None
    assert widget.peopleLabel is None


@pytest.mark.parametrize("names, expected", [
                            (['mock'], 'mock'),
                            (['mock', 'mok'], 'mock and mok'),
                            (['mock', 'moc', 'mok'], 'mock, moc and mok')])
def test_About_names(qtbot, mocker, names, expected):
    
    from dtocean_app.widgets.dialogs import yaml
    
    mocker.patch.object(yaml, 'load', return_value=names)
    
    widget = About()
    widget.show()
    qtbot.addWidget(widget)
    
    assert widget.peopleIntroLabel is not None
    assert widget.line is not None
    assert str(widget.peopleLabel.text()) == expected


def test_About_pix_none(qtbot, mocker):
    
    from dtocean_app.widgets.dialogs import glob
    
    mocker.patch.object(glob, 'glob', return_value=[])
    
    widget = About()
    widget.show()
    qtbot.addWidget(widget)
    
    assert widget._n_pix == 0
    assert widget._image_files is None
    assert widget.insitutionIntroLabel is None
    assert widget.frame is None
    assert widget.institutionLabel is None
    assert widget.line_3 is None


def test_About_pix_one(qtbot, mocker, picture):
    
    from dtocean_app.widgets.dialogs import glob
    
    mocker.patch.object(glob, 'glob', return_value=[picture])
    
    widget = About()
    widget.show()
    qtbot.addWidget(widget)
    
    assert widget._n_pix == 1
    assert widget._image_files is not None
    assert widget.insitutionIntroLabel is not None
    assert widget.frame is not None
    assert widget.institutionLabel is not None
    assert widget.line_3 is not None
    assert widget._timer is None
    assert widget._effect is None
    assert widget._fade_in is None
    assert widget._fade_out is None


def test_About_pix_many(qtbot, mocker, picture):
    
    from dtocean_app.widgets.dialogs import glob
    
    mocker.patch.object(glob, 'glob', return_value=[picture, picture])
    
    widget = About()
    widget.show()
    qtbot.addWidget(widget)
    
    assert widget._n_pix == 2
    assert widget._image_files is not None
    assert widget.insitutionIntroLabel is not None
    assert widget.frame is not None
    assert widget.institutionLabel is not None
    assert widget.line_3 is not None
    assert widget._timer is not None
    assert widget._effect is not None
    assert widget._fade_in is not None
    assert widget._fade_out is not None
