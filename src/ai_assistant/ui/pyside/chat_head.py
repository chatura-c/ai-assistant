import sys
from PySide6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QLabel, 
                             QVBoxLayout, QPushButton, QMenu, QFrame)
from PySide6.QtCore import Qt, Signal, QTimer, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap, QAction, QColor, QPainter

from ai_assistant.ui.pyside.chat_bubble import ChatBubbleContainer

class ChatHead(QWidget):
    clicked = Signal(str)
    settings_clicked = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(15)
        self.main_layout.setSizeConstraint(QHBoxLayout.SetFixedSize)

        self.head_container = QWidget()
        self.head_container.setFixedSize(70, 70) 

        self.chat_head_image = QLabel(self.head_container)
        self.chat_head_image.setFixedSize(60, 60)
        self.chat_head_image.move(0, 10)
        self.chat_head_image.setAlignment(Qt.AlignCenter)
        self.chat_head_image.setStyleSheet("""
            border-radius: 30px;
            border: 3px solid white;
            background-color: #222;
        """)

        self.menu_btn = QPushButton("⋮", self.head_container)
        self.menu_btn.setFixedSize(26, 26)
        self.menu_btn.move(40, 0) 
        self.menu_btn.setCursor(Qt.PointingHandCursor)
        self.menu_btn.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border-radius: 13px;
                border: 2px solid white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        self.menu_btn.clicked.connect(self.show_main_menu)

        self.main_layout.addWidget(self.head_container)

        self.heads = {}
        self.active_session = None
        self.bubble = None
        
        self.bubble_lifetime_timer = QTimer(self)
        self.bubble_lifetime_timer.setSingleShot(True)
        self.bubble_lifetime_timer.timeout.connect(self.bubble_timed_out)

    def show_main_menu(self):
        menu = QMenu(self)
        menu.setWindowFlags(menu.windowFlags() | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        menu.setAttribute(Qt.WA_TranslucentBackground)
        
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 25px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #0078fe;
            }
            QMenu::separator {
                height: 1px;
                background: #444;
                margin: 5px 0px;
            }
        """)

        chats_submenu = menu.addMenu("All Chats")
        if not self.heads:
            no_chats = chats_submenu.addAction("No active chats")
            no_chats.setEnabled(False)
        else:
            for sid in self.heads.keys():
                icon = "● " if sid == self.active_session else "  "
                action = chats_submenu.addAction(f"{icon}Session: {sid}")
                action.triggered.connect(lambda checked=False, s=sid: self.switch_chat(s))

        menu.addSeparator()
        
        settings_act = menu.addAction("Settings")
        settings_act.triggered.connect(self.open_settings)

        exit_act = menu.addAction("Exit")
        exit_act.triggered.connect(QApplication.instance().quit)

        menu.exec_(self.menu_btn.mapToGlobal(QPoint(0, self.menu_btn.height() + 5)))

    def open_settings(self):
        self.settings_clicked.emit()
 
    
    def switch_chat(self, session_id):
        self.active_session = session_id
        print(f"Switched to: {session_id}")
        self.clicked.emit(session_id)

    def add_new_chat(self, icon_path, session_id):
        self.heads[session_id] = icon_path
        self.active_session = session_id
        
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.chat_head_image.setPixmap(scaled)
        else:
            self.chat_head_image.setText(session_id[:1].upper())

    def on_message_received(self, text, is_user, session_id):
        self._update_layout_direction()
        self.active_session = session_id

        if self.bubble:
            self.bubble.animate_out()

        self.bubble = ChatBubbleContainer(text, is_user=is_user)
        self.main_layout.addWidget(self.bubble)

        self.bubble_lifetime_timer.start(5000)

    def bubble_timed_out(self):
        if self.bubble:
            self.bubble.animate_out()
            self.bubble = None

    def _update_layout_direction(self):
        screen = QApplication.primaryScreen().geometry()
        current_pos = self.geometry().center()
        
        if current_pos.x() > (screen.width() * 0.7):
            self.main_layout.setDirection(QHBoxLayout.RightToLeft)
        else:
            self.main_layout.setDirection(QHBoxLayout.LeftToRight)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.chat_head_image.geometry().contains(self.head_container.mapFromParent(event.pos())):
                if self.active_session:
                    self.clicked.emit(self.active_session)
        super().mousePressEvent(event)

