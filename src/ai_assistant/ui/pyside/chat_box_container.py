from PySide6.QtGui import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ai_assistant.ui.pyside.chat_box import ChatBox


class ChatBoxContainer(QWidget):
    chats = {}

    def __init__(self):
        super.__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMaximumHeight(500)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(10)
        
        self.chat_container = QHBoxLayout()
        self.main_layout.addLayout(self.chat_container)

        self.active_chats = QHBoxLayout()
        self.main_layout.addLayout(self.active_chats)


    def add_new_chat(self, session_id, assistant):
        self.chats[session_id] = ChatBox(session_id, assistant)
        self.active_chats.addWidget(QLabel("c"))

    
    def show_chat(self, session_id):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.main_layout.addWidget(self.chats[session_id])

    def close_chat(self, session_id):
        pass
