# -*- coding: utf-8 -*-
"""
Created on Mon May 30 15:08:09 2016
@author: at

"""

from OpenGL.GL import (
    GL_CCW,
    GL_COLOR_BUFFER_BIT,
    GL_CULL_FACE,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_FLAT,
    GL_LEQUAL,
    GL_LIGHTING,
    GL_LINES,
    GL_MODELVIEW,
    GL_PROJECTION,
    GL_QUADS,
    glBegin,
    glClear,
    glClearColor,
    glClearDepth,
    glColor,
    glColor3f,
    glDepthFunc,
    glDisable,
    glEnable,
    glEnd,
    glFrontFace,
    glLineWidth,
    glLoadIdentity,
    glMatrixMode,
    glShadeModel,
    glVertex,
    glVertex3f,
    glViewport,
)
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from .Camera import Camera
from .mesh_class import Mesh


class Viewer3DWidget(QOpenGLWidget):
    def __init__(self, parent, path, file_name):
        QOpenGLWidget.__init__(self, parent)
        self.setMouseTracking(True)
        self.setMinimumSize(800, 800)
        self.mesh_obj = Mesh(path, file_name)
        self.scaling_factor = self.get_scale()
        self.camera = Camera()
        self.camera.setSceneRadius(2 * self.scaling_factor)
        self.camera.reset()
        self.isPressed = False
        self.oldx = self.oldy = 0

        self.drawMesh_cond = True
        self.drawNorms_cond = False
        self.drawWire_cond = False

    def get_scale(self):
        return max(
            abs(self.mesh_obj.v.max(0)).max(), abs(self.mesh_obj.v.min(0)).max()
        )

    def paintGL(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        self.camera.transform()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore

        glDepthFunc(GL_LEQUAL)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glFrontFace(GL_CCW)
        glDisable(GL_LIGHTING)
        glShadeModel(GL_FLAT)

        glColor(1.0, 1.0, 1.0)
        glColor(1.0, 0.0, 0.0)
        glBegin(GL_LINES)
        glVertex(0, 0, 0)
        glVertex(1 * self.scaling_factor / 4, 0, 0)
        glEnd()

        glColor(0.0, 1.0, 0.0)
        glBegin(GL_LINES)
        glVertex(0, 0, 0)
        glVertex(0, 1 * self.scaling_factor / 4, 0)
        glEnd()

        glColor(0.0, 0.0, 1.0)
        glBegin(GL_LINES)
        glVertex(0, 0, 0)
        glVertex(0, 0, 1 * self.scaling_factor / 4)
        glEnd()

        glColor(1.0, 1.0, 1.0)
        # self.renderText(0, 0, 0, "(0,0,0)")
        # self.renderText(
        #     self.scaling_factor,
        #     self.scaling_factor,
        #     self.scaling_factor,
        #     "(%s,%s,%s)"
        #     % (self.scaling_factor, self.scaling_factor, self.scaling_factor),
        # )
        # self.renderText(
        #     -self.scaling_factor,
        #     self.scaling_factor,
        #     self.scaling_factor,
        #     "(%s,%s,%s)"
        #     % (-self.scaling_factor, self.scaling_factor, self.scaling_factor),
        # )
        # self.renderText(
        #     self.scaling_factor,
        #     -self.scaling_factor,
        #     self.scaling_factor,
        #     "(%s,%s,%s)"
        #     % (self.scaling_factor, -self.scaling_factor, self.scaling_factor),
        # )
        glColor(0.0, 1.0, 0.0)
        self.bounding_box()

        if self.drawMesh_cond:
            self.drawMesh()

        if self.drawNorms_cond:
            self.drawNorms()

        if self.drawWire_cond:
            self.drawMesh(wireframe=True)

    def drawNorms(self):
        self.makeCurrent()
        ind = -1

        while self.mesh_obj.p.shape[0] - 1 > ind:
            ind += 1
            centr = self.mesh_obj.c[ind]
            cpn = self.mesh_obj.n[ind] + centr
            glColor3f(1, 0, 0)
            glBegin(GL_LINES)
            glVertex3f(centr[0], centr[1], centr[2])
            glVertex3f(cpn[0], cpn[1], cpn[2])
            glEnd()

    def drawMesh(self, wireframe=False):
        self.makeCurrent()

        ind = -1

        while self.mesh_obj.p.shape[0] - 1 > ind:
            ind += 1
            mesh = self.mesh_obj.v[self.mesh_obj.p[ind, :], :]

            if not wireframe:
                glColor3f(0.2, 0.8, 0.5)

                glBegin(GL_QUADS)
                glVertex3f(mesh[0][0], mesh[0][1], mesh[0][2])
                glVertex3f(mesh[1][0], mesh[1][1], mesh[1][2])
                glVertex3f(mesh[2][0], mesh[2][1], mesh[2][2])
                glVertex3f(mesh[3][0], mesh[3][1], mesh[3][2])
                glEnd()

                glColor3f(0.05, 0.55, 0.3)
                glBegin(GL_QUADS)
                glVertex3f(mesh[3][0], mesh[3][1], mesh[3][2])
                glVertex3f(mesh[2][0], mesh[2][1], mesh[2][2])
                glVertex3f(mesh[1][0], mesh[1][1], mesh[1][2])
                glVertex3f(mesh[0][0], mesh[0][1], mesh[0][2])
                glEnd()

            glColor3f(1.0, 1.0, 1.0)
            glLineWidth(2)
            glBegin(GL_LINES)
            glVertex3f(mesh[0][0], mesh[0][1], mesh[0][2])
            glVertex3f(mesh[1][0], mesh[1][1], mesh[1][2])
            glEnd()

            glBegin(GL_LINES)
            glVertex3f(mesh[1][0], mesh[1][1], mesh[1][2])
            glVertex3f(mesh[2][0], mesh[2][1], mesh[2][2])
            glEnd()

            glBegin(GL_LINES)
            glVertex3f(mesh[2][0], mesh[2][1], mesh[2][2])
            glVertex3f(mesh[3][0], mesh[3][1], mesh[3][2])
            glEnd()

            glBegin(GL_LINES)
            glVertex3f(mesh[3][0], mesh[3][1], mesh[3][2])
            glVertex3f(mesh[0][0], mesh[0][1], mesh[0][2])
            glEnd()

    def bounding_box(self):
        self.makeCurrent()

        sf = 2 * self.scaling_factor

        glLineWidth(0.5)
        glColor3f(1.0, 1.0, 1.0)

        glBegin(GL_LINES)
        glVertex3f(-0.5 * sf, -0.5 * sf, -0.5 * sf)
        glVertex3f(0.5 * sf, -0.5 * sf, -0.5 * sf)
        glEnd()

        glBegin(GL_LINES)
        glVertex3f(0.5 * sf, -0.5 * sf, -0.5 * sf)
        glVertex3f(0.5 * sf, 0.5 * sf, -0.5 * sf)
        glEnd()

        glBegin(GL_LINES)
        glVertex3f(0.5 * sf, 0.5 * sf, -0.5 * sf)
        glVertex3f(-0.5 * sf, 0.5 * sf, -0.5 * sf)
        glEnd()

        glBegin(GL_LINES)
        glVertex3f(-0.5 * sf, 0.5 * sf, -0.5 * sf)
        glVertex3f(-0.5 * sf, -0.5 * sf, -0.5 * sf)
        glEnd()

        glBegin(GL_LINES)
        glVertex3f(-0.5 * sf, -0.5 * sf, -0.5 * sf)
        glVertex3f(-0.5 * sf, -0.5 * sf, 0.5 * sf)
        glEnd()

        glBegin(GL_LINES)
        glVertex3f(0.5 * sf, -0.5 * sf, -0.5 * sf)
        glVertex3f(0.5 * sf, -0.5 * sf, 0.5 * sf)
        glEnd()

        glBegin(GL_LINES)
        glVertex3f(0.5 * sf, 0.5 * sf, -0.5 * sf)
        glVertex3f(0.5 * sf, 0.5 * sf, 0.5 * sf)
        glEnd()

        glBegin(GL_LINES)
        glVertex3f(-0.5 * sf, 0.5 * sf, -0.5 * sf)
        glVertex3f(-0.5 * sf, 0.5 * sf, 0.5 * sf)
        glEnd()

        glBegin(GL_LINES)
        glVertex3f(-0.5 * sf, -0.5 * sf, 0.5 * sf)
        glVertex3f(0.5 * sf, -0.5 * sf, 0.5 * sf)
        glEnd()

        glBegin(GL_LINES)
        glVertex3f(0.5 * sf, -0.5 * sf, 0.5 * sf)
        glVertex3f(0.5 * sf, 0.5 * sf, 0.5 * sf)
        glEnd()

        glBegin(GL_LINES)
        glVertex3f(0.5 * sf, 0.5 * sf, 0.5 * sf)
        glVertex3f(-0.5 * sf, 0.5 * sf, 0.5 * sf)
        glEnd()

        glBegin(GL_LINES)
        glVertex3f(-0.5 * sf, 0.5 * sf, 0.5 * sf)
        glVertex3f(-0.5 * sf, -0.5 * sf, 0.5 * sf)
        glEnd()

    def resizeGL(self, widthInPixels, heightInPixels):
        self.camera.setViewportDimensions(widthInPixels, heightInPixels)
        glViewport(0, 0, widthInPixels, heightInPixels)

    def initializeGL(self):
        self.qglClearColor(QtGui.QColor(0, 0, 0))
        glClearDepth(1.0)

    def qglClearColor(self, clearColor: QtGui.QColor):
        glClearColor(
            clearColor.redF(),
            clearColor.greenF(),
            clearColor.blueF(),
            clearColor.alphaF(),
        )

    def mouseMoveEvent(self, mouseEvent):
        if mouseEvent.buttons() != QtCore.Qt.MouseButton.NoButton:
            # user is dragging
            delta_x = mouseEvent.x() - self.oldx
            delta_y = self.oldy - mouseEvent.y()
            if mouseEvent.buttons() & QtCore.Qt.MouseButton.RightButton:
                self.camera.orbit(
                    self.oldx,
                    self.oldy,
                    mouseEvent.x(),
                    mouseEvent.y(),
                )
            elif mouseEvent.buttons() & QtCore.Qt.MouseButton.MiddleButton:
                self.camera.dollyCameraForward(3 * (delta_x + delta_y), False)
            elif mouseEvent.buttons() & QtCore.Qt.MouseButton.LeftButton:
                self.camera.translateSceneRightAndUp(delta_x, delta_y)
            self.update()

        self.oldx = mouseEvent.x()
        self.oldy = mouseEvent.y()

    def mouseDoubleClickEvent(self, mouseEvent):
        self.showFullScreen()

    def mousePressEvent(self, e):
        self.isPressed = True

    def mouseReleaseEvent(self, e):
        self.isPressed = False

    def wheelEvent(self, e):
        z = e.angleDelta().toTuple()[1]
        self.camera.mouse_zoom(z * 0.001)
        self.update()


class PythonQtOpenGLMeshViewer(QtWidgets.QMainWindow):
    def __init__(self, path, file_name):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle(
            "Visualisation of the mesh: %s" % ("/" + path + "/" + file_name)
        )
        self.statusBar().showMessage("Mesh of the structure")

        exit = QtGui.QAction("Exit", self)
        exit.setShortcut("Ctrl+Q")
        exit.setStatusTip("Exit application")
        exit.triggered.connect(self.close)

        self.setToolTip("Mesh plotter")

        self.viewer3D = Viewer3DWidget(self, path, file_name)
        createButtons = True
        if createButtons:
            parentWidget = QtWidgets.QWidget()

            self.button1 = QtWidgets.QPushButton("Structure", self)
            self.button1.setStatusTip("Visualise the structure")
            self.viewer3D.makeCurrent()
            self.button1.clicked.connect(self.button1Action)

            self.button2 = QtWidgets.QPushButton("Norms", self)
            self.button2.setStatusTip("Visualise the norms")
            self.button2.clicked.connect(self.button2Action)

            self.button3 = QtWidgets.QPushButton("Wireframe", self)
            self.button3.setStatusTip("Visualise the the structure wireframe")
            self.button3.clicked.connect(self.button3Action)

            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(self.button1)
            vbox.addWidget(self.button3)
            vbox.addWidget(self.button2)
            vbox.addStretch(1)
            self.viewer3D.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Expanding,
            )
            hbox = QtWidgets.QHBoxLayout()
            hbox.addLayout(vbox)
            hbox.addWidget(self.viewer3D)

            parentWidget.setLayout(hbox)
            self.setCentralWidget(parentWidget)

        else:
            self.setCentralWidget(self.viewer3D)

    #        self.resize(800,800)

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to quit?",
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No,
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def button1Action(self):
        if self.viewer3D.drawMesh_cond:
            self.viewer3D.makeCurrent()
            self.viewer3D.drawMesh_cond = False
        else:
            self.viewer3D.makeCurrent()
            self.viewer3D.drawMesh_cond = True
            self.viewer3D.drawWire_cond = False
        self.viewer3D.update()

    def button2Action(self):
        if self.viewer3D.drawNorms_cond:
            self.viewer3D.makeCurrent()
            self.viewer3D.drawNorms_cond = False
        else:
            self.viewer3D.makeCurrent()
            self.viewer3D.drawNorms_cond = True
        self.viewer3D.update()

    def button3Action(self):
        if self.viewer3D.drawWire_cond:
            self.viewer3D.makeCurrent()
            self.viewer3D.drawWire_cond = False
        else:
            self.viewer3D.makeCurrent()
            self.viewer3D.drawWire_cond = True
            self.viewer3D.drawMesh_cond = False
        self.viewer3D.update()
