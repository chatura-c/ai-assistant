from PySide6.QtWidgets import (QWidget, QMessageBox, QVBoxLayout, QHBoxLayout, QFrame)
from PySide6.QtCore import Qt, QTimer, QPoint, Signal, Slot
from ai_assistant.ui.pyside.chat_head import ChatHead 
from ai_assistant.ui.pyside.chat_bubble import ChatBubbleContainer
from ai_assistant.ui.pyside.context_bar import ContextBar
from ai_assistant.ui.pyside.chat_box import ChatBox

class Chat:
    def __init__(self, head, box) -> None:
        self.head = head
        self.box = box

class DesktopAssistant(QWidget):
    context_signal = Signal(str)

    chats = {}
    
    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant
        self.context_text = None
        self.is_expanded = False  
        self.auto_process = False

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # self.setFixedSize(70, 70)
        # self.setHeight(70)
        self.setMaximumHeight(500)
        self.context_signal.connect(self.add_context)
        

        self.chat_head_wrapper = QFrame(self) 
        self.el_floating_head_layout = QHBoxLayout(self.chat_head_wrapper)
        self.el_floating_head_layout.addStretch()
    
        self.el_main_layout = QVBoxLayout(self)
        self.el_main_layout.addWidget(self.chat_head_wrapper)
        # self.collapse_ui()

        self.new_chat('general')
        self.active_chat_id = 'general'
        
        self.collapse_timer = QTimer()
        self.collapse_timer.setSingleShot(True)
        self.collapse_timer.setInterval(5000)
        self.collapse_timer.timeout.connect(self.check_and_collapse)


        self.collapse_ui()


    def on_chat_head_clicked(self, head_id):
        print("Clicked ", head_id)
        self.expand_ui()


    def new_chat(self, id: str):
        self.chats[id] = Chat(self.add_chat_head(id), self.add_chat_box(id))


    def add_chat_box(self, id):
        chat_box = ChatBox(id)
        chat_box.text_entered.connect(self.process_chat)
        self.el_main_layout.addWidget(chat_box)
        return chat_box


    def add_chat_head(self, id):
        head = ChatHead("assets/icon.png", id=id)
        head.clicked.connect(self.on_chat_head_clicked)
        self.el_floating_head_layout.insertWidget(0, head, alignment=Qt.AlignCenter)
        return head


    def on_message_received(self, chat_id, text, is_user=False):
        self.chats[chat_id].box.add_message(text, is_user)

        if not self.is_expanded:
            for i in reversed(range(self.el_floating_head_layout.count())):
                widget = self.el_floating_head_layout.itemAt(i).widget()
                if widget and widget.objectName() != "chat_head":
                    widget.deleteLater()

            new_bubble = ChatBubbleContainer(text, is_user=is_user, temporary=True)
            self.el_floating_head_layout.addWidget(new_bubble, alignment=Qt.AlignCenter)
    

    def expand_ui(self):
        if not self.is_expanded:
            self.chat_head_wrapper.hide()
            self.chats[self.active_chat_id].box.show()
            self.is_expanded = True
            self.updateGeometry()


    def collapse_ui(self):
        for c in self.chats.values():
            c.box.hide()
        self.chat_head_wrapper.show()
        self.is_expanded = False
        self.updateGeometry()
    

    def check_and_collapse(self):
        print("Checking before collapsing ", self.hasFocus(), self.focusWidget())
        if not self.hasFocus():
            self.collapse_ui()
        else:
            self.collapse_timer.start()
    

    def enterEvent(self, event):
        self.collapse_timer.stop()
        super().enterEvent(event)


    def leaveEvent(self, event):
        self.collapse_timer.start()
        super().leaveEvent(event)
    

    def clear_current_context(self):
        self.context_bar.clear_context()


    def show_full_context(self):
        QMessageBox.information(self, "Full Context", self.context_bar.full_text)


    def scroll_to_bottom(self):
        bar = self.scroll.verticalScrollBar()
        bar.setValue(bar.maximum())


    def process_chat(self, text):
        messages = [] 
        if text and text.strip() != "":
            messages.append(text)
            self.on_message_received('general', text, is_user=True)

        # if self.context_text and self.context_text.strip() != "" :
        #     messages.append(self.context_text)
        #     self.on_message_received(self.context_text, is_user=True)

        if len(messages) > 0:
            response = self.assistant.ask(messages)
            QTimer.singleShot(800, lambda: self.on_message_received('general', response, is_user=False))


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()


    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
    

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.collapse_ui()
            self.collapse_timer.stop()
        else:
            super().keyPressEvent(event)


    @Slot(str)
    def add_context(self, text):
        self.context_text = text
        self.on_message_received('general', text)
  
        # self.context_bar.set_context(text)
        # if self.auto_process:
        #     self.process_chat()
    
