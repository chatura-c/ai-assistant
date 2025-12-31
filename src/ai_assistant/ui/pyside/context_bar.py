
from PySide6.QtCore import Signal
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel)

from ai_assistant.ui.pyside.styles import context_bar_style, context_btn_style

class ContextBar(QWidget):
    context_dismissed = Signal(str)
    context_clicked = Signal(str)

    def __init__(self, text:str):
        super().__init__()
        self.setObjectName("ContextBar")
        self.setStyleSheet(context_bar_style)
        self.full_text = text

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 2, 10, 2)

        # Preview Text (Max 2 lines)
        self.label = QLabel()
        self.label.setObjectName("ContextLabel")
        self.label.setWordWrap(True)
        self.label.setMaximumHeight(35) # Limits to roughly 2 lines
        self.label.setText(text)
        layout.addWidget(self.label, stretch=1)

        # Buttons Container (Hidden by default)
        self.btn_container = QWidget()
        btn_layout = QHBoxLayout(self.btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        self.btn_container.show()
        
        self.remove_btn = QPushButton("✕")
        self.remove_btn.setStyleSheet(context_btn_style)
        self.remove_btn.clicked.connect(self.on_context_text_dismissed)
        btn_layout.addWidget(self.remove_btn)

        layout.addWidget(self.btn_container)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.context_clicked.emit(self.full_text)

    def on_context_text_dismissed(self):
        self.context_dismissed.emit(self.full_text)

    def enterEvent(self, event):
        super().enterEvent(event)

    def leaveEvent(self, event):
        super().leaveEvent(event)

