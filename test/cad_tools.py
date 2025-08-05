"""
cad_tools.py
CAD Tools system for 3D modeling application.
Includes sketching, 3D operations, and tool management.
"""

import math
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Tuple
from PySide6.QtCore import QObject, Signal, QPointF
from PySide6.QtGui import QVector3D, QColor, QVector2D
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.Qt3DRender import Qt3DRender

# Aliases
QEntity = Qt3DCore.QEntity
QTransform = Qt3DCore.QTransform
QCuboidMesh = Qt3DExtras.QCuboidMesh
QCylinderMesh = Qt3DExtras.QCylinderMesh
QSphereMesh = Qt3DExtras.QSphereMesh
QPhongMaterial = Qt3DExtras.QPhongMaterial


class ToolType(Enum):
    """Available CAD tool types"""
    # Sketch tools
    LINE = "line"
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    POLYGON = "polygon"
    
    # 3D operations
    EXTRUDE = "extrude"
    REVOLVE = "revolve"
    SWEEP = "sweep"
    LOFT = "loft"
    
    # Modification tools
    MOVE = "move"
    ROTATE = "rotate"
    SCALE = "scale"
    MIRROR = "mirror"
    
    # Boolean operations
    UNION = "union"
    SUBTRACT = "subtract"
    INTERSECT = "intersect"


class WorkPlane(Enum):
    """Standard work planes for sketching"""
    XY = "xy"
    XZ = "xz" 
    YZ = "yz"
    CUSTOM = "custom"


@dataclass
class Point2D:
    """2D point for sketching"""
    x: float
    y: float
    
    def to_vector2d(self) -> QVector2D:
        return QVector2D(self.x, self.y)
    
    def distance_to(self, other: 'Point2D') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


@dataclass
class SketchGeometry:
    """Base class for 2D sketch elements"""
    points: List[Point2D]
    closed: bool = False
    
    def get_bounds(self) -> Tuple[Point2D, Point2D]:
        """Get bounding box of the sketch geometry"""
        if not self.points:
            return Point2D(0, 0), Point2D(0, 0)
        
        min_x = min(p.x for p in self.points)
        max_x = max(p.x for p in self.points)
        min_y = min(p.y for p in self.points)
        max_y = max(p.y for p in self.points)
        
        return Point2D(min_x, min_y), Point2D(max_x, max_y)


class Sketch:
    """2D sketch on a work plane"""
    def __init__(self, work_plane: WorkPlane = WorkPlane.XY):
        self.work_plane = work_plane
        self.geometry: List[SketchGeometry] = []
        self.active = True
        self.visible = True
        
    def add_geometry(self, geom: SketchGeometry):
        self.geometry.append(geom)
    
    def get_closed_profiles(self) -> List[SketchGeometry]:
        """Get all closed profiles suitable for 3D operations"""
        return [g for g in self.geometry if g.closed]
    
    def world_to_sketch_coords(self, world_point: QVector3D) -> Point2D:
        """Convert 3D world coordinates to 2D sketch coordinates"""
        if self.work_plane == WorkPlane.XY:
            return Point2D(world_point.x(), world_point.y())
        elif self.work_plane == WorkPlane.XZ:
            return Point2D(world_point.x(), world_point.z())
        elif self.work_plane == WorkPlane.YZ:
            return Point2D(world_point.y(), world_point.z())
        else:
            # Custom plane - simplified for now
            return Point2D(world_point.x(), world_point.y())
    
    def sketch_to_world_coords(self, sketch_point: Point2D, depth: float = 0) -> QVector3D:
        """Convert 2D sketch coordinates to 3D world coordinates"""
        if self.work_plane == WorkPlane.XY:
            return QVector3D(sketch_point.x, sketch_point.y, depth)
        elif self.work_plane == WorkPlane.XZ:
            return QVector3D(sketch_point.x, depth, sketch_point.y)
        elif self.work_plane == WorkPlane.YZ:
            return QVector3D(depth, sketch_point.x, sketch_point.y)
        else:
            return QVector3D(sketch_point.x, sketch_point.y, depth)


class Feature3D:
    """Base class for 3D modeling operations"""
    def __init__(self, name: str):
        self.name = name
        self.visible = True
        self.entity: Optional[QEntity] = None
        
    def create_geometry(self, parent_entity: QEntity) -> QEntity:
        """Create the 3D geometry for this feature"""
        raise NotImplementedError
        
    def update_geometry(self):
        """Update the 3D geometry after parameter changes"""
        pass


