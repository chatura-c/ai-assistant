import sys
from dataclasses import dataclass
from abc import ABC, abstractmethod
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QLineEdit, QTextEdit, 
                             QPushButton, QLabel, QTabWidget, QFormLayout, 
                             QMessageBox, QStackedWidget)
from PySide6.QtCore import Qt



class ProfileManager(QWidget):
    def __init__(self, uow):
        super().__init__()
        self.profiles = []
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # Left side: List and Add/Delete buttons
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
        
        # Right side: Form
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
        new_p = Profile(name, "", "")
        self.profiles.append(new_p)
        self.list_widget.addItem(new_p.name)
        self.list_widget.setCurrentRow(len(self.profiles) - 1)

    def load_profile(self, index):
        if 0 <= index < len(self.profiles):
            p = self.profiles[index]
            self.name_input.setText(p.name)
            self.prompt_input.setPlainText(p.system_prompt)
            self.pic_input.setText(p.picture)

    def save_profile(self):
        idx = self.list_widget.currentRow()
        if idx >= 0:
            self.profiles[idx].name = self.name_input.text()
            self.profiles[idx].system_prompt = self.prompt_input.toPlainText()
            self.profiles[idx].picture = self.pic_input.text()
            self.list_widget.currentItem().setText(self.name_input.text())
            QMessageBox.information(self, "Success", "Profile Saved!")

    def delete_selected(self):
        idx = self.list_widget.currentRow()
        if idx >= 0:
            self.profiles.pop(idx)
            self.list_widget.takeItem(idx)


