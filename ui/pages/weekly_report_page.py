import datetime
import pandas as pd
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton, QDateEdit, QScrollArea, QFileDialog
from PyQt5.QtCore import QDate, Qt
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Import the new PDF exporter function
from utils.pdf_exporter import generate_weekly_report_pdf

class WeeklyReportPage(QWidget):
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

        # --- Header with Export Button ---
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("<h1>Weekly Productivity Report</h1>"))
        header_layout.addStretch()
        
        self.export_pdf_button = QPushButton("Export to PDF")
        self.export_pdf_button.clicked.connect(self.export_to_pdf)
        header_layout.addWidget(self.export_pdf_button)
        layout.addLayout(header_layout)
        
        # --- Date Filter ---
        filter_group = QGroupBox("Select Week")
        filter_layout = QHBoxLayout()
        self.week_start_edit = QDateEdit(QDate.currentDate().addDays(-QDate.currentDate().dayOfWeek() + 1))
        self.week_start_edit.setCalendarPopup(True)
        self.week_start_edit.setDisplayFormat("yyyy-MM-dd")
        self.week_start_edit.dateChanged.connect(self.update_report)

        filter_layout.addWidget(QLabel("Show report for the week starting:"))
        filter_layout.addWidget(self.week_start_edit)
        filter_layout.addStretch()
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # --- Bar Chart Report ---
        report_group = QGroupBox("Productive Time per Day")
        report_layout = QVBoxLayout()
        
        self.canvas = FigureCanvas(Figure(figsize=(10, 6)))
        self.ax = self.canvas.figure.subplots()
        
        report_layout.addWidget(self.canvas)
        report_group.setLayout(report_layout)
        layout.addWidget(report_group, 1)
        
        scroll_area.setWidget(content_card)
        page_layout.addWidget(scroll_area)
    
    def export_to_pdf(self):
        """Opens a save dialog and triggers the PDF generation."""
        from data.data_handler import load_activities
        
        start_date = self.week_start_edit.date().toPyDate()
        default_filename = f"Productivity_Report_{start_date.strftime('%Y_%m_%d')}.pdf"
        
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", default_filename, "PDF Files (*.pdf)")
        
        if path:
            activities_df = load_activities()
            end_date = start_date + datetime.timedelta(days=6)
            week_df = activities_df[
                (activities_df['start_time'].dt.date >= start_date) & 
                (activities_df['start_time'].dt.date <= end_date)
            ].copy()
            
            try:
                generate_weekly_report_pdf(path, start_date, week_df, self.main_window.config)
                # Optionally, open the PDF after saving or show a success message
            except Exception as e:
                # Handle potential errors during PDF generation
                print(f"Error generating PDF: {e}")

    def update_report(self):
        """This method will be called to generate the weekly chart."""
        from data.data_handler import load_activities
        activities_df = load_activities()
        config = self.main_window.config
        
        self.ax.clear()
        is_dark = config.get('is_dark_mode', False)
        text_color = '#E0E0E0' if is_dark else '#333'
        
        self.canvas.figure.patch.set_facecolor('none')
        self.ax.set_facecolor('none')
        self.ax.tick_params(axis='x', colors=text_color, rotation=45)
        self.ax.tick_params(axis='y', colors=text_color)
        self.ax.spines['bottom'].set_color(text_color)
        self.ax.spines['left'].set_color(text_color)
        self.ax.spines['top'].set_color('none')
        self.ax.spines['right'].set_color('none')

        start_date = self.week_start_edit.date().toPyDate()
        end_date = start_date + datetime.timedelta(days=6)
        
        week_df = activities_df[
            (activities_df['start_time'].dt.date >= start_date) & 
            (activities_df['start_time'].dt.date <= end_date)
        ].copy()

        productive_apps = config.get('productivity_apps', [])
        productive_mask = week_df['app_name'].str.contains('|'.join(productive_apps), case=False, na=False)
        productive_df = week_df[productive_mask]

        if not productive_df.empty:
            daily_productive_time = productive_df.groupby(productive_df['start_time'].dt.date)['duration_seconds'].sum() / 3600
            date_range = pd.to_datetime(pd.date_range(start=start_date, end=end_date)).date
            daily_productive_time = daily_productive_time.reindex(date_range, fill_value=0)
            days_of_week = [d.strftime('%A') for d in daily_productive_time.index]
            
            self.ax.bar(days_of_week, daily_productive_time.values, color='#4CAF50')
            self.ax.set_ylabel("Productive Time (Hours)", color=text_color)
            self.ax.set_title(f"Week of {start_date.strftime('%Y-%m-%d')}", color=text_color)
        else:
            self.ax.text(0.5, 0.5, f"No Productive Data for Selected Week", ha='center', va='center', color=text_color, fontsize=12)

        self.canvas.figure.tight_layout()
        self.canvas.draw()