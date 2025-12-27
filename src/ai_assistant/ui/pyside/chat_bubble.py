
from PySide6.QtWidgets import (QApplication, QWidget, QTextBrowser, 
                             QVBoxLayout, QPushButton, QGraphicsOpacityEffect)
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
        self.setFixedWidth(220)
        self.adjust_height()

    def adjust_height(self):
        doc = self.document()
        doc.setTextWidth(self.viewport().width())
        height = doc.size().height() + 25 
        self.setFixedHeight(int(height))

class ChatBubbleContainer(QWidget):
    """Wraps the bubble and a copy button into one layout."""
    def __init__(self, text, is_user=False, temporary=False):
        super().__init__()
        self.text_content = text
        self.temporary = temporary

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Create the bubble
        self.bubble = MarkdownBubble(text, is_user)

        # Create copy button (optional: only show for assistant or long text)
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setFixedSize(40, 20)
        self.copy_btn.setStyleSheet(copy_button_style)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        
        self.copy_btn.hide()

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.slide_anim = QPropertyAnimation(self, b"pos")
        
        self.lifetime_timer = QTimer(self)
        self.lifetime_timer.setSingleShot(True)
        self.lifetime_timer.timeout.connect(self.animate_out)

        if is_user:
            layout.addWidget(self.copy_btn, alignment=Qt.AlignBottom)
            layout.addStretch()
            layout.addWidget(self.bubble)
        else:
            layout.addWidget(self.copy_btn, alignment=Qt.AlignBottom)
            layout.addWidget(self.bubble)
            layout.addStretch()
    
    def enterEvent(self, event):
        self.copy_btn.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.copy_btn.hide()
        super().leaveEvent(event)

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_content)
        self.copy_btn.setText("✓")
        # Change back after 2 seconds
        QTimer.singleShot(2000, lambda: self.copy_btn.setText("Copy"))

    def animate_in(self, start_pos):
        # Fade In
        self.fade_anim.setDuration(400)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # Slide Up (starts 20px below its target)
        self.slide_anim.setDuration(400)
        self.slide_anim.setStartValue(QPoint(start_pos.x()-20, start_pos.y()))
        self.slide_anim.setEndValue(start_pos)
        self.slide_anim.setEasingCurve(QEasingCurve.OutBack)
        
        self.fade_anim.start()
        self.slide_anim.start()


    def animate_out(self):
        # Fade Out
        self.fade_anim.setDuration(250)
        self.fade_anim.setStartValue(1)
        self.fade_anim.setEndValue(0)
        
        # Trigger deletion when animation ends
        self.fade_anim.finished.connect(self.deleteLater)
        self.fade_anim.start()

    def showEvent(self, event):
        super().showEvent(event)
        self.animate_in(self.pos())
        if self.temporary:
            self.lifetime_timer.start(3000)
