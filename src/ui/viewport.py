"""
Viewport - 3D rendering widget for CAD operations
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette

class Viewport(QWidget):
    """3D viewport widget for displaying and interacting with CAD geometry"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the viewport user interface"""
        # Set minimum size
        self.setMinimumSize(600, 400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Temporary placeholder - will be replaced with 3D rendering
        placeholder = QLabel("3D Viewport\n(3D rendering will be implemented in Phase 2)")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                background-color: #2e2e2e;
                color: #ffffff;
                font-size: 16px;
                border: 2px dashed #555555;
                padding: 20px;
            }
        """)
        
        layout.addWidget(placeholder)
        
        # Set dark background for viewport area
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, Qt.darkGray)
        self.setPalette(palette)
        
    def reset_camera(self):
        """Reset camera to default position (placeholder)"""
        print("Camera reset - will be implemented in Phase 2")
        
    def mousePressEvent(self, event):
        """Handle mouse press events (placeholder)"""
        print(f"Mouse press at ({event.position().x()}, {event.position().y()})")
        
    def mouseMoveEvent(self, event):
        """Handle mouse move events (placeholder)"""
        # Only print if mouse button is pressed
        if event.buttons() != Qt.NoButton:
            print(f"Mouse drag to ({event.position().x()}, {event.position().y()})")
            
    def wheelEvent(self, event):
        """Handle mouse wheel events (placeholder)"""
        delta = event.angleDelta().y()
        print(f"Mouse wheel: {delta}")