from os import truncate
import threading
from ai_assistant.adapters.base_adapter import ContextFrame
from ai_assistant.adapters.hyprland import HyprlandAdapter
from ai_assistant.core.profile import Profile
from ai_assistant.providers.generic import GenericProvider
from ai_assistant.ui.pyside.main import UI
from assistant import AIAssistant
import time

app_name = "ai-assistant3"
ignore_list = ["python3", "ai-assitant", "ai-assistant3", "app.py"]

assistant = AIAssistant()
provider = GenericProvider("http://localhost:11434/v1/", app_name, "llama3.2")
profile = Profile("general", "You are a coding agent. Always reply only valid code answering the question.")

assistant.provider = provider
assistant.set_system_prompt(profile.system_prompt)

hyprland_adapter = HyprlandAdapter(app_name)

print(assistant.env)
# print(assistant.ask("What is the longest river in Sri Lanka ?"))


def start_watcher(adapter, callback, stop_event=None):
    last = ContextFrame(None, None, False)
    while stop_event is None or not stop_event.is_set():
        try:
            focus_frame = adapter.get_context_frame()
            if focus_frame is None:
                return
            
            if focus_frame.app in ignore_list:
                return
            
            if focus_frame is not None and focus_frame.text and focus_frame.text != last.text:
                callback(focus_frame)
                last = focus_frame
        except Exception as e:
            print(f"Watcher Error: {e}")
        
        time.sleep(0.5)

ui = UI(assistant, app_name)
threading.Thread(target=start_watcher, args=(hyprland_adapter, ui.on_context_changed,), daemon=True).start()
ui.show()
ui.exit()
