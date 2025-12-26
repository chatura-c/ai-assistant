import sys
from PySide6.QtWidgets import QApplication
from ai_assistant.ui.pyside.main import DesktopAssistant

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

