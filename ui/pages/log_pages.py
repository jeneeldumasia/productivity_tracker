import datetime
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
from PyQt5.QtCore import QDate, Qt

# We need to import the new update function from the data handler
from data.data_handler import update_activity_tags

class LogPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setStyleSheet("background: transparent;")
        # A flag to prevent the itemChanged signal from firing while we are populating the table
        self._is_populating = False
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
        # Increased column count to 5 to include Tags
        self.activities_table.setColumnCount(5)
        self.activities_table.setHorizontalHeaderLabels(["App", "Start Time", "End Time", "Duration", "Tags"])
        self.activities_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.activities_table.setAlternatingRowColors(True)
        
        # Connect the itemChanged signal to our handler
        self.activities_table.itemChanged.connect(self.handle_tag_changed)
        
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
        self._is_populating = True # Set flag to disable itemChanged signal
        self.activities_table.setRowCount(0)
        df = df.sort_values(by="start_time", ascending=False)
        
        for index, row in df.iterrows():
            row_num = self.activities_table.rowCount()
            self.activities_table.insertRow(row_num)
            
            # Store the original start time string in the first item of each row.
            # This will be our unique identifier for saving changes.
            start_time_str = row['start_time'].strftime('%Y-%m-%d %H:%M:%S.%f')
            app_item = QTableWidgetItem(row['app_name'])
            app_item.setData(Qt.UserRole, start_time_str)
            app_item.setFlags(app_item.flags() & ~Qt.ItemIsEditable) # Make non-tags columns read-only
            
            start_time_item = QTableWidgetItem(row['start_time'].strftime('%Y-%m-%d %H:%M:%S'))
            start_time_item.setFlags(start_time_item.flags() & ~Qt.ItemIsEditable)

            end_time_item = QTableWidgetItem(row['end_time'].strftime('%Y-%m-%d %H:%M:%S'))
            end_time_item.setFlags(end_time_item.flags() & ~Qt.ItemIsEditable)
            
            duration_item = QTableWidgetItem(str(datetime.timedelta(seconds=int(row['duration_seconds']))))
            duration_item.setFlags(duration_item.flags() & ~Qt.ItemIsEditable)

            tags_item = QTableWidgetItem(str(row['tags'])) # The tags column is editable by default

            self.activities_table.setItem(row_num, 0, app_item)
            self.activities_table.setItem(row_num, 1, start_time_item)
            self.activities_table.setItem(row_num, 2, end_time_item)
            self.activities_table.setItem(row_num, 3, duration_item)
            self.activities_table.setItem(row_num, 4, tags_item)
            
        self._is_populating = False # Unset flag

    def handle_tag_changed(self, item):
        # Only proceed if we are not populating the table and the changed item is in the 'Tags' column (column 4)
        if self._is_populating or item.column() != 4:
            return

        # Get the unique identifier (start_time) we stored in the first column
        row = item.row()
        start_time_item = self.activities_table.item(row, 0)
        if not start_time_item:
            return
            
        start_time_str = start_time_item.data(Qt.UserRole)
        new_tags = item.text()
        
        # Call the function in our data handler to update the CSV file
        update_activity_tags(start_time_str, new_tags)
        
        # Optional: refresh the dashboard to reflect the new tags in analytics
        self.main_window.update_all_ui()