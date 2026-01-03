from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (QPushButton, QWidget, QMessageBox, QVBoxLayout, QHBoxLayout, QFrame)
from PySide6.QtCore import QObject, QThread, Qt, QTimer, QPoint, Signal, Slot
from ai_assistant.core.manager import AssistantManager
from ai_assistant.ui.pyside.chat import chat_box
from ai_assistant.ui.pyside.chat.chat_head import ChatHead 
from ai_assistant.ui.pyside.chat.chat_bubble import ChatBubbleContainer
# from ai_assistant.ui.pyside.chat.context_bar import ContextBar
from ai_assistant.ui.pyside.chat.chat_box import ChatBox
from ai_assistant.ui.pyside.settings.settings import SettingsWindow


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
    
    def __init__(self, assistant:AssistantManager, mover):
        super().__init__()
        self.assistant = assistant
        self.window_mover = mover
        self.context_text = None
        self.is_expanded = False  
        self.auto_process = False
        self.active_chat_id = 'general'

        self.head = ChatHead()
        self.head.settings_clicked.connect(self.show_settings)

        self.box = ChatBox("temp", None)

        # self.head.on_message_received("Hello world", False, "123")
        self.head.clicked.connect(self.on_chat_head_clicked)
        self.context_signal.connect(self.add_context)

    def show(self):
        assistants = self.assistant.uow.assistants.get_all()
        try:
            if len(assistants) > 0:
                session_id = self.new_chat(assistants[1].profile_id, assistants[1].provider_id)
                profile = self.assistant.uow.profiles.get(assistants[1].profile_id)
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
        move_pos = self.get_pos(self.head)
        target_box = None

        for id, box in self.chats.items():
            if session_id == id:
                box.show()
                target_box = box
                if box.docked:
                    mov_pos = box.docked_at
            else:
                box.hide()

        self.head.hide()
        # QTimer.singleShot(100, lambda: self.move_window(target_box, move_pos))

        self.move_window(target_box, move_pos)

    def move_window(self, window, pos):
        print("moving to ",pos)
        self.window_mover.move_window(window, pos[0], pos[1])

    def get_pos(self, window):
        return self.window_mover.get_window_position(window)
        
    def on_chat_box_dismissed(self, session_id):
        chat_window = self.chats.get(session_id)
        move_pos = self.get_pos(chat_window) 
        
        if chat_window.docked:
            move_pos = chat_window.docked_at

        if not chat_window.pinned:
            chat_window.hide()
            self.head.show()
            self.move_window(self.head, move_pos)

    def on_chat_box_docked(self, session_id):
        chat_window = self.chats.get(session_id)
        current_pos = self.get_pos(chat_window) 

        chat_window.set_docked_at(current_pos)


    def new_chat(self, profile_id: str, provider_id: str):
        session_id = self.assistant.create_session(provider_id=provider_id, profile_id=profile_id)
        chat = ChatBox(session_id, self.assistant.get_assistant(session_id))
        chat.dismissed.connect(self.on_chat_box_dismissed)
        chat.dock_clicked.connect(self.on_chat_box_docked)
        chat.show()
        chat.pinned = True
        self.chats[session_id] = chat
       
        return session_id


    @Slot(str)
    def add_context(self, text):
        # self.context_text = text
        print("REceie", text)
        for box in self.chats.values():
            box.on_context_text_received(text)
