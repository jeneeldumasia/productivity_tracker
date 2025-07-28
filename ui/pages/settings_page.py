from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton, QLineEdit, QSpinBox, QScrollArea
from PyQt5.QtCore import Qt

class SettingsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setStyleSheet("background: transparent;")
        self._setup_ui()

    def _setup_ui(self):
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("pageScrollArea")
        content_card = QWidget()
        content_card.setObjectName("glassCard")

        layout = QVBoxLayout(content_card)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        layout.addWidget(QLabel("<h1>Settings</h1>"))
        
        theme_group = QGroupBox("Appearance")
        theme_layout = QHBoxLayout(theme_group)
        theme_layout.addWidget(QLabel("Interface Theme:"))
        self.theme_toggle_button = QPushButton()
        self.theme_toggle_button.clicked.connect(self.main_window.toggle_theme)
        theme_layout.addWidget(self.theme_toggle_button)
        layout.addWidget(theme_group)
        
        tracking_group = QGroupBox("Tracking Configuration")
        tracking_layout = QVBoxLayout(tracking_group)
        
        # --- Interval Setting ---
        interval_layout = QHBoxLayout()
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 60)
        self.interval_spinbox.setValue(self.main_window.config.get('check_interval_seconds', 3))
        interval_layout.addWidget(QLabel("Check interval (seconds):"))
        interval_layout.addWidget(self.interval_spinbox)
        interval_layout.addStretch()
        tracking_layout.addLayout(interval_layout)
        
        # --- Idle Threshold Setting ---
        idle_layout = QHBoxLayout()
        self.idle_spinbox = QSpinBox()
        self.idle_spinbox.setRange(1, 120) # 1 minute to 2 hours
        self.idle_spinbox.setValue(self.main_window.config.get('idle_threshold_minutes', 5))
        idle_layout.addWidget(QLabel("Idle threshold (minutes):"))
        idle_layout.addWidget(self.idle_spinbox)
        idle_layout.addStretch()
        tracking_layout.addLayout(idle_layout)

        # --- Productive Apps Setting ---
        apps_layout = QVBoxLayout()
        self.apps_input = QLineEdit(",".join(self.main_window.config.get('productivity_apps', [])))
        apps_layout.addWidget(QLabel("Productivity Keywords (comma-separated):"))
        apps_layout.addWidget(self.apps_input)
        tracking_layout.addLayout(apps_layout)
        
        save_button = QPushButton("Save Settings")
        save_button.clicked.connect(self.main_window.save_settings_handler)
        tracking_layout.addWidget(save_button, alignment=Qt.AlignRight)
        layout.addWidget(tracking_group)

        data_group = QGroupBox("Data Management")
        data_layout = QHBoxLayout(data_group)
        export_button = QPushButton("Export All Data (CSV)")
        export_button.clicked.connect(self.main_window.export_data)
        clear_button = QPushButton("Clear All Data")
        clear_button.clicked.connect(self.main_window.clear_data_prompt)
        data_layout.addWidget(export_button)
        data_layout.addWidget(clear_button)
        layout.addWidget(data_group)
        
        layout.addStretch()

        scroll_area.setWidget(content_card)
        page_layout.addWidget(scroll_area)

    def update_theme_button_text(self, is_dark):
        self.theme_toggle_button.setText("☀️ Switch to Light Mode" if is_dark else "🌙 Switch to Dark Mode")