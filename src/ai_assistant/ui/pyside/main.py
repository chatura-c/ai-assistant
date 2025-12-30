from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (QPushButton, QWidget, QMessageBox, QVBoxLayout, QHBoxLayout, QFrame)
from PySide6.QtCore import QObject, QThread, Qt, QTimer, QPoint, Signal, Slot
from ai_assistant.core.manager import AssistantManager
from ai_assistant.ui.pyside.chat_head import ChatHead 
from ai_assistant.ui.pyside.chat_bubble import ChatBubbleContainer
from ai_assistant.ui.pyside.circle import CircleApp
from ai_assistant.ui.pyside.context_bar import ContextBar
from ai_assistant.ui.pyside.chat_box import ChatBox
from ai_assistant.ui.pyside.settings import SettingsWindow


class AskWorker(QThread):
    finished = Signal(str)

    def __init__(self, provider, messages):
        super().__init__()
        self.provider = provider
        self.messages = messages

    def run(self):
        response = self.provider.ask(self.messages)
        self.finished.emit(response)


class DesktopAssistant(QObject):
    context_signal = Signal(str)

    chats:dict[str, QWidget] = {}
    
    def __init__(self, assistant:AssistantManager, adapter):
        super().__init__()
        self.assistant = assistant
        self.adapter = adapter
        self.context_text = None
        self.is_expanded = False  
        self.auto_process = False
        self.active_chat_id = 'general'

        self.head = ChatHead()
        self.head.settings_clicked.connect(self.show_settings)

        self.box = ChatBox("123", None)

        # self.head.on_message_received("Hello world", False, "123")
        self.head.clicked.connect(self.on_chat_head_clicked)

    def show(self):
        assistants = self.assistant.uow.assistants.get_all()
        try:
            if len(assistants) > 0:
                session_id = self.new_chat(assistants[0].profile_id, assistants[0].provider_id)
                profile = self.assistant.uow.profiles.get(assistants[0].profile_id)
                self.head.add_new_chat(profile.picture if profile.picture.strip() != "" else "assets/icon.png", session_id)
                self.head.show()
            else:
                self.show_settings()
        except Exception as e:
            print(e)
            self.show_settings()


    def show_settings(self):
        print("Opening settings")
        self.settings = SettingsWindow(self.assistant.uow)
        self.settings.show()


    def on_chat_head_clicked(self, session_id):
        for id, box in self.chats.items():
            if session_id == id:
                box.show()
                self.move_window(box, self.get_pos(self.head))
            else:
                box.hide()

        self.head.hide()

    def move_window(self, window, pos):
        print("moving to ",pos)
        self.adapter.move_window(pos[0], pos[1])

    def get_pos(self, window):
        return self.adapter.get_mouse_pos()
        
        current_pos = window.pos()

        # if current_pos == QPoint(0, 0):
        current_pos = QCursor.pos()
        print("mouse",current_pos)
        
        offset_x = self.head.width() // 2
        offset_y = self.head.height() // 2
        current_pos = QPoint(current_pos.x() - offset_x, current_pos.y() - offset_y)
        
        return current_pos

        
    def on_chat_box_dismissed(self, session_id):
        chat_window = self.chats.get(session_id)
        current_pos = self.get_pos(chat_window) 

        chat_window.hide()
        
        self.head.show()
        self.move_window(self.head, self.get_pos(self.head))

    def new_chat(self, profile_id: str, provider_id: str):
        session_id = self.assistant.create_session(provider_id=provider_id, profile_id=profile_id)
        chat = ChatBox(session_id, self.assistant.get_assistant(session_id))
        chat.dismissed.connect(self.on_chat_box_dismissed)
        self.chats[session_id] = chat
       
        return session_id


    @Slot(str)
    def add_context(self, text):
        self.context_text = text
        self.on_message_received('general', text)
