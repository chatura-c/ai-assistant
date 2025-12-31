from PySide6.QtWidgets import (QWidget, QLineEdit, QPushButton, QLabel, QTabWidget, QFormLayout, 
                             QMessageBox, QStackedWidget)
from PySide6.QtCore import Qt


class AppSettings(QWidget):
    def __init__(self, uow):
        super().__init__()
        layout = QFormLayout(self)
        layout.addRow(QLabel("<h2>App Preferences</h2>"))
        layout.addRow("Theme:", QLineEdit("Dark"))
        layout.addRow("Default Timeout:", QLineEdit("30s"))
        layout.addRow(QPushButton("Save Preferences"))
