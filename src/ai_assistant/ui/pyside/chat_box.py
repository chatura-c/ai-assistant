from PySide6.QtWidgets import (QLabel, QLineEdit, QScrollArea, QWidget, QMessageBox, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QThread

from ai_assistant.core.assistant import AIAssistant
from ai_assistant.ui.pyside.chat_bubble import ChatBubbleContainer


class AskWorker(QThread):
    finished = Signal(str)

    def __init__(self, provider, messages):
        super().__init__()
        self.provider = provider
        self.messages = messages

    def run(self):
        response = self.provider.ask(self.messages)
        self.finished.emit(response)


class ChatBox(QWidget):
    text_entered = Signal(str)

    def __init__(self, id, assistant:AIAssistant):
        super().__init__()
        # self.context_callbacks = context_callbacks or {}
            
        self.id = id
        self.assistant = assistant 
        self.init_ui()

    def init_ui(self):
        self.main_container_layout = QVBoxLayout(self)
        self.main_container_layout.setContentsMargins(0, 0, 0, 0)
        self.main_container_layout.setSpacing(0)

        self.chat_wrapper = QFrame()
        self.chat_wrapper_layout = QVBoxLayout(self.chat_wrapper)
        self.chat_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_wrapper_layout.setSpacing(10)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setMinimumHeight(300)
        self.scroll.setMaximumHeight(800)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        self.container = QWidget()
        self.container.setAttribute(Qt.WA_TranslucentBackground)
        self.chat_layout = QVBoxLayout(self.container)
        self.chat_layout.setContentsMargins(10, 5, 10, 5)
        self.chat_layout.setSpacing(15)
        self.chat_layout.addStretch() 
        
        self.scroll.setWidget(self.container)
        self.chat_wrapper_layout.addWidget(self.scroll)

        # try:
        #     from ai_assistant.ui.pyside.context_bar import ContextBar
        #     clear_cb = self.context_callbacks.get('clear')
        #     show_cb = self.context_callbacks.get('show')
        #
        #     self.context_bar = ContextBar(on_remove_callback=clear_cb)
        #
        #     if clear_cb:
        #         try: self.context_bar.remove_btn.clicked.connect(clear_cb)
        #         except AttributeError: pass
        #     if show_cb:
        #         try: self.context_bar.view_btn.clicked.connect(show_cb)
        #         except AttributeError: pass
        #
        #     self.chat_wrapper_layout.addWidget(self.context_bar)
        # except ImportError:
        #     pass
        #
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Message...")
        self.input_field.setFixedWidth(260)
        self.input_field.setStyleSheet("""
            QLineEdit {
                border-radius: 15px; 
                padding: 10px; 
                background: white; 
                border: 1px solid #888;
                color: #333;
            }
        """)
        
        self.input_field.returnPressed.connect(self.on_text_entered)
        
        self.main_container_layout.addWidget(self.chat_wrapper)
        self.main_container_layout.addWidget(self.input_field, alignment=Qt.AlignCenter)
    

    def process_chat(self, text):
        messages = [] 
        if text and text.strip() != "":
            messages.append(text)
            self.add_message(text, is_user=True)

        if len(messages) > 0:
            self.worker = AskWorker(self.assistant.ask, messages)
            self.worker.finished.connect(self.handle_assistant_response)
            self.worker.start()
 
    
    def handle_assistant_response(self, response):
        self.add_message(response, is_user=False)


    def on_text_entered(self):
        text = self.input_field.text()
        # self.text_entered.emit(text)
        self.add_message(text)
        self.process_chat(text)
        self.input_field.clear()


    def add_message(self, text, is_user=True):
        msg = ChatBubbleContainer(text, is_user)

        self.chat_layout.insertWidget(self.chat_layout.count() - 1, msg)
        
        self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        )

    def get_text(self):
        return self.input_field.text()

    def clear_input(self):
        self.input_field.clear()
