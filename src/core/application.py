"""
CAD Application - Core application controller
"""

from PySide6.QtCore import QObject
from src.ui.main_window import MainWindow

class CADApplication(QObject):
    """Main application controller that manages the overall application state"""
    
    def __init__(self):
        super().__init__()
        self.main_window = None
        self.current_document = None
        
    def run(self):
        """Initialize and show the main application window"""
        self.main_window = MainWindow()
        self.main_window.show()
        
    def get_main_window(self):
        """Get reference to main window"""
        return self.main_window