import datetime
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QScrollArea, QComboBox
from PyQt5.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class DashboardPage(QWidget):
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
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # --- Live Status ---
        status_group = QGroupBox("Live Status")
        status_layout = QHBoxLayout()
        self.current_app_label = QLabel("<b>Current App:</b> N/A")
        self.current_duration_label = QLabel("<b>Duration:</b> 00:00:00")
        status_layout.addWidget(self.current_app_label)
        status_layout.addStretch()
        status_layout.addWidget(self.current_duration_label)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # --- Tag Filter ---
        filter_group = QGroupBox("Filter Report by Tag")
        filter_layout = QHBoxLayout()
        self.tag_filter_combo = QComboBox()
        self.tag_filter_combo.currentIndexChanged.connect(self.main_window.update_all_ui) # Refresh UI when selection changes
        filter_layout.addWidget(QLabel("Show activity for:"))
        filter_layout.addWidget(self.tag_filter_combo)
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # --- Key Metrics ---
        metrics_group = QGroupBox("Key Metrics for Selection")
        metrics_layout = QHBoxLayout()
        self.productive_time_label = QLabel("<b>Productive:</b><br>0h 0m 0s")
        self.unproductive_time_label = QLabel("<b>Unproductive:</b><br>0h 0m 0s")
        self.focus_score_label = QLabel("<b>Focus Score:</b><br>0%")
        metrics_layout.addWidget(self.productive_time_label, alignment=Qt.AlignCenter)
        metrics_layout.addWidget(self.unproductive_time_label, alignment=Qt.AlignCenter)
        metrics_layout.addWidget(self.focus_score_label, alignment=Qt.AlignCenter)
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)

        # --- Bar Chart Report ---
        report_group = QGroupBox("Activity Breakdown for Selection")
        report_layout = QVBoxLayout()
        self.chart_scroll_area = QScrollArea()
        self.chart_scroll_area.setWidgetResizable(True)
        self.canvas = FigureCanvas(Figure(figsize=(5, 8)))
        self.ax = self.canvas.figure.subplots()
        self.chart_scroll_area.setWidget(self.canvas)
        report_layout.addWidget(self.chart_scroll_area)
        report_group.setLayout(report_layout)
        layout.addWidget(report_group, 1)
        
        scroll_area.setWidget(content_card)
        page_layout.addWidget(scroll_area)
        
    def update_live_ui(self, current_activity):
        if current_activity:
            self.current_app_label.setText(f"<b>Current App:</b> {current_activity['app_name']}")
            duration = (datetime.datetime.now() - current_activity['start_time']).total_seconds()
            self.current_duration_label.setText(f"<b>Duration:</b> {str(datetime.timedelta(seconds=int(duration)))}")

    def update_tag_filter(self, activities_df):
        """Populates the tag filter dropdown with unique tags from the data."""
        self.tag_filter_combo.blockSignals(True) # Prevent signal firing while we repopulate
        
        current_selection = self.tag_filter_combo.currentText()
        self.tag_filter_combo.clear()
        
        unique_tags = set()
        for tags_string in activities_df['tags'].dropna():
            for tag in tags_string.split(','):
                if tag.strip():
                    unique_tags.add(tag.strip())
        
        self.tag_filter_combo.addItem("All Activities")
        self.tag_filter_combo.addItems(sorted(list(unique_tags)))
        
        # Restore previous selection if it still exists
        index = self.tag_filter_combo.findText(current_selection)
        if index != -1:
            self.tag_filter_combo.setCurrentIndex(index)

        self.tag_filter_combo.blockSignals(False)

    def generate_activity_report(self, activities_df, config):
        self.update_tag_filter(activities_df)
        self.ax.clear()
        is_dark = config['is_dark_mode']
        text_color = '#E0E0E0' if is_dark else '#333'
        
        # --- Apply base styles to the chart ---
        self.canvas.figure.patch.set_facecolor('none')
        self.ax.set_facecolor('none')
        self.ax.tick_params(axis='x', colors=text_color)
        self.ax.tick_params(axis='y', colors=text_color)
        self.ax.spines['bottom'].set_color(text_color)
        self.ax.spines['left'].set_color(text_color)
        self.ax.spines['top'].set_color('none')
        self.ax.spines['right'].set_color('none')

        # --- Filter data by date and selected tag ---
        today_df = activities_df[activities_df['start_time'].dt.date == datetime.date.today()].copy()
        
        selected_tag = self.tag_filter_combo.currentText()
        if selected_tag and selected_tag != "All Activities":
            today_df = today_df[today_df['tags'].str.contains(selected_tag, na=False)]

        productive_seconds = 0
        total_seconds = 0

        if not today_df.empty and today_df['duration_seconds'].sum() > 0:
            total_time_per_app = today_df.groupby('app_name')['duration_seconds'].sum().sort_values(ascending=True)
            
            app_names = total_time_per_app.index
            durations_minutes = total_time_per_app.values / 60
            
            colors = ['#4CAF50' if any(p.lower() in app.lower() for p in config.get('productivity_apps', [])) else '#D32F2F' for app in app_names]

            self.ax.barh(app_names, durations_minutes, color=colors)
            
            total_seconds = today_df['duration_seconds'].sum()
            productive_mask = today_df['app_name'].str.contains('|'.join(config['productivity_apps']), case=False, na=False)
            productive_seconds = today_df[productive_mask]['duration_seconds'].sum()
            
            new_height = max(5, len(app_names) * 0.5)
            self.canvas.figure.set_figheight(new_height)
        else:
            self.ax.text(0.5, 0.5, f"No Data for '{selected_tag}' Today", ha='center', va='center', color=text_color, fontsize=12)

        # --- Update metric labels ---
        unproductive_seconds = total_seconds - productive_seconds
        focus_score = (productive_seconds / total_seconds * 100) if total_seconds > 0 else 0
        
        self.productive_time_label.setText(f"<b>Productive:</b><br>{str(datetime.timedelta(seconds=int(productive_seconds)))}")
        self.unproductive_time_label.setText(f"<b>Unproductive:</b><br>{str(datetime.timedelta(seconds=int(unproductive_seconds)))}")
        self.focus_score_label.setText(f"<b>Focus Score:</b><br>{focus_score:.1f}%")

        self.ax.set_xlabel("Time Spent (Minutes)", color=text_color)
        self.canvas.figure.tight_layout()
        self.canvas.draw()