class ExtrudeFeature(Feature3D):
    """Extrude a 2D sketch into 3D"""
    def __init__(self, sketch: Sketch, distance: float, name: str = "Extrude"):
        super().__init__(name)
        self.sketch = sketch
        self.distance = distance
        
    def create_geometry(self, parent_entity: QEntity) -> QEntity:
        """Create extruded geometry from sketch profiles"""
        self.entity = QEntity(parent_entity)
        
        # For now, create simple box extrusion from first closed profile
        closed_profiles = self.sketch.get_closed_profiles()
        if not closed_profiles:
            return self.entity
            
        profile = closed_profiles[0]
        min_pt, max_pt = profile.get_bounds()
        
        # Create box mesh
        mesh = QCuboidMesh()
        width = max_pt.x - min_pt.x
        height = max_pt.y - min_pt.y
        depth = abs(self.distance)
        
        mesh.setXExtent(width)
        mesh.setYExtent(height) 
        mesh.setZExtent(depth)
        
        self.entity.addComponent(mesh)
        
        # Material
        material = QPhongMaterial()
        material.setDiffuse(QColor.fromRgbF(0.0, 0.7, 1.0))  # Blue
        material.setAmbient(QColor.fromRgbF(0.0, 0.2, 0.3))
        self.entity.addComponent(material)
        
        # Transform
        transform = QTransform()
        center_x = (min_pt.x + max_pt.x) / 2
        center_y = (min_pt.y + max_pt.y) / 2
        center_z = self.distance / 2
        
        # Convert sketch coordinates to world coordinates
        world_center = self.sketch.sketch_to_world_coords(
            Point2D(center_x, center_y), center_z
        )
        transform.setTranslation(world_center)
        self.entity.addComponent(transform)
        
        return self.entity


class RevolveFeature(Feature3D):
    """Revolve a 2D sketch around an axis"""
    def __init__(self, sketch: Sketch, axis_point: Point2D, axis_direction: Point2D, 
                 angle: float = 360, name: str = "Revolve"):
        super().__init__(name)
        self.sketch = sketch
        self.axis_point = axis_point
        self.axis_direction = axis_direction
        self.angle = angle
        
    def create_geometry(self, parent_entity: QEntity) -> QEntity:
        """Create revolved geometry (simplified as cylinder for demo)"""
        self.entity = QEntity(parent_entity)
        
        closed_profiles = self.sketch.get_closed_profiles()
        if not closed_profiles:
            return self.entity
            
        profile = closed_profiles[0]
        min_pt, max_pt = profile.get_bounds()
        
        # Simplified: create cylinder
        mesh = QCylinderMesh()
        radius = max(abs(max_pt.x), abs(min_pt.x))
        height = max_pt.y - min_pt.y
        
        mesh.setRadius(radius)
        mesh.setLength(height)
        
        self.entity.addComponent(mesh)
        
        # Material
        material = QPhongMaterial()
        material.setDiffuse(QColor.fromRgbF(1.0, 0.5, 0.0))  # Orange
        material.setAmbient(QColor.fromRgbF(0.3, 0.15, 0.0))
        self.entity.addComponent(material)
        
        # Transform
        transform = QTransform()
        center_y = (min_pt.y + max_pt.y) / 2
        world_center = self.sketch.sketch_to_world_coords(
            Point2D(0, center_y), 0
        )
        transform.setTranslation(world_center)
        self.entity.addComponent(transform)
        
        return self.entity


