def _screen_to_world(self, screen_pos):
        """Convert screen coordinates to 3D world coordinates on active work plane"""
        # Get viewport dimensions
        viewport_rect = self.container.rect()
        if viewport_rect.width() == 0 or viewport_rect.height() == 0:
            print("Viewport has zero dimensions")
            return None
        
        print(f"Viewport size: {viewport_rect.width()} x {viewport_rect.height()}")
        
        # Handle both QPointF and QPoint
        if hasattr(screen_pos, 'x'):
            x_pixel = screen_pos.x()
            y_pixel = screen_pos.y()
        else:
            x_pixel = float(screen_pos[0])
            y_pixel = float(screen_pos[1])
        
        # Simple coordinate conversion - map screen to a fixed world area
        # This is much simpler and more predictable than camera-based conversion
        world_width = 20.0   # World units visible horizontally
        world_height = 15.0  # World units visible vertically
        
        # Convert screen pixels to world coordinates
        world_x = (x_pixel / viewport_rect.width() - 0.5) * world_width
        world_y = (0.5 - y_pixel / viewport_rect.height()) * world_height  # Flip Y
        
        print(f"Simple conversion - Screen: ({x_pixel:.0f}, {y_pixel:.0f}) -> World: ({world_x:.2f}, {world_y:.2f})")
        
        # Project onto the appropriate plane
        work_plane = self.cad_manager.active_work_plane
        if work_plane == WorkPlane.XY:
            result = QVector3D(world_x, world_y, 0)
        elif work_plane == WorkPlane.XZ:
            result = QVector3D(world_x, 0, world_y)
        elif work_plane == WorkPlane.YZ:
            result = QVector3D(0, world_x, world_y)
        else:
            result = QVector3D(world_x, world_y, 0)
        
        print(f"Final world coords: ({result.x():.2f}, {result.y():.2f}, {result.z():.2f})")
        return result
# """
# enhanced_viewport.py
# Enhanced 3D viewport with integrated CAD tools support.
# Extends the original viewport with mouse handling, tool management, and UI integration.
# """

import sys
import math
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QApplication, 
                              QToolBar, QPushButton, QLabel, QSpinBox, QDoubleSpinBox,
                              QComboBox, QGroupBox, QSplitter, QTextEdit, QMainWindow)
from PySide6.QtCore import Qt, QPoint, Signal, QEvent
from PySide6.QtGui import QVector3D, QColor, QMouseEvent
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DRender import Qt3DRender
from PySide6.Qt3DInput import Qt3DInput

# Import our CAD tools
from cad_tools import CADToolManager, ToolType, WorkPlane, create_tool_descriptions, get_tool_category

# Create shorter aliases
Qt3DWindow = Qt3DExtras.Qt3DWindow
QOrbitCameraController = Qt3DExtras.QOrbitCameraController
QCuboidMesh = Qt3DExtras.QCuboidMesh
QPhongMaterial = Qt3DExtras.QPhongMaterial
QEntity = Qt3DCore.QEntity
QDirectionalLight = Qt3DRender.QDirectionalLight
QTransform = Qt3DCore.QTransform


