import datetime
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QDateTimeEdit, QDialogButtonBox
from PyQt5.QtCore import QDateTime

class AddActivityDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Manual Activity")
        self.setMinimumWidth(400)
        
        # --- Data Storage ---
        self.activity_data = None
        
        # --- UI Elements ---
        layout = QVBoxLayout(self)
        
        # App Name
        layout.addWidget(QLabel("Activity/App Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        
        # Start and End Time
        time_layout = QHBoxLayout()
        start_group = QVBoxLayout()
        start_group.addWidget(QLabel("Start Time:"))
        self.start_time_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.start_time_input.setCalendarPopup(True)
        self.start_time_input.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        start_group.addWidget(self.start_time_input)
        time_layout.addLayout(start_group)
        
        end_group = QVBoxLayout()
        end_group.addWidget(QLabel("End Time:"))
        self.end_time_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.end_time_input.setCalendarPopup(True)
        self.end_time_input.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        end_group.addWidget(self.end_time_input)
        time_layout.addLayout(end_group)
        layout.addLayout(time_layout)
        
        # Tags
        layout.addWidget(QLabel("Tags (comma-separated):"))
        self.tags_input = QLineEdit()
        layout.addWidget(self.tags_input)
        
        # --- Dialog Buttons ---
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept(self):
        """Called when the Save button is clicked."""
        start_time = self.start_time_input.dateTime().toPyDateTime()
        end_time = self.end_time_input.dateTime().toPyDateTime()
        
        # Basic validation
        if not self.name_input.text():
            # In a real app, you would show a QMessageBox here
            print("Error: Activity name cannot be empty.")
            return
        if start_time >= end_time:
            print("Error: Start time must be before end time.")
            return
            
        duration = (end_time - start_time).total_seconds()
        
        self.activity_data = {
            'app_name': self.name_input.text(),
            'start_time': start_time,
            'end_time': end_time,
            'duration_seconds': duration,
            'tags': self.tags_input.text()
        }
        
        super().accept()

    def get_activity_data(self):
        """Returns the collected data if the dialog was accepted."""
        return self.activity_data