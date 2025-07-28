import sys
import time
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

# --- Platform-specific imports for idle detection ---
IS_WINDOWS = sys.platform == "win32"
if IS_WINDOWS:
    try:
        import win32api
        import win32gui
    except ImportError:
        print("Warning: pywin32 is not installed. Idle detection and window tracking will not work.")
        IS_WINDOWS = False

def get_idle_time_seconds():
    """Returns the time in seconds since the last user input."""
    if IS_WINDOWS:
        try:
            last_input_info = win32api.GetLastInputInfo()
            return (win32api.GetTickCount() - last_input_info) / 1000.0
        except Exception:
            return 0
    return 0

def get_active_window_title():
    """Retrieves the title of the currently active foreground window."""
    if IS_WINDOWS:
        try:
            hwnd = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(hwnd)
        except Exception:
            return "Window Error (Win)"
            
    platform = sys.platform
    if platform == "darwin":
        return "macOS tracking not yet implemented"
    elif "linux" in platform:
        return "Linux tracking not yet implemented"
    return "Unknown OS"


class WindowDetector(QObject):
    """
    A QObject that detects active window changes and user idle time using a QTimer.
    """
    activity_changed = pyqtSignal(str)

    def __init__(self, check_interval_seconds, idle_threshold_minutes):
        super().__init__()
        self.idle_threshold_seconds = idle_threshold_minutes * 60
        
        self.timer = QTimer(self)
        self.timer.setInterval(check_interval_seconds * 1000)
        self.timer.timeout.connect(self._check_activity)

    def _check_activity(self):
        """This method is called by the QTimer to check for activity."""
        idle_time = get_idle_time_seconds()
        
        if self.idle_threshold_seconds > 0 and idle_time >= self.idle_threshold_seconds:
            current_activity_name = "Idle"
        else:
            current_activity_name = get_active_window_title()

        self.activity_changed.emit(current_activity_name)

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()