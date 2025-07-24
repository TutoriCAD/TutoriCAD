"""
Main Window - Primary application window with menus and viewport
"""

from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QMenuBar, QStatusBar, QSplitter)
from PySide6.QtCore import Qt
from src.ui.viewport import Viewport

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.viewport = None
        self.setup_ui()
        self.setup_menus()
        self.setup_status_bar()
        
    def setup_ui(self):
        """Setup the main user interface"""
        self.setWindowTitle("CAD Tutorial Application")
        self.setMinimumSize(1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Create viewport (main 3D area)
        self.viewport = Viewport()
        splitter.addWidget(self.viewport)
        
        # Set splitter proportions (viewport takes most space)
        splitter.setSizes([800, 200])
        
    def setup_menus(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New", self.new_document)
        file_menu.addAction("Open", self.open_document)
        file_menu.addAction("Save", self.save_document)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Undo", self.undo)
        edit_menu.addAction("Redo", self.redo)
        
        # View menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Reset Camera", self.reset_camera)
        view_menu.addAction("Fit All", self.fit_all)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Line", self.select_line_tool)
        tools_menu.addAction("Rectangle", self.select_rectangle_tool)
        tools_menu.addAction("Circle", self.select_circle_tool)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About", self.show_about)
        
    def setup_status_bar(self):
        """Create the status bar"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
    # Menu action handlers (placeholder implementations)
    def new_document(self):
        self.status_bar.showMessage("New document")
        
    def open_document(self):
        self.status_bar.showMessage("Open document")
        
    def save_document(self):
        self.status_bar.showMessage("Save document")
        
    def undo(self):
        self.status_bar.showMessage("Undo")
        
    def redo(self):
        self.status_bar.showMessage("Redo")
        
    def reset_camera(self):
        if self.viewport:
            self.viewport.reset_camera()
        self.status_bar.showMessage("Camera reset")
        
    def fit_all(self):
        self.status_bar.showMessage("Fit all")
        
    def select_line_tool(self):
        self.status_bar.showMessage("Line tool selected")
        
    def select_rectangle_tool(self):
        self.status_bar.showMessage("Rectangle tool selected")
        
    def select_circle_tool(self):
        self.status_bar.showMessage("Circle tool selected")
        
    def show_about(self):
        self.status_bar.showMessage("About CAD Tutorial")