class CADToolManager(QObject):
    """Manages CAD tools and operations"""
    
    # Signals
    tool_changed = Signal(ToolType)
    sketch_created = Signal(Sketch)
    feature_created = Signal(Feature3D)
    geometry_updated = Signal()
    
    def __init__(self, viewport_root_entity: QEntity):
        super().__init__()
        self.root_entity = viewport_root_entity
        self.active_tool = None
        self.active_sketch = None
        self.active_work_plane = WorkPlane.XY
        
        # Collections
        self.sketches: List[Sketch] = []
        self.features: List[Feature3D] = []
        
        # Temporary drawing state
        self.current_points: List[Point2D] = []
        self.is_drawing = False
        
    def set_active_tool(self, tool: ToolType):
        """Set the currently active tool"""
        self.active_tool = tool
        if tool:  # Only emit if tool is not None
            self.tool_changed.emit(tool)
        
        # Reset drawing state when switching tools
        self.current_points.clear()
        self.is_drawing = False
    
    def set_work_plane(self, plane: WorkPlane):
        """Set the active work plane for sketching"""
        self.active_work_plane = plane
        
        # End current sketch if switching planes
        if self.active_sketch and self.active_sketch.work_plane != plane:
            self.finish_sketch()
    
    def start_sketch(self, plane: WorkPlane = None):
        """Start a new sketch"""
        if plane is None:
            plane = self.active_work_plane
            
        self.active_sketch = Sketch(plane)
        self.sketches.append(self.active_sketch)
        self.sketch_created.emit(self.active_sketch)
    
    def finish_sketch(self):
        """Finish the current sketch"""
        if self.active_sketch:
            self.active_sketch.active = False
            self.active_sketch = None
    
    def handle_click(self, world_point: QVector3D) -> bool:
        """Handle mouse click in 3D viewport"""
        if not self.active_tool:
            return False
            
        # Ensure we have an active sketch for sketch tools
        if self.active_tool in [ToolType.LINE, ToolType.RECTANGLE, ToolType.CIRCLE, ToolType.POLYGON]:
            if not self.active_sketch:
                self.start_sketch()
                
            return self._handle_sketch_click(world_point)
        
        return False
    
    def _handle_sketch_click(self, world_point: QVector3D) -> bool:
        """Handle clicks for sketching tools"""
        if not self.active_sketch:
            return False
            
        sketch_point = self.active_sketch.world_to_sketch_coords(world_point)
        
        if self.active_tool == ToolType.LINE:
            return self._handle_line_click(sketch_point)
        elif self.active_tool == ToolType.RECTANGLE:
            return self._handle_rectangle_click(sketch_point)
        elif self.active_tool == ToolType.CIRCLE:
            return self._handle_circle_click(sketch_point)
        elif self.active_tool == ToolType.POLYGON:
            return self._handle_polygon_click(sketch_point)
            
        return False
    
    def _handle_line_click(self, point: Point2D) -> bool:
        """Handle line drawing"""
        self.current_points.append(point)
        
        if len(self.current_points) >= 2:
            # Create line geometry
            line_geom = SketchGeometry(self.current_points.copy(), closed=False)
            self.active_sketch.add_geometry(line_geom)
            
            # Start new line from last point
            self.current_points = [self.current_points[-1]]
            
            self.geometry_updated.emit()
            return True
        
        return False
    
    def _handle_rectangle_click(self, point: Point2D) -> bool:
        """Handle rectangle drawing"""
        self.current_points.append(point)
        
        if len(self.current_points) >= 2:
            # Create rectangle from diagonal points
            p1, p2 = self.current_points[0], self.current_points[1]
            rect_points = [
                Point2D(p1.x, p1.y),
                Point2D(p2.x, p1.y),
                Point2D(p2.x, p2.y),
                Point2D(p1.x, p2.y)
            ]
            
            rect_geom = SketchGeometry(rect_points, closed=True)
            self.active_sketch.add_geometry(rect_geom)
            
            self.current_points.clear()
            self.geometry_updated.emit()
            return True
        
        return False
    
    def _handle_circle_click(self, point: Point2D) -> bool:
        """Handle circle drawing"""
        self.current_points.append(point)
        
        if len(self.current_points) >= 2:
            center = self.current_points[0]
            edge = self.current_points[1]
            radius = center.distance_to(edge)
            
            # Create circle as polygon approximation
            circle_points = []
            segments = 16
            for i in range(segments):
                angle = 2 * math.pi * i / segments
                x = center.x + radius * math.cos(angle)
                y = center.y + radius * math.sin(angle)
                circle_points.append(Point2D(x, y))
            
            circle_geom = SketchGeometry(circle_points, closed=True)
            self.active_sketch.add_geometry(circle_geom)
            
            self.current_points.clear()
            self.geometry_updated.emit()
            return True
        
        return False
    
    def _handle_polygon_click(self, point: Point2D) -> bool:
        """Handle polygon drawing (right-click to finish)"""
        self.current_points.append(point)
        return False  # Don't auto-finish, wait for finish_current_geometry()
    
    def finish_current_geometry(self):
        """Finish the current geometry being drawn"""
        if not self.current_points or not self.active_sketch:
            return
            
        if self.active_tool == ToolType.POLYGON and len(self.current_points) >= 3:
            poly_geom = SketchGeometry(self.current_points.copy(), closed=True)
            self.active_sketch.add_geometry(poly_geom)
            self.geometry_updated.emit()
        
        self.current_points.clear()
    
    def create_extrude(self, sketch: Sketch, distance: float) -> ExtrudeFeature:
        """Create an extrude feature from a sketch"""
        feature = ExtrudeFeature(sketch, distance)
        feature.create_geometry(self.root_entity)
        self.features.append(feature)
        self.feature_created.emit(feature)
        return feature
    
    def create_revolve(self, sketch: Sketch, axis_point: Point2D, 
                      axis_direction: Point2D, angle: float = 360) -> RevolveFeature:
        """Create a revolve feature from a sketch"""
        feature = RevolveFeature(sketch, axis_point, axis_direction, angle)
        feature.create_geometry(self.root_entity)
        self.features.append(feature)
        self.feature_created.emit(feature)
        return feature
    
    def get_available_tools(self) -> List[ToolType]:
        """Get list of available tools"""
        return list(ToolType)
    
    def can_extrude(self) -> bool:
        """Check if we can perform extrude operation"""
        return any(sketch.get_closed_profiles() for sketch in self.sketches)
    
    def can_revolve(self) -> bool:
        """Check if we can perform revolve operation"""
        return any(sketch.get_closed_profiles() for sketch in self.sketches)
    
    def delete_feature(self, feature: Feature3D):
        """Delete a 3D feature"""
        if feature in self.features:
            if feature.entity:
                # Remove from scene
                feature.entity.setParent(None)  # This should remove it from Qt3D scene
            self.features.remove(feature)
            self.geometry_updated.emit()
    
    def delete_sketch(self, sketch: Sketch):
        """Delete a sketch"""
        if sketch in self.sketches:
            # Also delete any features that depend on this sketch
            dependent_features = [f for f in self.features 
                                if hasattr(f, 'sketch') and f.sketch == sketch]
            for feature in dependent_features:
                self.delete_feature(feature)
                
            self.sketches.remove(sketch)
            self.geometry_updated.emit()


