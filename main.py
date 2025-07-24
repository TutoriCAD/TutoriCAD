#!/usr/bin/env python3
"""
CAD Tutorial Application - Main Entry Point
"""

import sys
from PySide6.QtWidgets import QApplication
from src.core.application import CADApplication

def main():
    """Main application entry point"""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("CAD Tutorial")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("CAD Tutorial App")
    
    # Create and run CAD application
    cad_app = CADApplication()
    cad_app.run()
    
    # Start Qt event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()