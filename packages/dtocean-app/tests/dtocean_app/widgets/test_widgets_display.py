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


import matplotlib.pyplot as plt
import pytest

from dtocean_app.widgets.display import (
    MPLWidget,
    get_current_figure_size,
    get_current_filetypes,
    save_current_figure,
)


@pytest.fixture
def mpl_widget(qtbot, figure):
    widget = MPLWidget(figure)
    widget.show()
    qtbot.addWidget(widget)

    return widget


def test_MPLWidget_init(mpl_widget):
    assert mpl_widget.isVisible()


def test_MPLWidget_closing(mpl_widget):
    mpl_widget.close()


def test_get_current_filetypes():
    plt.figure()
    test = get_current_filetypes()
    plt.close("all")

    assert "png" in test


def test_get_current_filetypes_no_figure():
    plt.close("all")
    test = get_current_filetypes()
    assert not test


def test_save_current_figure(tmp_path):
    plt.figure()
    p = tmp_path / "mock.png"
    save_current_figure(str(p))
    plt.close("all")

    assert p.is_file()


def test_save_current_figureno_figure(tmp_path):
    plt.close("all")
    p = tmp_path / "mock.png"
    save_current_figure(str(p))

    assert not p.is_file()


def test_get_current_figure_size_no_figure():
    plt.close("all")

    with pytest.raises(RuntimeError) as excinfo:
        get_current_figure_size()

    assert "No open plots" in str(excinfo)


def test_get_current_figure_size():
    plt.figure()
    test = get_current_figure_size()
    plt.close("all")

    assert (test == [6.4, 4.8]).all()