class CADViewport3D(QWidget):
    """
    Enhanced 3D viewport with CAD tools integration.
    Handles mouse input for tool interactions and maintains the original scene.
    """
    
    # Signals for communication with UI
    status_message = Signal(str)
    
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
        
        # Initialize CAD tools manager
        self.cad_manager = CADToolManager(self.rootEntity)
        self.cad_manager.tool_changed.connect(self._on_tool_changed)
        self.cad_manager.geometry_updated.connect(self._on_geometry_updated)
        
        # Setup the scene (same as original)
        self._setup_scene()
        
        # Setup mouse handling AFTER everything else
        self._setup_mouse_input()
        
        self.view.setRootEntity(self.rootEntity)

    def _setup_scene(self):
        """Setup the basic scene elements (ground, axes, test cube)"""
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

        # Original test cube (keep for reference, but make it smaller and move it)
        self.cubeEntity = QEntity(self.rootEntity)
        self.cubeMesh = QCuboidMesh()
        self.cubeMesh.setXExtent(0.5)  # Smaller
        self.cubeMesh.setYExtent(0.5)
        self.cubeMesh.setZExtent(0.5)
        self.cubeEntity.addComponent(self.cubeMesh)
        self.material = QPhongMaterial(self.rootEntity)
        self.material.setDiffuse(QColor.fromRgbF(1.0, 0.0, 0.0))  # Red
        self.cubeEntity.addComponent(self.material)
        cubeTransform = QTransform()
        cubeTransform.setTranslation(QVector3D(5, 0.25, 5))  # Move to corner
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
        self.camera.setPosition(QVector3D(5, 5, 10))
        self.camera.setViewCenter(QVector3D(0, 0, 0))

        # Camera controls
        self.camController = QOrbitCameraController(self.rootEntity)
        self.camController.setCamera(self.camera)

        # Set ambient on the material
        self.material.setAmbient(QColor.fromRgbF(0.3, 0.0, 0.0))
    
    def _setup_mouse_input(self):
        """Setup mouse input handling for CAD tools"""
        # Create Qt3D input handlers and connect them properly
        self.inputEntity = QEntity(self.rootEntity)
        
        # Mouse device and handler
        self.mouseDevice = Qt3DInput.QMouseDevice()
        self.mouseHandler = Qt3DInput.QMouseHandler()
        self.mouseHandler.setSourceDevice(self.mouseDevice)
        
        # Connect signals properly
        self.mouseHandler.clicked.connect(self._qt3d_mouse_clicked)
        self.mouseHandler.pressed.connect(self._qt3d_mouse_pressed)
        
        # Add to input entity
        self.inputEntity.addComponent(self.mouseHandler)
        
        print("Mouse input setup complete - using Qt3D input system")
    
    def _qt3d_mouse_clicked(self, click):
        """Handle Qt3D mouse click events for CAD tools"""
        print(f"Qt3D click: button={click.button()}")
        
        # Only handle if we have an active CAD tool
        if not self.cad_manager.active_tool:
            return
            
        if click.button() == Qt3DInput.QMouseEvent.Buttons.LeftButton:
            # We need to get mouse position from somewhere else since Qt3D doesn't provide it
            # Let's use a simple approach - get the mouse position from Qt
            from PySide6.QtGui import QCursor
            from PySide6.QtCore import QPoint
            
            # Get global mouse position
            global_pos = QCursor.pos()
            
            # Convert to container local coordinates
            container_global_pos = self.container.mapToGlobal(QPoint(0, 0))
            local_x = global_pos.x() - container_global_pos.x()
            local_y = global_pos.y() - container_global_pos.y()
            
            print(f"Calculated mouse position: ({local_x}, {local_y})")
            
            # Convert to world coordinates
            from PySide6.QtCore import QPointF
            screen_pos = QPointF(local_x, local_y)
            world_point = self._screen_to_world(screen_pos)
            
            if world_point:
                print(f"CAD click at: {world_point.x():.2f}, {world_point.y():.2f}, {world_point.z():.2f}")
                handled = self.cad_manager.handle_click(world_point)
                if handled:
                    print("CAD tool handled the click")
    
    def _qt3d_mouse_pressed(self, press):
        """Handle Qt3D mouse press events"""
        print(f"Qt3D press: button={press.button()}")
        
        if press.button() == Qt3DInput.QMouseEvent.Buttons.RightButton:
            print("Right click - finishing current geometry")
            self.cad_manager.finish_current_geometry()
    
    def _screen_to_world(self, screen_pos):
        """Convert screen coordinates to 3D world coordinates on active work plane"""
        # Get viewport dimensions
        viewport_rect = self.container.rect()
        if viewport_rect.width() == 0 or viewport_rect.height() == 0:
            print("Viewport has zero dimensions")
            return None
        
        print(f"Viewport size: {viewport_rect.width()} x {viewport_rect.height()}")
        
        # Handle both QPointF and QPoint
        if hasattr(screen_pos, 'x'):
            x_pixel = screen_pos.x()
            y_pixel = screen_pos.y()
        else:
            x_pixel = float(screen_pos[0])
            y_pixel = float(screen_pos[1])
        
        # Simple coordinate conversion - map screen to a fixed world area
        # This is much simpler and more predictable than camera-based conversion
        world_width = 20.0   # World units visible horizontally
        world_height = 15.0  # World units visible vertically
        
        # Convert screen pixels to world coordinates
        world_x = (x_pixel / viewport_rect.width() - 0.5) * world_width
        world_y = (0.5 - y_pixel / viewport_rect.height()) * world_height  # Flip Y
        
        print(f"Simple conversion - Screen: ({x_pixel:.0f}, {y_pixel:.0f}) -> World: ({world_x:.2f}, {world_y:.2f})")
        
        # Project onto the appropriate plane
        work_plane = self.cad_manager.active_work_plane
        if work_plane == WorkPlane.XY:
            result = QVector3D(world_x, world_y, 0)
        elif work_plane == WorkPlane.XZ:
            result = QVector3D(world_x, 0, world_y)
        elif work_plane == WorkPlane.YZ:
            result = QVector3D(0, world_x, world_y)
        else:
            result = QVector3D(world_x, world_y, 0)
        
        print(f"Final world coords: ({result.x():.2f}, {result.y():.2f}, {result.z():.2f})")
        return result
    
    def _on_tool_changed(self, tool: ToolType):
        """Handle tool change notification"""
        descriptions = create_tool_descriptions()
        self.status_message.emit(f"Tool: {tool.value.title()} - {descriptions.get(tool, '')}")
        
        # Disable camera controller when CAD tool is active
        if tool:
            print(f"Disabling camera controller for tool: {tool.value}")
            self.camController.setEnabled(False)
        else:
            print("Re-enabling camera controller")
            self.camController.setEnabled(True)
    
    def _on_geometry_updated(self):
        """Handle geometry update notification"""
        self.status_message.emit("Geometry updated")
    
    def get_cad_manager(self) -> CADToolManager:
        """Get the CAD tools manager"""
        return self.cad_manager


