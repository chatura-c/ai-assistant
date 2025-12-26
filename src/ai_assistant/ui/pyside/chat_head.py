import sys
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class ChatHead(QLabel):
    def __init__(self, icon_path, parent=None):
        super().__init__(parent)
        self.setObjectName("chat_head")
        self.setFixedSize(60, 60)
        self.setAlignment(Qt.AlignCenter)
        
        # Set the Icon
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled_pixmap)
        
        # Set the Styling
        self.setStyleSheet("""
            QLabel#chat_head {
                color: white;
                font-size: 30px;
                border-radius: 30px;
                border: 2px solid white;
                background-color: transparent; 
            }
        """)

