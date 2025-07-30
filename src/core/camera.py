# src/core/camera.py
"""
Camera system for 3D viewport navigation.
Phase 2.2 - Simple camera that works with Qt3D's built-in controls
"""


class Camera:
    """Simple camera class that tracks basic state."""
    
    def __init__(self):
        # Basic camera state (Qt3D will handle the actual camera)
        self.initialized = False
        
        # Default settings
        self.fov = 45.0
        self.near_plane = 0.1
        self.far_plane = 1000.0
        
        print("Camera system initialized for Phase 2")
    
    def mark_initialized(self):
        """Mark camera as initialized by Qt3D."""
        self.initialized = True
        print("Camera marked as initialized")
    
    def is_ready(self):
        """Check if camera is ready for use."""
        return self.initialized