# Helper functions for tool UI integration
def create_tool_descriptions() -> dict:
    """Get user-friendly descriptions for each tool"""
    return {
        ToolType.LINE: "Draw connected line segments",
        ToolType.RECTANGLE: "Draw rectangles by diagonal corners", 
        ToolType.CIRCLE: "Draw circles by center and radius",
        ToolType.POLYGON: "Draw custom polygons (right-click to finish)",
        ToolType.EXTRUDE: "Extrude 2D sketches into 3D",
        ToolType.REVOLVE: "Revolve 2D sketches around an axis",
        ToolType.SWEEP: "Sweep profile along a path",
        ToolType.LOFT: "Blend between multiple profiles",
        ToolType.MOVE: "Move objects in 3D space",
        ToolType.ROTATE: "Rotate objects around an axis",
        ToolType.SCALE: "Resize objects uniformly or non-uniformly",
        ToolType.MIRROR: "Mirror objects across a plane",
        ToolType.UNION: "Combine solid bodies together",
        ToolType.SUBTRACT: "Remove one body from another",
        ToolType.INTERSECT: "Keep only the intersection of bodies"
    }


def get_tool_category(tool: ToolType) -> str:
    """Get the category for a tool (for UI organization)"""
    sketch_tools = [ToolType.LINE, ToolType.RECTANGLE, ToolType.CIRCLE, ToolType.POLYGON]
    modeling_tools = [ToolType.EXTRUDE, ToolType.REVOLVE, ToolType.SWEEP, ToolType.LOFT]
    transform_tools = [ToolType.MOVE, ToolType.ROTATE, ToolType.SCALE, ToolType.MIRROR]
    boolean_tools = [ToolType.UNION, ToolType.SUBTRACT, ToolType.INTERSECT]
    
    if tool in sketch_tools:
        return "Sketch"
    elif tool in modeling_tools:
        return "3D Modeling"
    elif tool in transform_tools:
        return "Transform"
    elif tool in boolean_tools:
        return "Boolean"
    else:
        return "Other"