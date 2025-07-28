import sys
import time
from PyQt5.QtCore import QThread, pyqtSignal, QObject, QTimer

# --- Platform-specific imports for idle detection ---
IS_WINDOWS = sys.platform == "win32"
if IS_WINDOWS:
    try:
        import win32api
    except ImportError:
        print("Warning: pywin32 is not installed. Idle detection will not work.")
        IS_WINDOWS = False

def get_idle_time_seconds():
    """Returns the time in seconds since the last user input."""
    if IS_WINDOWS:
        try:
            last_input_info = win32api.GetLastInputInfo()
            # The result of GetTickCount is in milliseconds
            return (win32api.GetTickCount() - last_input_info) / 1000.0
        except Exception:
            return 0 # In case of an error, assume not idle
    # Stubs for other OSes
    # On macOS or Linux, you would implement a different method here.
    return 0

def get_active_window_title():
    """Retrieves the title of the currently active foreground window."""
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
        active_window_title = "macOS tracking not yet implemented"

    elif "linux" in platform: # Linux
        active_window_title = "Linux tracking not yet implemented"
             
    return active_window_title


class WindowDetector(QObject):
    """
    A QThread that detects active window changes and user idle time.
    """
    active_window_changed = pyqtSignal(str)
    activity_changed = pyqtSignal(str)  # Add this line

    def __init__(self, check_interval_seconds, idle_threshold_minutes):
        super().__init__()
        self._running = True
        self.check_interval = check_interval_seconds
        self.idle_threshold_seconds = idle_threshold_minutes * 60
        self.timer = QTimer(self)
        self.timer.setInterval(check_interval_seconds * 1000)
        self.timer.timeout.connect(self._check_active_window)

    def run(self):
        while self._running:
            idle_time = get_idle_time_seconds()
            
            # If user is idle, report "Idle". Otherwise, get the active window.
            if self.idle_threshold_seconds > 0 and idle_time >= self.idle_threshold_seconds:
                current_activity_name = "Idle"
            else:
                current_activity_name = get_active_window_title()

            self.active_window_changed.emit(current_activity_name)
            self.activity_changed.emit(current_activity_name)  # Emit the activity change signal
            time.sleep(self.check_interval)

    def stop(self):
        if hasattr(self, "timer"):
            self.timer.stop()
        # Remove or comment out self.wait()

    def start(self):
        self.timer.start()

    def _check_active_window(self):
        # Your logic to check the active window and emit the signal
        pass