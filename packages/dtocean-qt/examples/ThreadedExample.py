import sys
import time

from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import Slot

from dtocean_qt.pandas.models.ProgressThread import ProgressWorker, createThread
from dtocean_qt.pandas.views.OverlayProgressView import OverlayProgressWidget


class ExampleWorker(ProgressWorker):
    def __init__(self, name, ticks):
        super(ExampleWorker, self).__init__(name)
        self.ticks = ticks

    def run(self):
        count = 0
        while count < 100:
            time.sleep(1)
            count += self.ticks
            if count > 100:
                count = 100
                self.progressChanged.emit(count)
                break

            self.progressChanged.emit(count)


class Example(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Example, self).__init__(parent)

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 300, 300)

        self.vlayout = QtWidgets.QVBoxLayout(self)

        self.imgContainer = QtWidgets.QLabel(self)
        img = QtGui.QPixmap(":/europe.png")
        self.imgContainer.setPixmap(img)
        size = img.size()
        self.imgContainer.resize(size.width(), self.height())

        self.vlayout.addWidget(self.imgContainer)
        self.vlayout.addWidget(QtWidgets.QLabel("FOOO", self))

        threads = []

        worker1 = ExampleWorker("foo", 10)
        worker2 = ExampleWorker("bar", 13)
        worker3 = ExampleWorker("spam", 25)

        workers = [worker1, worker2, worker3]
        for worker in workers:
            thread = createThread(self, worker)
            threads.append(thread)
            worker.finished.connect(self.debugPrint)

        self.pgFrame = OverlayProgressWidget(self.imgContainer, workers=workers)

        for t in threads:
            t.start()

    @Slot()
    def debugPrint(self):
        sender = self.sender()
        assert isinstance(sender, ProgressWorker)
        print("THREAD %s ended" % (sender.name,))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = Example()
    widget.show()
    app.exec()
