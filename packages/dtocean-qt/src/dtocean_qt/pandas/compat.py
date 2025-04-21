import logging
log = logging.getLogger(__name__)

try:
    from PyQt4 import QtCore as QtCore_
    from PyQt4 import QtGui as QtGui_
    from PyQt4.QtCore import pyqtSlot as Slot, pyqtSignal as Signal
except ImportError, e:
    from PySide import QtCore as QtCore_
    from PySide import QtGui as QtGui_
    from PySide.QtCore import Slot, Signal

QtCore = QtCore_
QtGui = QtGui_
Qt = QtCore_.Qt

__all__ = ['QtCore', 'QtGui', 'Qt', 'Signal', 'Slot']
