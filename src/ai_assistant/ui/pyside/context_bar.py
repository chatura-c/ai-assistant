
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel)


class ContextBar(QWidget):
    def __init__(self, on_remove_callback):
        super().__init__()
        self.setObjectName("ContextBar")
        self.setStyleSheet(context_bar_style)
        self.full_text = ""
        self.on_remove = on_remove_callback

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 2, 10, 2)

        # Preview Text (Max 2 lines)
        self.label = QLabel()
        self.label.setObjectName("ContextLabel")
        self.label.setWordWrap(True)
        self.label.setMaximumHeight(35) # Limits to roughly 2 lines
        layout.addWidget(self.label, stretch=1)

        # Buttons Container (Hidden by default)
        self.btn_container = QWidget()
        btn_layout = QHBoxLayout(self.btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        self.view_btn = QPushButton("View Full")
        self.remove_btn = QPushButton("✕")
        
        for btn in [self.view_btn, self.remove_btn]:
            btn.setStyleSheet(context_btn_style)
            btn_layout.addWidget(btn)

        layout.addWidget(self.btn_container)
        self.btn_container.hide()
        self.hide() # Start hidden

    def set_context(self, text):
        self.full_text = text
        self.label.setText(f"Context: {text}")
        self.show()

    def clear_context(self):
        self.full_text = ""
        self.hide()

    def enterEvent(self, event):
        self.btn_container.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.btn_container.hide()
        super().leaveEvent(event)

