from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class ContextFrame:
    text: str | None
    app: str | None
    is_ignored: bool

class BaseAdapter(ABC):
    @abstractmethod
    def replace_selected_text(self, new_text):
        pass

    @abstractmethod
    def get_mouse_pos(self) -> tuple[int, int]:
        pass

    @abstractmethod
    def get_context_frame(self) -> ContextFrame:
        pass

    @abstractmethod
    def copy_text_into_clipboard(self, text):
        pass

    @abstractmethod
    def move_window(self, x, y):
        pass

