from PySide6.QtWidgets import (QApplication, QWidget, QTextBrowser,
                             QVBoxLayout, QPushButton, QGraphicsOpacityEffect, QSizePolicy)
from PySide6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve
from ai_assistant.ui.pyside.styles import user_style, assistant_style, copy_button_style

class MarkdownBubble(QTextBrowser):
    def __init__(self, text, is_user=False):
        super().__init__()
        self.setReadOnly(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameStyle(0)
        self.setMarkdown(text)
        self.setStyleSheet(user_style if is_user else assistant_style)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.adjust_height()

    def adjust_height(self):
        doc = self.document()
        doc.setTextWidth(self.viewport().width())
        height = doc.documentLayout().documentSize().height()
        self.setFixedHeight(int(height) + 20)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_height()

class ChatBubbleContainer(QWidget):
    def __init__(self, text, is_user=False):
        super().__init__()
        self.text_content = text

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.bubble = MarkdownBubble(text, is_user)

        self.copy_btn = QPushButton("Copy", self)
        self.copy_btn.setFixedSize(40, 20)
        self.copy_btn.setStyleSheet(copy_button_style)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        
        self.copy_btn.hide()

        if is_user:
            layout.addWidget(self.bubble, alignment=Qt.AlignRight)
        else:
            layout.addWidget(self.bubble, alignment=Qt.AlignLeft)


    def enterEvent(self, event):
        self.copy_btn.show()
        self.copy_btn.raise_()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.copy_btn.hide()
        super().leaveEvent(event)

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_content)
        self.copy_btn.setText("✓")
        QTimer.singleShot(2000, lambda: self.copy_btn.setText("Copy"))

    def animate_in(self, start_pos):
        # self.fade_anim.setDuration(400)
        # self.fade_anim.setStartValue(0)
        # self.fade_anim.setEndValue(1)
        # self.fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        #
        # self.slide_anim.setDuration(400)
        # self.slide_anim.setStartValue(QPoint(start_pos.x() - 20, start_pos.y()))
        # self.slide_anim.setEndValue(start_pos)
        # self.slide_anim.setEasingCurve(QEasingCurve.OutBack)
        #
        # self.fade_anim.start()
        # self.slide_anim.start()
        pass

    def animate_out(self):
        # self.fade_anim.setDuration(250)
        # self.fade_anim.setStartValue(1)
        # self.fade_anim.setEndValue(0)
        # self.fade_anim.finished.connect(self.deleteLater)
        # self.fade_anim.start()
        self.deleteLater()

    def showEvent(self, event):
        super().showEvent(event)
        # self.animate_in(self.pos())
