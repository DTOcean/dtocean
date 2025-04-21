import codecs
import os
import tempfile
import time
import traceback
from io import StringIO

from easygui.boxes.derived_boxes import msgbox
from PySide6 import QtWidgets


def excepthook(excType, excValue, tracebackobj):
    """
    Global function to catch unhandled exceptions.

    @param excType exception type
    @param excValue exception value
    @param tracebackobj traceback object
    """
    separator = "-" * 80

    logFile = os.path.join(tempfile.gettempdir(), "error.log")
    notice = """An unhandled exception occurred. Please report the problem.\n"""
    notice += (
        """A log has been written to "{}".\n\nError information:""".format(
            logFile
        )
    )
    timeString = time.strftime("%Y-%m-%d, %H:%M:%S")

    tbinfofile = StringIO()
    traceback.print_tb(tracebackobj, None, tbinfofile)
    tbinfofile.seek(0)
    tbinfo = tbinfofile.read()
    excValueStr = str(excValue)

    errmsg = "{0}: \n{1}".format(excType, excValueStr)
    sections = [
        "\n",
        separator,
        timeString,
        separator,
        errmsg,
        separator,
        tbinfo,
    ]
    msg = "\n".join(sections)
    try:
        f = codecs.open(logFile, "a+", encoding="utf-8")
        f.write(msg)
        f.close()
    except IOError:
        msgbox("unable to write to {0}".format(logFile), "Writing error")

    # always show an error message
    try:
        if not _isQAppRunning():
            QtWidgets.QApplication([])
        _showMessageBox(notice + msg)
    except Exception:
        msgbox(notice + msg, "Error")


def _isQAppRunning():
    if QtWidgets.QApplication.instance() is None:
        return False
    else:
        return True


def _showMessageBox(text):
    errorbox = QtWidgets.QMessageBox()
    errorbox.setText(text)
    errorbox.exec_()
