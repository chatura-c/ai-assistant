import threading
import time
from typing import Optional

from ai_assistant.repositories.json_uow import  JsonUnitOfWork
from ai_assistant.core.manager import AssistantManager
from ai_assistant.adapters.hyprland import HyprlandAdapter
from ai_assistant.ui.pyside.ui import UI

APP_NAME = "ai-assistant3"
IGNORE_LIST = ["python3", "ai-assistant", "ai-assistant3", "app.py"]

def start_watcher(adapter: HyprlandAdapter, ui_callback, stop_event: Optional[threading.Event] = None):
    last_text = ""
    while stop_event is None or not stop_event.is_set():
        try:
            focus_frame = adapter.get_context_frame()
            
            if focus_frame and focus_frame.app not in IGNORE_LIST:
                if focus_frame.text and focus_frame.text != last_text:
                    ui_callback(focus_frame)
                    last_text = focus_frame.text
        except Exception as e:
            print(f"Watcher Error: {e}")
        
        time.sleep(0.2)

def main():
    uow = JsonUnitOfWork()
    manager = AssistantManager(uow)
    hyprland_adapter = HyprlandAdapter(APP_NAME)
    ui = UI(manager, APP_NAME)

    stop_event = threading.Event()
    watcher_thread = threading.Thread(
        target=start_watcher, 
        args=(hyprland_adapter, ui.on_context_changed, stop_event), 
        daemon=True
    )
    watcher_thread.start()

    try:
        ui.show()
        ui.run()
    except KeyboardInterrupt:
        stop_event.set()
        print("\nShutting down ")

if __name__ == "__main__":
    main()
