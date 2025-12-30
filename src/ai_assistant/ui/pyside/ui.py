import sys
from PySide6.QtWidgets import QApplication
from ai_assistant.ui.pyside.main import DesktopAssistant

class UI:
    def __init__(self, assistant_manager, adapter, app_name):
        app = QApplication(sys.argv)
        app.setDesktopFileName(app_name)
        window = DesktopAssistant(assistant_manager, adapter)
        
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

