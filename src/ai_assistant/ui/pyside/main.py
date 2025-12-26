import sys
from PySide6.QtWidgets import (QWidget, QMessageBox, QLineEdit, 
                             QVBoxLayout, QHBoxLayout, QScrollArea)
from PySide6.QtCore import Qt, QTimer, QPoint, Signal, Slot
from ai_assistant.ui.pyside.chat_head import ChatHead 
from ai_assistant.ui.pyside.chat_bubble import ChatBubbleContainer

class DesktopAssistant(QWidget):
    context_signal = Signal(str)
    
    def ui_floating_chat_bubble(self):
        head = ChatHead("assets/icon.png")
        self.el_floating_head_layout = QHBoxLayout(self)

        self.el_floating_head_layout.addWidget(head, alignment=Qt.AlignCenter)
        self.el_floating_head_layout.addStretch()
    
    def on_message_received(self, text):
        if not self.is_expanded:
            for i in reversed(range(self.el_floating_head_layout.count())):
                widget = self.el_floating_head_layout.itemAt(i).widget()
                if widget and widget.objectName() != "chat_head":
                    widget.deleteLater()

            new_bubble = ChatBubbleContainer(text, is_user=False, temporary=True)
            self.el_floating_head_layout.addWidget(new_bubble)
    
    def main_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(0)

        self.icon_widget = self.chat_head()
        self.main_layout.addWidget(self.icon_widget, alignment=Qt.AlignCenter)

        # self.chat_container = QWidget()
        # self.chat_vbox = QVBoxLayout(self.chat_container)
        # self.chat_vbox.setContentsMargins(0, 0, 0, 0)
        # self.setup_chat_ui() 
        
        # self.main_layout.addWidget(self.chat_container)
       
        self._drag_pos = QPoint()
        # self.collapse_ui() 


    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant
        self.context_text = None
        self.is_expanded = False  
        self.auto_process = False

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)


        
        # self.setFixedSize(70, 70)
        self.setFixedHeight(70)
        self.setMaximumHeight(500)
        self.context_signal.connect(self.add_context)
        # self.main_ui()
        self.ui_floating_chat_bubble()

    def setup_chat_ui(self):
        """Initializes the components for the chat interface."""
        # Scroll Area for Bubbles
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(300) 
        self.scroll.setStyleSheet("background: transparent; border: none;")
        
        # Chat Bubble Container
        self.container = QWidget()
        self.container.setAttribute(Qt.WA_TranslucentBackground)
        self.chat_layout = QVBoxLayout(self.container)
        self.chat_layout.setContentsMargins(10, 5, 10, 5)
        self.chat_layout.setSpacing(15)
        self.chat_layout.addStretch() 
        
        self.scroll.setWidget(self.container)
        self.chat_vbox.addWidget(self.scroll)

        # Context Bar
        self.context_bar = ContextBar(on_remove_callback=self.clear_current_context)
        self.context_bar.remove_btn.clicked.connect(self.clear_current_context)
        self.context_bar.view_btn.clicked.connect(self.show_full_context)
        self.chat_vbox.addWidget(self.context_bar)

        # Input Field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Message...")
        self.input_field.setFixedWidth(260)
        self.input_field.setStyleSheet("""
            border-radius: 15px; 
            padding: 10px; 
            background: white; 
            border: 1px solid #888;
            color: #333;
        """)
        self.input_field.returnPressed.connect(self.process_chat)
        self.chat_vbox.addWidget(self.input_field, alignment=Qt.AlignCenter)

    # State Toggle Methods
    def expand_ui(self):
        print("exapanding ui", self.is_expanded)
        if not self.is_expanded:
            self.icon_widget.hide()
            self.chat_container.show()
            self.setFixedSize(320, 420)
            self.is_expanded = True
            self.input_field.setFocus()

    def collapse_ui(self):
        print("collapsiing ui")
        self.chat_container.hide()
        self.icon_widget.show()
        self.setFixedSize(70, 70)
        self.is_expanded = False

    # Interaction Overrides
    def enterEvent(self, event):
        self.expand_ui()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.collapse_ui()
        # We only collapse if the user isn't currently typing
        # instead of checking if the input field is focused, which will be always.
        # check if user is actively typing before n seconds?
        # if not self.input_field.hasFocus() and self.is_expanded:
        #      QTimer.singleShot(1000, self.collapse_ui) 
        #      pass
        super().leaveEvent(event)

    def clear_current_context(self):
        self.context_bar.clear_context()

    def show_full_context(self):
        QMessageBox.information(self, "Full Context", self.context_bar.full_text)

    def add_message(self, text, is_user=False):
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
        self.on_message_received(text)
  
        # self.context_bar.set_context(text)
        # if self.auto_process:
        #     self.process_chat()
    
