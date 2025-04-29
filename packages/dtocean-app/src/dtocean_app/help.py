# -*- coding: utf-8 -*-

#    Copyright (C) 2016 Mathew Topper, Rui Duarte
#    Copyright (C) 2017-2018 Mathew Topper
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
Created on Sat Oct 15 12:14:30 2016

.. moduleauthor:: Rui Duarte <rui.duarte@france-energies-marines.org>
.. moduleauthor:: Mathew Topper <mathew.topper@dataonlygreater.com>
"""

import os

from PIL.Image import WEB
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QUrl
from PyQt4.QtWebKit import QWebView

from .utils.config import get_install_paths
from .widgets.dialogs import Message


class HelpWidget(QtGui.QDialog):
    
    force_quit = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        
        super(HelpWidget, self).__init__(parent)
        self._layout = None
        self._msg_widget = None
        self._url_widget = None
        
        self._init_ui()
        
        return
        
    def _init_ui(self):
        
        self._layout = QtGui.QVBoxLayout(self)
        
        man_paths = self._get_man_paths()
        
        if man_paths is None:
            self._init_message()
        else:
            self._init_help(man_paths)
            
        self.setLayout(self._layout)

        self.resize(900, 800)
        self.setWindowTitle("DTOcean User Manual")
            
        return
        
    def _init_message(self):
        
        text = "No manuals installated"
        self._msg_widget = Message(self, text)
        
        self._layout.addWidget(self._msg_widget)
        
        return
        
    def _init_help(self, path_dict):
        
        index_path = os.path.join(path_dict["man_user_path"], "index.html")
        url = QUrl.fromLocalFile(index_path)

        self._url_widget = QWebView(self)        
        self._url_widget.load(url)
        self._url_widget.show()
        
        self._layout.addWidget(self._url_widget)
             
        return
        
    def _get_man_paths(self):
        
        path_dict = get_install_paths()
                         
        return path_dict

