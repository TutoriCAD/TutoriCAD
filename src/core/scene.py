
# src/core/scene.py
"""
Scene management for 3D objects and rendering state.
Phase 2.1 - Clean, simple scene container
"""

from typing import List


class SceneObject:
    """Base class for all renderable objects."""
    
    def __init__(self, name: str = "Object"):
        self.name = name
        self.visible = True
        self.selected = False


class TestObjects:
    """Collection of test objects to verify 3D rendering works."""
    
    @staticmethod
    def get_coordinate_axes():
        """Get coordinate axes data."""
        return {
            'name': 'Coordinate Axes',
            'lines': [
                # X axis (red)
                {'start': [0, 0, 0], 'end': [3, 0, 0], 'color': 'red'},
                # Y axis (green)  
                {'start': [0, 0, 0], 'end': [0, 3, 0], 'color': 'green'},
                # Z axis (blue)
                {'start': [0, 0, 0], 'end': [0, 0, 3], 'color': 'blue'},
            ]
        }
    
    @staticmethod
    def get_test_cube():
        """Get test cube data."""
        return {
            'name': 'Test Cube',
            'position': [0, 0, 0.5],  # Slightly above origin
            'size': [1, 1, 1],
            'color': 'white'
        }


class Scene:
    """Main scene container - keeps it simple for Phase 2."""
    
    def __init__(self):
        self.objects: List[SceneObject] = []
        self.test_mode = True  # Phase 2 test mode
        
        print("Scene initialized for Phase 2")