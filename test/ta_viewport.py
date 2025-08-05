"""
viewport.py
Main 3D viewport widget using PySide6 Qt3D.

Camera Controls:
- Left Mouse Drag: Orbit around the scene
- Right Mouse Drag or Ctrl + Left Mouse Drag: Pan the camera
- Mouse Wheel: Zoom in/out
- (Optional) Arrow keys: Orbit (if enabled in QOrbitCameraController)
"""

import sys
from PySide6.QtWidgets import QWidget, QHBoxLayout, QApplication
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DRender import Qt3DRender
from PySide6.QtGui import QVector3D, QColor

# Create shorter aliases
Qt3DWindow = Qt3DExtras.Qt3DWindow
QOrbitCameraController = Qt3DExtras.QOrbitCameraController
QCuboidMesh = Qt3DExtras.QCuboidMesh
QPhongMaterial = Qt3DExtras.QPhongMaterial
QEntity = Qt3DCore.QEntity
QDirectionalLight = Qt3DRender.QDirectionalLight
QTransform = Qt3DCore.QTransform


class Viewport3D(QWidget):
    """
    Main 3D viewport widget using Qt3D. Contains a red cube, axes, and two-tone background.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = Qt3DWindow()
        self.container = QWidget.createWindowContainer(self.view)
        layout = QHBoxLayout(self)
        layout.addWidget(self.container)
        self.setLayout(layout)

        # Set background color to sky blue
        self.view.defaultFrameGraph().setClearColor(QColor.fromRgbF(0.85, 0.9, 0.95))

        # Root entity
        self.rootEntity = QEntity()

        # Ground plane (large, flat, grey)
        self.groundEntity = QEntity(self.rootEntity)
        self.groundMesh = QCuboidMesh()
        self.groundMesh.setXExtent(100.0)
        self.groundMesh.setYExtent(0.01)
        self.groundMesh.setZExtent(100.0)
        self.groundEntity.addComponent(self.groundMesh)
        self.groundMaterial = QPhongMaterial(self.rootEntity)
        self.groundMaterial.setDiffuse(QColor.fromRgbF(0.7, 0.7, 0.7))
        self.groundEntity.addComponent(self.groundMaterial)
        groundTransform = QTransform()
        groundTransform.setTranslation(QVector3D(0, -0.005, 0))
        self.groundEntity.addComponent(groundTransform)

        # X, Y, Z axes (thin cuboids)
        axis_length = 100.0
        axis_radius = 0.03
        # X axis (red)
        self.xAxisEntity = QEntity(self.rootEntity)
        self.xAxisMesh = QCuboidMesh()
        self.xAxisMesh.setXExtent(axis_length)
        self.xAxisMesh.setYExtent(axis_radius)
        self.xAxisMesh.setZExtent(axis_radius)
        self.xAxisEntity.addComponent(self.xAxisMesh)
        self.xAxisMaterial = QPhongMaterial(self.rootEntity)
        self.xAxisMaterial.setDiffuse(QColor.fromRgbF(1.0, 0.0, 0.0))
        self.xAxisEntity.addComponent(self.xAxisMaterial)
        xAxisTransform = QTransform()
        xAxisTransform.setTranslation(QVector3D(axis_length/2, 0, 0))
        self.xAxisEntity.addComponent(xAxisTransform)
        # Y axis (green)
        self.yAxisEntity = QEntity(self.rootEntity)
        self.yAxisMesh = QCuboidMesh()
        self.yAxisMesh.setXExtent(axis_radius)
        self.yAxisMesh.setYExtent(axis_length)
        self.yAxisMesh.setZExtent(axis_radius)
        self.yAxisEntity.addComponent(self.yAxisMesh)
        self.yAxisMaterial = QPhongMaterial(self.rootEntity)
        self.yAxisMaterial.setDiffuse(QColor.fromRgbF(0.0, 1.0, 0.0))
        self.yAxisEntity.addComponent(self.yAxisMaterial)
        yAxisTransform = QTransform()
        yAxisTransform.setTranslation(QVector3D(0, axis_length/2, 0))
        self.yAxisEntity.addComponent(yAxisTransform)
        # Z axis (blue)
        self.zAxisEntity = QEntity(self.rootEntity)
        self.zAxisMesh = QCuboidMesh()
        self.zAxisMesh.setXExtent(axis_radius)
        self.zAxisMesh.setYExtent(axis_radius)
        self.zAxisMesh.setZExtent(axis_length)
        self.zAxisEntity.addComponent(self.zAxisMesh)
        self.zAxisMaterial = QPhongMaterial(self.rootEntity)
        self.zAxisMaterial.setDiffuse(QColor.fromRgbF(0.0, 0.4, 1.0))
        self.zAxisEntity.addComponent(self.zAxisMaterial)
        zAxisTransform = QTransform()
        zAxisTransform.setTranslation(QVector3D(0, 0, axis_length/2))
        self.zAxisEntity.addComponent(zAxisTransform)

        # Cube mesh (red)
        self.cubeEntity = QEntity(self.rootEntity)
        self.cubeMesh = QCuboidMesh()
        self.cubeEntity.addComponent(self.cubeMesh)
        self.material = QPhongMaterial(self.rootEntity)
        self.material.setDiffuse(QColor.fromRgbF(1.0, 0.0, 0.0))  # Red
        self.cubeEntity.addComponent(self.material)
        # Offset the cube above the floor and away from the origin
        cubeTransform = QTransform()
        cubeTransform.setTranslation(QVector3D(2, 1, 0))
        self.cubeEntity.addComponent(cubeTransform)

        # Light
        self.lightEntity = QEntity(self.rootEntity)
        self.light = QDirectionalLight(self.lightEntity)
        self.light.setWorldDirection(QVector3D(-1, -1, -1))
        self.light.setColor("white")
        self.light.setIntensity(2.0)
        self.lightEntity.addComponent(self.light)

        # Camera
        self.camera = self.view.camera()
        self.camera.lens().setPerspectiveProjection(45.0, 16/9, 0.1, 1000)
        self.camera.setPosition(QVector3D(0, 0, 10))
        self.camera.setViewCenter(QVector3D(0, 0, 0))

        # Camera controls
        self.camController = QOrbitCameraController(self.rootEntity)
        self.camController.setCamera(self.camera)

        self.view.setRootEntity(self.rootEntity)

        # Set ambient on the material
        self.material.setAmbient(QColor.fromRgbF(0.3, 0.0, 0.0))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = Viewport3D()
    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec())