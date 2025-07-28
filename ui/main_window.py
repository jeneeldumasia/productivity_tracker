import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QGraphicsBlurEffect, QMessageBox, QFileDialog
)
from PyQt5.QtCore import QCoreApplication, QEvent, QPropertyAnimation, QEasingCurve, Qt, QTimer

from data.data_handler import ensure_data_dir_and_files, load_config, save_config, append_activity, load_activities, update_activity_tags, update_last_activity_end_time
from tracking.window_detector import WindowDetector
from utils.helpers import get_clean_app_name
from utils.theme_manager import get_stylesheet

# Import the new page
from .pages.dashboard_page import DashboardPage
from .pages.log_pages import LogPage
from .pages.settings_page import SettingsPage
from .pages.weekly_report_page import WeeklyReportPage
from .widgets.compact_mode_widget import CompactModeWidget


class ProductivityTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        ensure_data_dir_and_files()
        self.config = load_config()
        self.current_activity = None
        self.last_app_name = ""
        self.is_paused = False

        self.compact_widget = CompactModeWidget(main_window=self)
        self.compact_widget.show_full_window_requested.connect(self.toggle_compact_mode)
        self.compact_widget.exit_requested.connect(self.close)
        self.compact_widget.pause_requested.connect(self.toggle_pause)

        self.setWindowTitle("Automated Productivity Tracker")
        self.setGeometry(100, 100, 1250, 850)
        self.setMinimumSize(1000, 700)

        self._setup_background()
        self._setup_ui()

        self.ui_timer = QTimer(self)
        self.ui_timer.setInterval(1000)
        self.ui_timer.timeout.connect(self.update_live_ui)
        self.ui_timer.start()

        self.apply_theme()
        self.init_and_start_tracker()
        self.update_all_ui()
        QCoreApplication.instance().aboutToQuit.connect(self.on_app_exit)

    def _create_collapsible_menu(self):
        self.nav_pane = QWidget()
        self.nav_pane.setObjectName("navPane")
        nav_layout = QVBoxLayout(self.nav_pane)
        nav_layout.setContentsMargins(5, 15, 5, 15)
        nav_layout.setAlignment(Qt.AlignTop)

        # Add the new button to the dictionary
        self.nav_buttons = {
            "📊  Dashboard": QPushButton("📊  Dashboard"),
            "📈  Weekly Report": QPushButton("📈  Weekly Report"),
            "📋  Activity Log": QPushButton("📋  Activity Log"),
            "⚙️  Settings": QPushButton("⚙️  Settings")
        }

        for text, button in self.nav_buttons.items():
            button.setObjectName("navButton")
            nav_layout.addWidget(button)
        
        nav_layout.addStretch()
        exit_button = QPushButton("❌  Exit")
        exit_button.setObjectName("navButton")
        exit_button.clicked.connect(self.close)
        nav_layout.addWidget(exit_button)

        self.nav_pane.setFixedWidth(0)
        self.main_layout.addWidget(self.nav_pane)
        self.menu_animation = QPropertyAnimation(self.nav_pane, b"minimumWidth")
        self.menu_animation.setDuration(250)
        self.menu_animation.setEasingCurve(QEasingCurve.InOutCubic)

    def _create_pages(self, parent_layout):
        self.stacked_widget = QStackedWidget()
        self.dashboard_page = DashboardPage(self)
        self.weekly_report_page = WeeklyReportPage(self) # Instantiate the new page
        self.log_page = LogPage(self)
        self.settings_page = SettingsPage(self)

        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.weekly_report_page) # Add it to the stacked widget
        self.stacked_widget.addWidget(self.log_page)
        self.stacked_widget.addWidget(self.settings_page)
        parent_layout.addWidget(self.stacked_widget)

        # Connect navigation buttons
        self.nav_buttons["📊  Dashboard"].clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.dashboard_page))
        self.nav_buttons["📈  Weekly Report"].clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.weekly_report_page))
        self.nav_buttons["📋  Activity Log"].clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.log_page))
        self.nav_buttons["⚙️  Settings"].clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.settings_page))
        
    def update_all_ui(self):
        activities = load_activities()
        self.log_page.display_activities(activities)
        self.dashboard_page.generate_activity_report(activities, self.config)
        self.weekly_report_page.update_report() # Ensure the weekly report also updates

    # ... (the rest of your main_window.py file remains unchanged)
    def handle_return_from_idle(self, idle_activity, new_app_name):
        idle_duration_minutes = round(idle_activity['duration_seconds'] / 60)
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Returned from Idle")
        msg_box.setText(f"You were idle for about {idle_duration_minutes} minutes.")
        msg_box.setInformativeText("How would you like to log this time?")
        log_break_button = msg_box.addButton("Log as Break", QMessageBox.YesRole)
        keep_time_button = msg_box.addButton("Keep Previous Activity Time", QMessageBox.NoRole)
        discard_button = msg_box.addButton("Discard Idle Time", QMessageBox.DestructiveRole)
        msg_box.exec_()
        clicked_button = msg_box.clickedButton()
        if clicked_button == log_break_button:
            idle_activity['app_name'] = "Break"
            append_activity(idle_activity)
        elif clicked_button == keep_time_button:
            update_last_activity_end_time(idle_activity['end_time'])
        elif clicked_button == discard_button:
            pass
        self.start_new_activity(new_app_name)
        self.update_all_ui()

    def start_new_activity(self, app_name):
        self.current_activity = {'app_name': app_name, 'start_time': datetime.datetime.now(), 'tags': ''}
        self.last_app_name = app_name

    def handle_activity_change(self, app_name_with_idle):
        if self.is_paused:
            return
        clean_app_name = get_clean_app_name(app_name_with_idle)
        if self.last_app_name == "Idle" and clean_app_name != "Idle":
            idle_end_time = datetime.datetime.now()
            idle_duration = (idle_end_time - self.current_activity['start_time']).total_seconds()
            if idle_duration > 60:
                self.current_activity['end_time'] = idle_end_time
                self.current_activity['duration_seconds'] = idle_duration
                self.handle_return_from_idle(self.current_activity, clean_app_name)
            else:
                self.start_new_activity(clean_app_name)
            return
        if clean_app_name != self.last_app_name:
            current_time = datetime.datetime.now()
            if self.current_activity and self.last_app_name != "Idle":
                duration = (current_time - self.current_activity['start_time']).total_seconds()
                if duration > self.config['check_interval_seconds']:
                    self.current_activity.update({'end_time': current_time, 'duration_seconds': duration})
                    append_activity(self.current_activity)
                    self.update_all_ui()
            self.start_new_activity(clean_app_name)

    def toggle_compact_mode(self):
        if self.isVisible():
            self.hide()
            self.compact_widget.update_display(self.current_activity)
            self.compact_widget.show()
        else:
            self.compact_widget.hide()
            self.show()

    def _setup_background(self):
        self.background_widget = QWidget(self)
        self.background_widget.setObjectName("backgroundWidget")
        self.blur_background_label = QLabel(self.background_widget)
        blur_effect = QGraphicsBlurEffect()
        blur_effect.setBlurRadius(20)
        self.blur_background_label.setGraphicsEffect(blur_effect)

    def _setup_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color: transparent;")
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self._create_collapsible_menu()
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 10, 15, 15)
        self.main_layout.addWidget(content_widget)
        self._create_header(content_layout)
        self._create_pages(content_layout)

    def _create_header(self, parent_layout):
        header_layout = QHBoxLayout()
        self.menu_toggle_button = QPushButton("☰")
        self.menu_toggle_button.setObjectName("menuButton")
        self.menu_toggle_button.setFixedSize(40, 40)
        self.menu_toggle_button.installEventFilter(self)
        self.nav_pane.installEventFilter(self)
        header_layout.addWidget(self.menu_toggle_button, alignment=Qt.AlignLeft)
        header_layout.addStretch(1)
        title_label = QLabel("Productivity Tracker")
        title_label.setObjectName("headerTitle")
        header_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        header_layout.addStretch(1)
        self.compact_mode_button = QPushButton("↘")
        self.compact_mode_button.setObjectName("headerButton")
        self.compact_mode_button.setFixedSize(40, 40)
        self.compact_mode_button.setToolTip("Switch to Compact Mode")
        self.compact_mode_button.clicked.connect(self.toggle_compact_mode)
        header_layout.addWidget(self.compact_mode_button, alignment=Qt.AlignRight)
        parent_layout.addLayout(header_layout)

    def resizeEvent(self, event):
        self.background_widget.setGeometry(0, 0, self.width(), self.height())
        self.blur_background_label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def eventFilter(self, watched, event):
        if watched == self.menu_toggle_button and event.type() == QEvent.Enter: self.open_menu()
        if watched == self.nav_pane and event.type() == QEvent.Leave: self.close_menu()
        return super().eventFilter(watched, event)

    def open_menu(self):
        if self.nav_pane.width() == 0:
            self.menu_animation.setStartValue(0)
            self.menu_animation.setEndValue(220)
            self.menu_animation.start()

    def close_menu(self):
        if self.nav_pane.width() > 0:
            self.menu_animation.setStartValue(self.nav_pane.width())
            self.menu_animation.setEndValue(0)
            self.menu_animation.start()
            
    def toggle_theme(self):
        self.config['is_dark_mode'] = not self.config['is_dark_mode']
        save_config(self.config)
        self.apply_theme()

    def apply_theme(self):
        is_dark = self.config['is_dark_mode']
        gradient = "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1D2B64, stop:1 #F8CDDA)" if is_dark else "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #8EC5FC, stop:1 #E0C3FC)"
        self.blur_background_label.setStyleSheet(f"background-color: {gradient};")
        self.setStyleSheet(get_stylesheet(is_dark))
        self.settings_page.update_theme_button_text(is_dark)
        self.update_all_ui()

    def init_and_start_tracker(self):
        self.window_detector = WindowDetector(self.config['check_interval_seconds'], self.config['idle_threshold_minutes'])
        self.window_detector.activity_changed.connect(self.handle_activity_change)
        self.window_detector.start()

    def update_live_ui(self):
        if self.is_paused: return
        if self.isVisible(): self.dashboard_page.update_live_ui(self.current_activity)
        if self.compact_widget.isVisible(): self.compact_widget.update_display(self.current_activity)

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        status = "Paused" if self.is_paused else "Resumed"
        print(f"Tracking {status}")

    def save_settings_handler(self):
        old_interval = self.config['check_interval_seconds']
        old_idle_threshold = self.config['idle_threshold_minutes']
        self.config['check_interval_seconds'] = self.settings_page.interval_spinbox.value()
        self.config['idle_threshold_minutes'] = self.settings_page.idle_spinbox.value()
        self.config['productivity_apps'] = [app.strip() for app in self.settings_page.apps_input.text().split(',') if app.strip()]
        save_config(self.config)
        if old_interval != self.config['check_interval_seconds'] or old_idle_threshold != self.config['idle_threshold_minutes']:
            self.window_detector.stop()
            self.init_and_start_tracker()
        self.update_all_ui()
        QMessageBox.information(self, "Settings Saved", "Your settings have been updated.")

    def export_data(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv)")
        if path:
            try:
                df = load_activities()
                if df.empty:
                    QMessageBox.warning(self, "Export Failed", "No data to export.")
                    return
                df.to_csv(path, index=False)
                QMessageBox.information(self, "Export Complete", f"Data exported to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"An error occurred: {e}")

    def clear_data_prompt(self):
        reply = QMessageBox.question(self, 'Confirm Deletion', "Delete ALL activity data?\nThis cannot be undone.", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            from data.data_handler import ACTIVITIES_FILE
            pd.DataFrame(columns=['app_name', 'start_time', 'end_time', 'duration_seconds', 'tags']).to_csv(ACTIVITIES_FILE, index=False)
            self.update_all_ui()
            QMessageBox.information(self, "Data Cleared", "All activity data has been deleted.")

    def on_app_exit(self):
        if self.current_activity:
            end_time = datetime.datetime.now()
            duration = (end_time - self.current_activity['start_time']).total_seconds()
            if duration > 1 and not self.is_paused:
                self.current_activity.update({'end_time': end_time, 'duration_seconds': duration})
                append_activity(self.current_activity)
        self.window_detector.stop()
        print("Application exiting. Final activity saved.")