import sys
from uuid import uuid4
from dataclasses import dataclass
from abc import ABC, abstractmethod
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QLineEdit, QTextEdit, 
                             QPushButton, QLabel, QTabWidget, QFormLayout, 
                             QMessageBox, QStackedWidget)
from PySide6.QtCore import Qt

from ai_assistant.core.models import Profile
from ai_assistant.core.uow import AbstractUnitOfWork


class ProfileManager(QWidget):
    def __init__(self, uow:AbstractUnitOfWork):
        super().__init__()
        self.uow = uow
        self.profiles = []
        self.init_ui()

        self.load()

    def init_ui(self):
        layout = QHBoxLayout(self)
        
        list_container = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self.load_profile)
        
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Profile")
        self.del_btn = QPushButton("Delete")
        self.add_btn.clicked.connect(self.add_new)
        self.del_btn.clicked.connect(self.delete_selected)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.del_btn)
        
        list_container.addWidget(QLabel("Profiles"))
        list_container.addWidget(self.list_widget)
        list_container.addLayout(btn_layout)
        
        self.form_widget = QWidget()
        form_layout = QFormLayout(self.form_widget)
        
        self.name_input = QLineEdit()
        self.prompt_input = QTextEdit()
        self.pic_input = QLineEdit()
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.save_profile)
        
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("System Prompt:", self.prompt_input)
        form_layout.addRow("Picture Path:", self.pic_input)
        form_layout.addRow(self.save_btn)
        
        layout.addLayout(list_container, 1)
        layout.addWidget(self.form_widget, 2)

    def add_new(self):
        name = f"New Profile {self.list_widget.count() + 1}"
        new_profile = Profile(str(uuid4()), name, "", "")
        self.uow.profiles.create(new_profile.id, new_profile)

        self.profiles.append(new_profile)
        self.list_widget.addItem(new_profile.name)
        self.list_widget.setCurrentRow(len(self.profiles) - 1)

    def load(self):
        self.profiles = self.uow.profiles.get_all()
        self.list_widget.clear()
        self.list_widget.addItems([p.name for p in self.profiles])

    def load_profile(self, index):
        if 0 <= index < len(self.profiles):
            p = self.profiles[index]
            self.name_input.setText(p.name)
            self.prompt_input.setPlainText(p.system_prompt)
            self.pic_input.setText(p.picture)

    def save_profile(self):
        idx = self.list_widget.currentRow()
        if idx >= 0:
            current_profile = self.profiles[idx]
            new_profile = Profile(
                current_profile.id,
                self.name_input.text(),
                self.prompt_input.toPlainText(),
                self.pic_input.text()
            )
            self.uow.profiles.update(current_profile.id, new_profile)
            self.load()
            QMessageBox.information(self, "Success", "Profile Saved!")

    def delete_selected(self):
        idx = self.list_widget.currentRow()
        if idx >= 0:
            self.profiles.pop(idx)
            self.list_widget.takeItem(idx)


