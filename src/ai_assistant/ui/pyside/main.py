import sys
from PySide6.QtWidgets import (QApplication, QWidget, QMessageBox, QTextBrowser, QLineEdit, 
                             QVBoxLayout, QHBoxLayout, QScrollArea, QPushButton, QLabel)
from PySide6.QtGui import QPainter, QPixmap, QClipboard
from PySide6.QtCore import Qt, QTimer, QRect, QPoint, Signal, QObject, Slot

# --- STYLES ---
bubble_base_style = """
QTextBrowser {
    border-radius: 15px;
    padding: 10px;
    background-color: %s;
    border: 1.5px solid %s;
    color: %s;
}
"""

assistant_style = bubble_base_style % ("#FFFFAA", "#888888", "black")

user_style = bubble_base_style % ("#E1F5FE", "#03A9F4", "#333")

scrollbar_style = """
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: rgba(100, 100, 100, 80);
    min-height: 20px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(100, 100, 100, 150);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
copy_button_style = """
QPushButton {
    background-color: rgba(0, 0, 0, 40);
    border: none;
    border-radius: 10px;
    color: white;
    font-size: 9px;
}
QPushButton:hover {
    background-color: #03A9F4;
}
"""

context_bar_style = """
#ContextBar {
    background-color: rgba(255, 255, 255, 180);
    border-top: 1px solid #ddd;
    border-radius: 10px 10px 0px 0px;
}
#ContextLabel {
    color: #eee;
    font-size: 11px;
    padding: 5px;
}
"""

context_btn_style = """
QPushButton {
    background: rgba(0, 0, 0, 20);
    border: none;
    border-radius: 4px;
    color: #555;
    font-size: 10px;
    padding: 2px 5px;
}
QPushButton:hover {
    background: rgba(0, 0, 0, 40);
}
"""

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
    def __init__(self, text, is_user=False):
        super().__init__()
        self.text_content = text
        layout = QHBoxLayout(self)
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

        if is_user:
            layout.addStretch()
            layout.addWidget(self.copy_btn, alignment=Qt.AlignBottom)
            layout.addWidget(self.bubble)
        else:
            layout.addWidget(self.bubble)
            layout.addWidget(self.copy_btn, alignment=Qt.AlignBottom)
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


# --- MAIN ASSISTANT CLASS ---

class DesktopAssistant(QWidget):
    context_signal = Signal(str)
    
    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant
        
        self.context_text = None
        self.context_signal.connect(self.add_context)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(320)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 10, 0, 10)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(300) 
        self.scroll.setStyleSheet("background: transparent; border: none;")

        # self.scroll.setStyleSheet(f"background: transparent; border: none; {scrollbar_style}")
        
        self.container = QWidget()
        self.container.setAttribute(Qt.WA_TranslucentBackground)
        self.chat_layout = QVBoxLayout(self.container)
        self.chat_layout.setContentsMargins(10, 5, 10, 5)
        self.chat_layout.setSpacing(15)
        self.chat_layout.addStretch() 
        
        self.scroll.setWidget(self.container)
        self.main_layout.addWidget(self.scroll)

        # Assuming CharacterSprite class is defined as before
        # self.character = CharacterSprite(...) 
        self.context_bar = ContextBar(on_remove_callback=self.clear_current_context)
        self.context_bar.remove_btn.clicked.connect(self.clear_current_context)
        self.context_bar.view_btn.clicked.connect(self.show_full_context)
        self.main_layout.addWidget(self.context_bar)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Message...")
        self.input_field.setFixedWidth(260)
        self.input_field.setStyleSheet("border-radius: 15px; padding: 10px; background: white; border: 1px solid #888;")
        self.input_field.returnPressed.connect(self.process_chat)
        self.main_layout.addWidget(self.input_field, alignment=Qt.AlignCenter)
        
        self._drag_pos = QPoint()

    def clear_current_context(self):
        self.context_bar.clear_context()

    def show_full_context(self):
        QMessageBox.information(self, "Full Context", self.context_bar.full_text)

    def add_message(self, text, is_user=False):
        # Now we add the CONTAINER instead of just the bubble
        container = ChatBubbleContainer(text, is_user)
        count = self.chat_layout.count()
        self.chat_layout.insertWidget(count - 1, container)
        QTimer.singleShot(50, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        bar = self.scroll.verticalScrollBar()
        bar.setValue(bar.maximum())

    def process_chat(self):
        messages = [] 
        text = self.input_field.text()
        if text and text.strip() != "":
            messages.append(text)
            self.add_message(text, is_user=True)
            self.input_field.clear()

        if self.context_text and self.context_text.strip() != "" :
            messages.append(self.context_text)
            self.add_message(self.context_text, is_user=True)

        if len(messages) > 0:
            response = self.assistant.ask(messages)
            QTimer.singleShot(800, lambda: self.add_message(response, is_user=False))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    @Slot(str)
    def add_context(self, text):
        self.context_text = text
        self.context_bar.set_context(text)
        self.process_chat()
    
class UI:
    def __init__(self, assistant, app_name):
        app = QApplication(sys.argv)
        app.setDesktopFileName(app_name)
        window = DesktopAssistant(assistant)
        
        self.assistant = assistant
        self.window = window
        self.app = app

    def show(self):
        self.window.show()

    def exit(self):
        sys.exit(self.app.exec())

    def on_context_changed(self, focus_frame):
        self.window.context_signal.emit(focus_frame.text)

