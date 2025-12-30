
import sys
from dataclasses import dataclass
from abc import ABC, abstractmethod
from uuid import uuid4
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QLineEdit, QTextEdit, 
                             QPushButton, QLabel, QTabWidget, QFormLayout, 
                             QMessageBox, QStackedWidget)
from PySide6.QtCore import Qt

from ai_assistant.core.models import Provider, SafeKey
from ai_assistant.core.uow import AbstractUnitOfWork


class ProviderManager(QWidget):
    def __init__(self, uow: AbstractUnitOfWork):
        super().__init__()
        self.uow = uow
        self.providers = [] 
        self.init_ui()

        self.load()

    def init_ui(self):
        layout = QHBoxLayout(self)
        
        list_nav = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self.load_provider)
        
        add_btn = QPushButton("+ New Provider")
        add_btn.clicked.connect(self.add_new)
        
        list_nav.addWidget(self.list_widget)
        list_nav.addWidget(add_btn)

        self.form = QWidget()
        form_layout = QFormLayout(self.form)
        
        self.name_input = QLineEdit()
        self.url_input = QLineEdit()
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.Password)
        self.model_input = QLineEdit()
        
        save_btn = QPushButton("Save Provider")
        save_btn.clicked.connect(self.save_data)

        form_layout.addRow("Provider ID:", self.name_input)
        form_layout.addRow("Base URL:", self.url_input)
        form_layout.addRow("API Key:", self.key_input)
        form_layout.addRow("Model Name:", self.model_input)
        form_layout.addRow(save_btn)

        layout.addLayout(list_nav, 1)
        layout.addWidget(self.form, 2)


    def add_new(self):
        name = f"New Provider {self.list_widget.count() + 1}"
        new_provider = Provider(str(uuid4()), name, "http://localhost:11434/v1", "", "")
        self.uow.providers.create(new_provider.id, new_provider)

        self.providers.append(new_provider)
        self.list_widget.addItem(new_provider.name)
        self.list_widget.setCurrentRow(len(self.providers) - 1)


    def load_provider(self, index):
        if 0 <= index < len(self.providers):
            p = self.providers[index]
            self.name_input.setText(p.name)
            self.url_input.setText(p.url)
            self.key_input.setText("")
            self.model_input.setText(p.model)


    def load(self):
        self.providers = self.uow.providers.get_all()
        self.list_widget.clear()
        self.list_widget.addItems([p.name for p in self.providers])

    def save_data(self):
        idx = self.list_widget.currentRow()
        if idx >= 0:
            selected_provider = self.providers[idx]
            new_provider = Provider(
                selected_provider.id,
                self.name_input.text(),
                self.url_input.text(),
                "",
                self.model_input.text()
            )
            self.uow.providers.create(selected_provider.id, new_provider)
            
            if len(self.key_input.text()) > 0:
                self.uow.secrets.create(selected_provider.id, SafeKey(selected_provider.id, self.key_input.text()))

            self.load()
        QMessageBox.information(self, "Saved", "Provider configuration updated.")

