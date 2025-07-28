import datetime
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QTextEdit, QScrollArea
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
        
        status_group = QGroupBox("Live Status")
        status_layout = QHBoxLayout()
        self.current_app_label = QLabel("<b>Current App:</b> N/A")
        self.current_duration_label = QLabel("<b>Duration:</b> 00:00:00")
        status_layout.addWidget(self.current_app_label)
        status_layout.addStretch()
        status_layout.addWidget(self.current_duration_label)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        report_group = QGroupBox("Today's Activity Report")
        report_layout = QHBoxLayout()
        self.canvas = FigureCanvas(Figure(figsize=(5, 5)))
        self.ax = self.canvas.figure.subplots()
        report_layout.addWidget(self.canvas, 2)
        
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        report_layout.addWidget(self.report_text, 1)

        report_group.setLayout(report_layout)
        layout.addWidget(report_group)
        
        scroll_area.setWidget(content_card)
        page_layout.addWidget(scroll_area)
        
    def update_live_ui(self, current_activity):
        if current_activity:
            self.current_app_label.setText(f"<b>Current App:</b> {current_activity['app_name']}")
            duration = (datetime.datetime.now() - current_activity['start_time']).total_seconds()
            self.current_duration_label.setText(f"<b>Duration:</b> {str(datetime.timedelta(seconds=int(duration)))}")

    def generate_activity_report(self, activities_df, config):
        self.ax.clear()
        is_dark = config['is_dark_mode']
        text_color = '#E0E0E0' if is_dark else '#333'
        
        self.canvas.figure.patch.set_facecolor('none')
        self.ax.set_facecolor('none')

        today_df = activities_df[activities_df['start_time'].dt.date == datetime.date.today()]

        if not today_df.empty and today_df['duration_seconds'].sum() > 0:
            total_time_per_app = today_df.groupby('app_name')['duration_seconds'].sum().sort_values(ascending=False)
            total_tracked_time = total_time_per_app.sum()

            wedges, _, autotexts = self.ax.pie(
                total_time_per_app, autopct='%1.1f%%', startangle=90,
                pctdistance=0.85, wedgeprops={'edgecolor': 'white' if is_dark else '#555', 'linewidth': 0.5}
            )
            for autotext in autotexts: autotext.set_color('white'); autotext.set_fontsize(9); autotext.set_fontweight('bold')
            self.ax.axis('equal')
            
            report_text_content, legend_labels = "", []
            for app_name, duration in total_time_per_app.items():
                is_productive = any(p.lower() in app_name.lower() for p in config['productivity_apps'])
                tag = " <font color='#4CAF50'>(Productive)</font>" if is_productive else ""
                report_text_content += f"<b>{app_name}</b>{tag}<br>{str(datetime.timedelta(seconds=int(duration)))}<br><br>"
                legend_labels.append(f"{app_name} ({ (duration/total_tracked_time)*100 :.1f}%)")
            
            leg = self.ax.legend(wedges, legend_labels, title="Applications", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            plt.setp(leg.get_texts(), color=text_color)
            plt.setp(leg.get_title(), color=text_color, fontweight='bold')
            leg.get_frame().set_edgecolor('none')
            leg.get_frame().set_facecolor('none')
            
            self.report_text.setHtml(f"<div style='color: {text_color};'>{report_text_content}</div>")
        else:
            self.ax.text(0.5, 0.5, "No Data for Today", ha='center', va='center', color=text_color, fontsize=12)
            self.report_text.setHtml(f"<div style='color: {text_color};'>No activities recorded yet for today.</div>")

        self.canvas.draw()