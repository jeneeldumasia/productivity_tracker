import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

# --- Start of fix ---
# This ensures the application finds the modules correctly when run as a script.
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
# --- End of fix ---

from ui.main_window import ProductivityTrackerApp

if __name__ == '__main__':
    """
    Main entry point for the Automated ProductivityTracker application.
    """
    app = QApplication(sys.argv)
    
    # Set a modern, clean default font for the entire application
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Instantiate and show the main application window
    main_app = ProductivityTrackerApp()
    main_app.show()
    
    # Start the application's event loop
    sys.exit(app.exec_())