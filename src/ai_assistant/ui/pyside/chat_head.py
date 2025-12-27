import sys
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal


class ChatHead(QLabel):
    clicked = Signal(str)
    def __init__(self, icon_path, id="chat_head"):
        super().__init__()
        self.setObjectName("chat_head")
        self.setFixedSize(60, 60)
        self.setAlignment(Qt.AlignCenter)

        self.id = id

        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled_pixmap)
        
        # Set the Styling
        self.setStyleSheet("""
            ChatHead {
                color: white;
                font-size: 30px;
                border-radius: 30px;
                border: 1px solid white;
                background-color: transparent; 
            }
        """)

    

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.id)
        super().mousePressEvent(event)
