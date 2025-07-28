import sys
import time
from PyQt5.QtCore import QThread, pyqtSignal

def get_active_window_title():
    """
    Retrieves the title of the currently active foreground window
    using OS-specific libraries.
    """
    platform = sys.platform
    active_window_title = "Unknown"

    if platform == "win32":
        try:
            import win32gui
            hwnd = win32gui.GetForegroundWindow()
            active_window_title = win32gui.GetWindowText(hwnd)
        except ImportError:
            active_window_title = "Tracking requires pywin32 on Windows"
        except Exception:
            active_window_title = "Window Error (Win)"

    elif platform == "darwin": # macOS
        # Stub for macOS support
        # To implement, install py-get-active-window: pip install py-get-active-window
        active_window_title = "macOS tracking not yet implemented"

    elif "linux" in platform: # Linux
        # Stub for Linux support
        # To implement, install python-xlib: sudo apt-get install python3-xlib
        active_window_title = "Linux tracking not yet implemented"
             
    return active_window_title


class WindowDetector(QThread):
    """A QThread that detects active window changes."""
    active_window_changed = pyqtSignal(str)

    def __init__(self, check_interval):
        super().__init__()
        self._running = True
        self.check_interval = check_interval

    def run(self):
        while self._running:
            title = get_active_window_title()
            self.active_window_changed.emit(title)
            time.sleep(self.check_interval)

    def stop(self):
        self._running = False
        self.wait()