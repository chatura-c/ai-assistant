
import sys
from dataclasses import dataclass
from abc import ABC, abstractmethod
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QLineEdit, QTextEdit, 
                             QPushButton, QLabel, QTabWidget, QFormLayout, 
                             QMessageBox, QStackedWidget)
from PySide6.QtCore import Qt


class ProviderManager(QWidget):
    def __init__(self, uow):
        super().__init__()
        self.providers = [] # List of Provider objects
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # Sidebar
        list_nav = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self.load_provider)
        
        add_btn = QPushButton("+ New Provider")
        add_btn.clicked.connect(self.add_new)
        
        list_nav.addWidget(self.list_widget)
        list_nav.addWidget(add_btn)

        # Form
        self.form = QWidget()
        form_layout = QFormLayout(self.form)
        
        self.id_input = QLineEdit()
        self.url_input = QLineEdit()
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.Password)
        self.model_input = QLineEdit()
        
        save_btn = QPushButton("Save Provider")
        save_btn.clicked.connect(self.save_data)

        form_layout.addRow("Provider ID:", self.id_input)
        form_layout.addRow("Base URL:", self.url_input)
        form_layout.addRow("API Key:", self.key_input)
        form_layout.addRow("Model Name:", self.model_input)
        form_layout.addRow(save_btn)

        layout.addLayout(list_nav, 1)
        layout.addWidget(self.form, 2)

    def add_new(self):
        # Default empty state
        self.id_input.clear()
        self.url_input.setText("https://api.openai.com/v1")
        self.list_widget.addItem("New Provider")

    def load_provider(self, row):
        # Implementation to map self.providers[row] to inputs
        pass

    def save_data(self):
        # Logic to instantiate specific Provider subclass based on ID or Type
        QMessageBox.information(self, "Saved", "Provider configuration updated.")

