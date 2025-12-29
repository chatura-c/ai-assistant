from ai_assistant.core.adapter import BaseAdapter, ContextFrame

class NullAdapter(BaseAdapter):
    def replace_selected_text(self, new_text):
        pass

    def get_mouse_pos(self) -> tuple[int, int]:
        return (0, 0)

    def get_context_frame(self) -> ContextFrame:
        return ContextFrame(text=None, app=None, is_ignored=True)
    
    def copy_text_into_clipboard(self, text):
        pass