class CADToolPanel(QWidget):
    """Panel containing CAD tool buttons and options"""
    
    def __init__(self, cad_manager: CADToolManager, parent=None):
        super().__init__(parent)
        self.cad_manager = cad_manager
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the tool panel UI"""
        layout = QVBoxLayout(self)
        
        # Work plane selection
        plane_group = QGroupBox("Work Plane")
        plane_layout = QVBoxLayout(plane_group)
        
        self.plane_combo = QComboBox()
        self.plane_combo.addItems(["XY Plane", "XZ Plane", "YZ Plane"])
        self.plane_combo.currentTextChanged.connect(self._on_plane_changed)
        plane_layout.addWidget(self.plane_combo)
        layout.addWidget(plane_group)
        
        # Tool categories
        tools_by_category = {}
        for tool in ToolType:
            category = get_tool_category(tool)
            if category not in tools_by_category:
                tools_by_category[category] = []
            tools_by_category[category].append(tool)
        
        descriptions = create_tool_descriptions()
        
        for category, tools in tools_by_category.items():
            group = QGroupBox(category)
            group_layout = QVBoxLayout(group)
            
            for tool in tools:
                btn = QPushButton(tool.value.title())
                btn.setToolTip(descriptions.get(tool, ""))
                btn.setCheckable(True)  # Make buttons checkable
                btn.clicked.connect(lambda checked, t=tool, b=btn: self._on_tool_selected(t, b))
                group_layout.addWidget(btn)
                
                # Store button reference for later use
                if not hasattr(self, 'tool_buttons'):
                    self.tool_buttons = {}
                self.tool_buttons[tool] = btn
            
            layout.addWidget(group)
        
        # 3D Operations
        operations_group = QGroupBox("3D Operations")
        operations_layout = QVBoxLayout(operations_group)
        
        # Extrude controls
        extrude_btn = QPushButton("Extrude Selected Sketch")
        extrude_btn.clicked.connect(self._on_extrude_clicked)
        operations_layout.addWidget(extrude_btn)
        
        self.extrude_distance = QDoubleSpinBox()
        self.extrude_distance.setRange(-100.0, 100.0)
        self.extrude_distance.setValue(1.0)
        self.extrude_distance.setSuffix(" units")
        operations_layout.addWidget(QLabel("Extrude Distance:"))
        operations_layout.addWidget(self.extrude_distance)
        
        # Revolve controls
        revolve_btn = QPushButton("Revolve Selected Sketch")
        revolve_btn.clicked.connect(self._on_revolve_clicked)
        operations_layout.addWidget(revolve_btn)
        
        self.revolve_angle = QSpinBox()
        self.revolve_angle.setRange(1, 360)
        self.revolve_angle.setValue(360)
        self.revolve_angle.setSuffix("°")
        operations_layout.addWidget(QLabel("Revolve Angle:"))
        operations_layout.addWidget(self.revolve_angle)
        
        layout.addWidget(operations_group)
        
        # Actions
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        finish_sketch_btn = QPushButton("Finish Current Sketch")
        finish_sketch_btn.clicked.connect(self.cad_manager.finish_sketch)
        actions_layout.addWidget(finish_sketch_btn)
        
        clear_all_btn = QPushButton("Clear All")
        clear_all_btn.clicked.connect(self._clear_all)
        actions_layout.addWidget(clear_all_btn)
        
        layout.addWidget(actions_group)
        
        # Stretch to fill remaining space
        layout.addStretch()
    
    def _on_tool_selected(self, tool: ToolType, button: QPushButton):
        """Handle tool selection"""
        # Uncheck all other tool buttons
        for t, btn in self.tool_buttons.items():
            btn.setChecked(t == tool)
        
        self.cad_manager.set_active_tool(tool)
        print(f"Tool selected: {tool.value}")  # Debug output
    
    def _on_plane_changed(self, plane_text: str):
        """Handle work plane change"""
        plane_map = {
            "XY Plane": WorkPlane.XY,
            "XZ Plane": WorkPlane.XZ,
            "YZ Plane": WorkPlane.YZ
        }
        plane = plane_map.get(plane_text, WorkPlane.XY)
        self.cad_manager.set_work_plane(plane)
    
    def _on_extrude_clicked(self):
        """Handle extrude button click"""
        # Find the most recent sketch with closed profiles
        sketches_with_profiles = [s for s in self.cad_manager.sketches 
                                if s.get_closed_profiles()]
        if sketches_with_profiles:
            sketch = sketches_with_profiles[-1]  # Use most recent
            distance = self.extrude_distance.value()
            self.cad_manager.create_extrude(sketch, distance)
        else:
            print("No closed profiles available for extrusion")
    
    def _on_revolve_clicked(self):
        """Handle revolve button click"""
        from cad_tools import Point2D
        
        sketches_with_profiles = [s for s in self.cad_manager.sketches 
                                if s.get_closed_profiles()]
        if sketches_with_profiles:
            sketch = sketches_with_profiles[-1]
            angle = self.revolve_angle.value()
            # Use Y-axis as default revolve axis
            axis_point = Point2D(0, 0)
            axis_direction = Point2D(0, 1)
            self.cad_manager.create_revolve(sketch, axis_point, axis_direction, angle)
        else:
            print("No closed profiles available for revolution")
    
    def _clear_all(self):
        """Clear all sketches and features"""
        # Clear features first (they may depend on sketches)
        for feature in self.cad_manager.features.copy():
            self.cad_manager.delete_feature(feature)
        
        # Clear sketches
        for sketch in self.cad_manager.sketches.copy():
            self.cad_manager.delete_sketch(sketch)


class CADMainWindow(QMainWindow):
    """Main window for the CAD application"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D CAD Learning Tool")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Create viewport
        self.viewport = CADViewport3D()
        self.viewport.status_message.connect(self._update_status)
        
        # Create tool panel
        self.tool_panel = CADToolPanel(self.viewport.get_cad_manager())
        self.tool_panel.setMaximumWidth(300)
        self.tool_panel.setMinimumWidth(250)
        
        # Create info panel
        self.info_panel = self._create_info_panel()
        self.info_panel.setMaximumWidth(300)
        self.info_panel.setMinimumWidth(250)
        
        # Add to splitter
        splitter.addWidget(self.tool_panel)
        splitter.addWidget(self.viewport)
        splitter.addWidget(self.info_panel)
        
        # Set splitter proportions (tool panel, viewport, info panel)
        splitter.setSizes([250, 700, 250])
        
        # Main layout
        layout = QHBoxLayout(main_widget)
        layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready - Select a tool to begin")
    
    def _create_info_panel(self) -> QWidget:
        """Create the information/help panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Instructions
        instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout(instructions_group)
        
        instructions_text = QTextEdit()
        instructions_text.setReadOnly(True)
        instructions_text.setHtml("""
        <h3>How to Use:</h3>
        <p><b>Sketching:</b></p>
        <ul>
        <li>Select a sketch tool (Line, Rectangle, Circle, Polygon)</li>
        <li>Choose your work plane (XY, XZ, YZ)</li>
        <li>Left-click in the viewport to create points</li>
        <li>Right-click to finish polygons</li>
        </ul>
        
        <p><b>3D Modeling:</b></p>
        <ul>
        <li>Create closed sketches (rectangles, circles, polygons)</li>
        <li>Use "Extrude" to turn 2D shapes into 3D</li>
        <li>Use "Revolve" to spin shapes around an axis</li>
        </ul>
        
        <p><b>Camera Controls:</b></p>
        <ul>
        <li>Left Mouse Drag: Orbit around scene</li>
        <li>Right Mouse Drag: Pan camera</li>
        <li>Mouse Wheel: Zoom in/out</li>
        </ul>
        """)
        instructions_layout.addWidget(instructions_text)
        layout.addWidget(instructions_group)
        
        # Scene info
        scene_group = QGroupBox("Scene Info")
        scene_layout = QVBoxLayout(scene_group)
        
        self.scene_info = QTextEdit()
        self.scene_info.setReadOnly(True)
        self.scene_info.setMaximumHeight(150)
        scene_layout.addWidget(self.scene_info)
        layout.addWidget(scene_group)
        
        # Update scene info
        self._update_scene_info()
        
        return panel
    
    def _update_status(self, message: str):
        """Update status bar message"""
        self.statusBar().showMessage(message)
    
    def _update_scene_info(self):
        """Update scene information display"""
        cad_manager = self.viewport.get_cad_manager()
        
        info_text = f"""
        <b>Sketches:</b> {len(cad_manager.sketches)}<br>
        <b>3D Features:</b> {len(cad_manager.features)}<br>
        <b>Active Tool:</b> {cad_manager.active_tool.value if cad_manager.active_tool else "None"}<br>
        <b>Work Plane:</b> {cad_manager.active_work_plane.value}<br>
        """
        
        self.scene_info.setHtml(info_text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = CADMainWindow()
    window.show()
    
    sys.exit(app.exec())