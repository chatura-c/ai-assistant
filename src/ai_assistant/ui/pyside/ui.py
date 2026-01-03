from abc import ABC, abstractmethod
import sys
from time import sleep
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication
from ai_assistant.core.host import Host
from ai_assistant.ui.pyside.main import DesktopAssistant

class WindowPlacingStrategy(ABC):
    @abstractmethod
    def move_window(self, ref, x, y):
        pass

    @abstractmethod
    def get_window_position(self, ref, id=None):
        pass

class AdapterWindowPlacingStrategy(WindowPlacingStrategy):
    def __init__(self, adapter) -> None:
        super().__init__()
        self.adapter = adapter

    def move_window(self, ref, x, y):
        self.adapter.move_window(x, y)

    def get_window_position(self, ref, id=None):
        return self.adapter.get_mouse_pos()

class QWindowPlacingStrategy(WindowPlacingStrategy):
    def move_window(self, ref, x, y):
        ref.move(QPoint(x,y))

    def get_window_position(self, ref, id=None):
        pos = ref.pos()
        return (pos.x(), pos.y()) 

class UI:
    def __init__(self, assistant_manager, adapter, app_name):
        app = QApplication(sys.argv)
        app.setDesktopFileName(app_name)
        
        window_move_strategy = QWindowPlacingStrategy()

        if Host.get_desktop().value == "hyprland":
            window_move_strategy = AdapterWindowPlacingStrategy(adapter)


        window = DesktopAssistant(assistant_manager, window_move_strategy)
        
        self.assistant = assistant_manager
        self.window = window
        self.adapter = adapter
        self.app = app

    def show(self):
        self.window.show()

    def run(self):
        sys.exit(self.app.exec())

    def on_context_changed(self, focus_frame):
        self.window.context_signal.emit(focus_frame.text)

