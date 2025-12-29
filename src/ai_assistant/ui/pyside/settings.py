import sys
from dataclasses import dataclass
from abc import ABC, abstractmethod
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QLineEdit, QTextEdit, 
                             QPushButton, QLabel, QTabWidget, QFormLayout, 
                             QMessageBox, QStackedWidget)
from PySide6.QtCore import Qt

from ai_assistant.ui.pyside.settings_app import AppSettings
from ai_assistant.ui.pyside.settings_assistants import AssistantManager
from ai_assistant.ui.pyside.settings_profiles import ProfileManager
from ai_assistant.ui.pyside.settings_providers import ProviderManager




class SettingsWindow(QMainWindow):
    def __init__(self, uow):
        super().__init__()
        self.setWindowTitle("AI Profile & Provider Manager")
        self.resize(800, 500)

        self.tabs = QTabWidget()
        self.tabs.addTab(ProfileManager(uow), "Profiles")
        self.tabs.addTab(ProviderManager(uow), "Providers")
        self.tabs.addTab(AssistantManager(uow), "Assitants")
        self.tabs.addTab(AppSettings(uow), "Preferences")

        self.setCentralWidget(self.tabs)

