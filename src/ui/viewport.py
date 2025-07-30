# src/ui/viewport.py
"""
3D viewport widget using Qt3D - Phase 2 implementation.
Based on proven working Qt3D code with CAD-specific improvements.
"""

import sys
from PySide6.QtWidgets import QWidget, QHBoxLayout, QApplication, QVBoxLayout, QLabel
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DRender import Qt3DRender
from PySide6.QtGui import QVector3D, QColor
from PySide6.QtCore import Qt

from src.core.scene import Scene
from src.core.camera import Camera

# Create shorter aliases
Qt3DWindow = Qt3DExtras.Qt3DWindow
QOrbitCameraController = Qt3DExtras.QOrbitCameraController
QCuboidMesh = Qt3DExtras.QCuboidMesh
QPhongMaterial = Qt3DExtras.QPhongMaterial
QEntity = Qt3DCore.QEntity
QDirectionalLight = Qt3DRender.QDirectionalLight
QTransform = Qt3DCore.QTransform


class Viewport(QWidget):
    """
    Main 3D viewport widget using Qt3D.
    Phase 2: Basic 3D rendering with test objects.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create scene and camera objects for CAD logic
        self.scene = Scene()
        self.camera = Camera()
        
        # Set up the UI
        self._setup_ui()
        
        # Create the 3D scene
        self._create_3d_scene()
        
        print("Phase 2 Viewport initialized successfully")
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Status bar - much smaller
        self.status_label = QLabel("Phase 2: Qt3D Rendering Active - Scene Loaded", self)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 150, 0, 200);
                color: white;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 12px;
                border-radius: 4px;
            }
        """)
        self.status_label.setFixedHeight(28)  # Fixed small height
        #self.status_label.setSizePolicy(self.status_label.sizePolicy().Horizontal, self.status_label.sizePolicy().Fixed)
        main_layout.addWidget(self.status_label)
        
        # Create Qt3D window
        self.view = Qt3DWindow()
        self.container = QWidget.createWindowContainer(self.view, self)
        main_layout.addWidget(self.container)
        
        # Set CAD-appropriate background color (dark gray)
        self.view.defaultFrameGraph().setClearColor(QColor.fromRgbF(0.15, 0.15, 0.15))
    
    def _create_3d_scene(self):
        """Create the 3D scene with test objects."""
        # Root entity
        self.rootEntity = QEntity()

        # Create coordinate axes (shorter than the original for better scale)
        self._create_coordinate_axes()
        
        # Create test cube positioned for visibility
        self._create_test_cube()
        
        # Add lighting
        self._create_lighting()
        
        # Set up camera
        self._setup_camera()
        
        # Set root entity (this makes everything visible)
        self.view.setRootEntity(self.rootEntity)
        
        # Mark camera as ready
        self.camera.mark_initialized()
        
        print("3D scene created with test objects")
    
    def _create_coordinate_axes(self):
        """Create X, Y, Z coordinate axes."""
        axis_length = 3.0  # Shorter than original for better proportions
        axis_thickness = 0.05
        
        # X axis (red)
        self.xAxisEntity = QEntity(self.rootEntity)
        self.xAxisMesh = QCuboidMesh()
        self.xAxisMesh.setXExtent(axis_length)
        self.xAxisMesh.setYExtent(axis_thickness)
        self.xAxisMesh.setZExtent(axis_thickness)
        self.xAxisEntity.addComponent(self.xAxisMesh)
        self.xAxisMaterial = QPhongMaterial()
        self.xAxisMaterial.setDiffuse(QColor.fromRgbF(1.0, 0.0, 0.0))  # Red
        self.xAxisEntity.addComponent(self.xAxisMaterial)
        xAxisTransform = QTransform()
        xAxisTransform.setTranslation(QVector3D(axis_length/2, 0, 0))
        self.xAxisEntity.addComponent(xAxisTransform)
        
        # Y axis (green)
        self.yAxisEntity = QEntity(self.rootEntity)
        self.yAxisMesh = QCuboidMesh()
        self.yAxisMesh.setXExtent(axis_thickness)
        self.yAxisMesh.setYExtent(axis_length)
        self.yAxisMesh.setZExtent(axis_thickness)
        self.yAxisEntity.addComponent(self.yAxisMesh)
        self.yAxisMaterial = QPhongMaterial()
        self.yAxisMaterial.setDiffuse(QColor.fromRgbF(0.0, 1.0, 0.0))  # Green
        self.yAxisEntity.addComponent(self.yAxisMaterial)
        yAxisTransform = QTransform()
        yAxisTransform.setTranslation(QVector3D(0, axis_length/2, 0))
        self.yAxisEntity.addComponent(yAxisTransform)
        
        # Z axis (blue)
        self.zAxisEntity = QEntity(self.rootEntity)
        self.zAxisMesh = QCuboidMesh()
        self.zAxisMesh.setXExtent(axis_thickness)
        self.zAxisMesh.setYExtent(axis_thickness)
        self.zAxisMesh.setZExtent(axis_length)
        self.zAxisEntity.addComponent(self.zAxisMesh)
        self.zAxisMaterial = QPhongMaterial()
        self.zAxisMaterial.setDiffuse(QColor.fromRgbF(0.0, 0.4, 1.0))  # Blue
        self.zAxisEntity.addComponent(self.zAxisMaterial)
        zAxisTransform = QTransform()
        zAxisTransform.setTranslation(QVector3D(0, 0, axis_length/2))
        self.zAxisEntity.addComponent(zAxisTransform)
        
        print("Coordinate axes created")
    
    def _create_test_cube(self):
        """Create test cube for Phase 2 verification."""
        # Cube mesh (white for good visibility)
        self.cubeEntity = QEntity(self.rootEntity)
        self.cubeMesh = QCuboidMesh()
        self.cubeEntity.addComponent(self.cubeMesh)
        
        # White material with ambient lighting
        self.cubeMaterial = QPhongMaterial()
        self.cubeMaterial.setDiffuse(QColor.fromRgbF(0.9, 0.9, 0.9))  # Light gray/white
        self.cubeMaterial.setAmbient(QColor.fromRgbF(0.3, 0.3, 0.3))   # Ambient
        self.cubeEntity.addComponent(self.cubeMaterial)
        
        # Position cube above origin for visibility
        cubeTransform = QTransform()
        cubeTransform.setTranslation(QVector3D(0, 0, 0.5))  # Half unit above XY plane
        self.cubeEntity.addComponent(cubeTransform)
        
        print("Test cube created")
    
    def _create_lighting(self):
        """Add directional lighting to the scene."""
        self.lightEntity = QEntity(self.rootEntity)
        self.light = QDirectionalLight()
        self.light.setWorldDirection(QVector3D(-1, -1, -1))
        self.light.setColor("white")
        self.light.setIntensity(2.0)
        self.lightEntity.addComponent(self.light)
        
        print("Lighting created")
    
    def _setup_camera(self):
        """Set up camera with good initial position and orbit controls."""
        # Get Qt3D camera
        self.qt3d_camera = self.view.camera()
        self.qt3d_camera.lens().setPerspectiveProjection(45.0, 16/9, 0.1, 1000)
        
        # Position camera for good view of test objects
        self.qt3d_camera.setPosition(QVector3D(4, 4, 3))
        self.qt3d_camera.setViewCenter(QVector3D(0, 0, 0.5))  # Look at cube
        self.qt3d_camera.setUpVector(QVector3D(0, 0, 1))      # Z is up
        
        # Set up orbit controls
        self.camController = QOrbitCameraController(self.rootEntity)
        self.camController.setCamera(self.qt3d_camera)
        
        print("Camera and controls set up")
    
    # Public interface for main window integration
    def get_scene(self):
        """Get the scene object."""
        return self.scene
    
    def get_camera(self):
        """Get the camera object."""
        return self.camera
    
    def reset_camera(self):
        """Reset camera to default view (for main window menu)."""
        if hasattr(self, 'qt3d_camera'):
            self.qt3d_camera.setPosition(QVector3D(4, 4, 3))
            self.qt3d_camera.setViewCenter(QVector3D(0, 0, 0.5))
            self.qt3d_camera.setUpVector(QVector3D(0, 0, 1))
            print("Camera reset")
    
    def fit_all(self):
        """Fit all objects in view (for main window menu)."""
        self.reset_camera()
        print("Fit all")


# Test the viewport standalone
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create a test window
    viewport = Viewport()
    viewport.setWindowTitle("Phase 2 - 3D Viewport Test")
    viewport.resize(900, 700)
    viewport.show()
    
    print("Standalone viewport test running...")
    print("Controls: Left drag = orbit, Right drag = pan, Wheel = zoom")
    
    sys.exit(app.exec())