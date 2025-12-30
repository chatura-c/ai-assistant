
import subprocess
import json
from collections import deque

from ai_assistant.core.adapter import BaseAdapter, ContextFrame
from ai_assistant.core.host import Host

class HyprlandAdapter(BaseAdapter):
    def __init__(self, max_history=10) -> None:
        super().__init__()
        self.app_name = Host.APP_ID
        self.ignore_classes = [self.app_name]
        
        self.stack: deque[ContextFrame] = deque(maxlen=max_history)
        self.stack.append(ContextFrame(None, None, False))

    def replace_selected_text(self, new_text):
        pass

    def get_focused_window(self) -> str | None:
        try:
            output = subprocess.check_output(["hyprctl", "activewindow", "-j"], timeout=0.1)
            data = json.loads(output)
            
            return data.get("class") 
        except:
            return None
    
    def get_mouse_pos(self) -> tuple[int, int]:
        pos = subprocess.check_output(["hyprctl", "cursorpos"]).decode().strip()
        x, y = map(int, pos.split(","))
        return (x, y)

    def get_context_frame(self) -> ContextFrame:
        current_focus = self.get_focused_window()
        raw_text = self._get_raw_wl_paste()
        
        is_ignored = current_focus in self.ignore_classes
        last_frame = self.stack[-1]

        if raw_text and raw_text != last_frame.text:
            if is_ignored:
                raw_text = None

            new_frame = ContextFrame(
                text=raw_text,
                app=current_focus,
                is_ignored=is_ignored
            )
            self.stack.append(new_frame)

        # if current_focus != last_frame.app or (raw_text and raw_text != last_frame.text):
        #     new_frame = ContextFrame(
        #         text=raw_text if not is_ignored else "",
        #         app=current_focus,
        #         is_ignored=is_ignored
        #     )
        #     self.stack.append(new_frame)

        for frame in reversed(self.stack):
            if not frame.is_ignored and frame.text:
                return frame

        return ContextFrame(None, None, False)
    
    def _get_raw_wl_paste(self) -> str | None:
        """Internal helper to grab text without logic."""
        try:
            primary = subprocess.check_output(
                ["wl-paste", "--primary", "--no-newline"], 
                stderr=subprocess.DEVNULL, timeout=0.05
            ).decode().strip()
            
            if primary: return primary

            return subprocess.check_output(
                ["wl-paste", "--no-newline"], 
                stderr=subprocess.DEVNULL, timeout=0.05
            ).decode().strip()
        except:
            return None

    def copy_text_into_clipboard(self, text):
        subprocess.run(["wl-copy"], input=text)

    def move_window(self, x, y):
        x, y = int(x), int(y)
        cmd = [
            "hyprctl", "dispatch", 
            "movewindowpixel", 
            f"exact {x} {y},class:^{self.app_name}$"
        ]
        
        subprocess.Popen(cmd)
