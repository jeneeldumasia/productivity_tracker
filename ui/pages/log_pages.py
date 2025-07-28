import datetime
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
from PyQt5.QtCore import QDate

class LogPage(QWidget):
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

        layout.addWidget(QLabel("<h1>Activity Log</h1>"))
        
        filter_group = QGroupBox("Filter by Date")
        filter_layout = QHBoxLayout()
        self.start_date_edit = QDateEdit(QDate.currentDate().addMonths(-1))
        self.end_date_edit = QDateEdit(QDate.currentDate())
        for edit in [self.start_date_edit, self.end_date_edit]:
            edit.setCalendarPopup(True)
            edit.setDisplayFormat("yyyy-MM-dd")
        
        apply_button = QPushButton("Apply Filter")
        apply_button.clicked.connect(self.filter_activities)

        filter_layout.addWidget(QLabel("Start Date:"))
        filter_layout.addWidget(self.start_date_edit)
        filter_layout.addStretch(1)
        filter_layout.addWidget(QLabel("End Date:"))
        filter_layout.addWidget(self.end_date_edit)
        filter_layout.addStretch(1)
        filter_layout.addWidget(apply_button)
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        self.activities_table = QTableWidget()
        self.activities_table.setColumnCount(4)
        self.activities_table.setHorizontalHeaderLabels(["App", "Start Time", "End Time", "Duration"])
        self.activities_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.activities_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.activities_table.setAlternatingRowColors(True)
        layout.addWidget(self.activities_table)

        scroll_area.setWidget(content_card)
        page_layout.addWidget(scroll_area)

    def filter_activities(self):
        from data.data_handler import load_activities # local import
        activities = load_activities()
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()
        mask = (activities['start_time'].dt.date >= start_date) & (activities['start_time'].dt.date <= end_date)
        self.display_activities(activities.loc[mask])

    def display_activities(self, df):
        self.activities_table.setRowCount(0)
        df = df.sort_values(by="start_time", ascending=False)
        for _, row in df.iterrows():
            row_num = self.activities_table.rowCount()
            self.activities_table.insertRow(row_num)
            self.activities_table.setItem(row_num, 0, QTableWidgetItem(row['app_name']))
            self.activities_table.setItem(row_num, 1, QTableWidgetItem(row['start_time'].strftime('%Y-%m-%d %H:%M:%S')))
            self.activities_table.setItem(row_num, 2, QTableWidgetItem(row['end_time'].strftime('%Y-%m-%d %H:%M:%S')))
            self.activities_table.setItem(row_num, 3, QTableWidgetItem(str(datetime.timedelta(seconds=int(row['duration_seconds'])))))