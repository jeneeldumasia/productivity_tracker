import datetime
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QMenu, QAction
from PyQt5.QtCore import Qt, pyqtSignal, QPoint

class CompactModeWidget(QWidget):
    # Define signals that the main window can connect to
    show_full_window_requested = pyqtSignal()
    exit_requested = pyqtSignal()
    pause_requested = pyqtSignal()

    def __init__(self, main_window):
        super().__init__(parent=None) # This makes it an independent window
        self.main_window = main_window
        # --- Widget Styling and Behavior ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 300, 80)

        # --- UI Elements ---
        self.container = QWidget(self)
        self.container.setObjectName("compactWidgetCard")
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(15, 10, 15, 10)
        
        self.app_name_label = QLabel("Initializing...")
        self.app_name_label.setObjectName("compactAppName")
        self.app_name_label.setAlignment(Qt.AlignCenter)
        
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setObjectName("compactTimer")
        self.timer_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.app_name_label)
        layout.addWidget(self.timer_label)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.container)
        self.setLayout(main_layout)

        self._drag_pos = QPoint()

    def update_display(self, current_activity, is_paused):
        """Public method to update the labels from the main window."""
        is_dark = self.main_window.config.get('is_dark_mode', False)
        
        if is_paused:
            self.app_name_label.setText("Tracking Paused")
            self.timer_label.setText("00:00:00")
            # Set a distinct color for the paused state
            text_color = "#FFA726" # A nice orange color
        else:
            if current_activity:
                app_name = current_activity.get('app_name', 'N/A')
                if len(app_name) > 35:
                    app_name = app_name[:32] + "..."
                
                self.app_name_label.setText(app_name)
                
                duration = (datetime.datetime.now() - current_activity.get('start_time', datetime.datetime.now())).total_seconds()
                duration_str = str(datetime.timedelta(seconds=int(duration)))
                self.timer_label.setText(duration_str)
            
            text_color = "#F0F0F0" if is_dark else "#222"

        self.app_name_label.setStyleSheet(f"color: {text_color}; font-size: 14px;")
        self.timer_label.setStyleSheet(f"color: {text_color}; font-size: 20px; font-weight: bold;")
        
        is_dark = self.main_window.config.get('is_dark_mode', False)
        text_color = "#F0F0F0" if is_dark else "#222"
        self.app_name_label.setStyleSheet(f"color: {text_color}; font-size: 14px;")
        self.timer_label.setStyleSheet(f"color: {text_color}; font-size: 20px; font-weight: bold;")

    def contextMenuEvent(self, event):
        """Create a right-click context menu."""
        context_menu = QMenu(self)
        
        pause_action = context_menu.addAction("Pause/Resume Tracking")
        show_full_action = context_menu.addAction("Show Full Window")
        context_menu.addSeparator()
        exit_action = context_menu.addAction("Exit")
        
        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        
        if action == show_full_action:
            self.show_full_window_requested.emit()
        elif action == exit_action:
            self.exit_requested.emit()
        elif action == pause_action:
            self.pause_requested.emit()

    def mousePressEvent(self, event):
        self._drag_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self._drag_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self._drag_pos = event.globalPos()