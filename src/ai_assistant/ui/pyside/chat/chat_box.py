from PySide6.QtWidgets import (QLabel, QLineEdit, QScrollArea, QWidget, 
                             QVBoxLayout, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QThread, QTimer

from ai_assistant.ui.pyside.chat.chat_bubble import ChatBubbleContainer

class LoadingIndicator(QFrame):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)
        
        self.label = QLabel("thinking...")
        self.label.setStyleSheet("color: #777; font-style: italic; font-size: 11px;")
        layout.addWidget(self.label)
        
        self.setStyleSheet("""
            QFrame {
                background: #f0f0f0;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        self.setFixedWidth(150)
        self.hide()

class AskWorker(QThread):
    finished = Signal(str)

    def __init__(self, provider_func, messages):
        super().__init__()
        self.provider_func = provider_func
        self.messages = messages

    def run(self):
        response = self.provider_func(self.messages)
        self.finished.emit(response)

class ChatBox(QWidget):
    dismissed = Signal(str)

    def __init__(self, session_id, assistant):
        super().__init__()
        self.session_id = session_id
        self.assistant = assistant 
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(320)
        self.setMinimumHeight(400)

        self.idle_timer = QTimer(singleShot=True)
        self.idle_timer.timeout.connect(lambda: self.dismissed.emit(session_id))

        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.container = QWidget()
        self.container.setAttribute(Qt.WA_TranslucentBackground)
        self.chat_layout = QVBoxLayout(self.container)
        self.chat_layout.setContentsMargins(5, 5, 5, 5)
        self.chat_layout.setSpacing(10)
        
        self.chat_layout.addStretch() 
        
        self.typing_indicator = LoadingIndicator()
        self.chat_layout.addWidget(self.typing_indicator)
        
        self.scroll.setWidget(self.container)
        self.main_layout.addWidget(self.scroll)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask me anything...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                border-radius: 18px; 
                padding: 10px 15px; 
                background: white; 
                border: 1px solid #dcdcdc;
                color: #222;
                font-size: 13px;
            }
        """)
        self.input_field.returnPressed.connect(self.on_text_entered)
        self.main_layout.addWidget(self.input_field)

    def on_text_entered(self):
        text = self.input_field.text().strip()
        if not text:
            return
            
        self.input_field.clear()
        self.input_field.setEnabled(False)
        
        self.add_message(text, is_user=True)
        self.show_typing(True)
        self.process_chat(text)

    def process_chat(self, text):
        self.worker = AskWorker(self.assistant.ask, [text])
        self.worker.finished.connect(self.handle_assistant_response)
        self.worker.start()

    def handle_assistant_response(self, response):
        self.show_typing(False)
        self.add_message(response, is_user=False)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()

    def show_typing(self, visible: bool):
        if visible:
            self.typing_indicator.show()
        else:
            self.typing_indicator.hide()
        self.scroll_to_bottom()

    def add_message(self, text, is_user=True):
        
        msg = ChatBubbleContainer(text, is_user)
        
        idx = self.chat_layout.count() - 2
        self.chat_layout.insertWidget(max(0, idx), msg)
        
        QTimer.singleShot(50, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        bar = self.scroll.verticalScrollBar()
        bar.setValue(bar.maximum())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.dismissed.emit(self.session_id)
            event.accept()
        else:
            super().keyPressEvent(event)


    def leaveEvent(self, event) -> None:
        self.idle_timer.start(4000)


    def enterEvent(self, event) -> None:
        self.idle_timer.stop()


    def moveEvent(self, event):
        print(f"ChatHead moved to: {event.pos().x()}, {event.pos().y()}")
        super().moveEvent(event)
