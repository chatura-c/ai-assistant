from ai_assistant.adapters.base_adapter import BaseAdapter

import gi
import threading

from assistant import AIAssistant

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

class AssistantPopup(Gtk.Window):
    assistant: AIAssistant
    adaptor: BaseAdapter

    def __init__(self, adaptor: BaseAdapter):
        super().__init__(title="AI Assistant")
        self.adaptor = adaptor

        self.selected_text = ""
        self.is_expanded = False
        self.hide_timer = None

        # 1. Window Configuration
        self.set_name("ai-assistant")
        self.set_keep_above(True)
        self.set_decorated(False) 
        
        # 2. UI Layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.add(self.main_box)

        # Icon View (The "Faded Icon")
        self.icon_image = Gtk.Image.new_from_icon_name("view-reveal-symbolic", Gtk.IconSize.DND)
        self.main_box.pack_start(self.icon_image, True, True, 0)

        # App View Container (Hidden initially)
        self.app_view = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        self.entry = Gtk.Entry(placeholder_text="Ask llama3.2...")
        self.entry.connect("activate", self.on_trigger_action)
        self.app_view.pack_start(self.entry, False, False, 0)

        self.text_view = Gtk.TextView(editable=True, wrap_mode=Gtk.WrapMode.WORD)
        scrolled = Gtk.ScrolledWindow(min_content_height=150)
        scrolled.add(self.text_view)
        self.app_view.pack_start(scrolled, True, True, 0)
        
        self.btn_use = Gtk.Button(label="Replace Selection")
        self.btn_use.connect("clicked", self.on_use_clicked)
        self.app_view.pack_start(self.btn_use, False, False, 0)

        self.main_box.pack_start(self.app_view, True, True, 0)

        # 3. Events
        self.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
        self.connect("enter-notify-event", self.expand_ui)
        self.connect("delete-event", lambda w, e: self.hide_on_delete())
    
    def on_context_updated(self):
        self.selected_text = self.adaptor.get_context_text()
        # print(self.context_text.get_buffer().set_text(self.selected_text))
        self.show_as_icon()
        
    def show_as_icon(self):
        self.is_expanded = False
        self.app_view.hide()
        self.icon_image.show()
        self.set_opacity(0.4)
        self.set_resizable(False)
        self.resize(32, 32)

        # Move to cursor
        x, y = self.adaptor.get_mouse_pos()
        self.move(15, 15)
        print("Mouse Position")
        print(x,y)

        self.show_all()
        self.app_view.hide() 

        if self.hide_timer: GLib.source_remove(self.hide_timer)
        self.hide_timer = GLib.timeout_add_seconds(3, self.hide_if_unexpanded)

    def expand_ui(self, widget, event):
        if self.is_expanded: return
        
        if self.hide_timer: GLib.source_remove(self.hide_timer)
        self.is_expanded = True
        
        # Morph into full window
        self.set_opacity(1.0)
        self.icon_image.hide()
        self.app_view.show_all()
        self.resize(400, 300)
        self.set_resizable(True)
        self.entry.grab_focus()

    def hide_if_unexpanded(self):
        if not self.is_expanded:
            self.hide()
        return False

    def on_use_clicked(self, btn):
        buffer = self.text_view.get_buffer()
        res = buffer.get_selection_bounds()
        start, end = res if res else buffer.get_bounds()
        final_text = buffer.get_text(start, end, True)

        self.adaptor.copy_text_into_clipboard(final_text) 
        self.hide()
        
        # Small delay for focus return
        GLib.timeout_add(200, lambda: self.adaptor.replace_selected_text(final_text))

    def on_trigger_action(self, entry):
        query = entry.get_text()
        threading.Thread(target=self.ask_llm, args=(query,), daemon=True).start()

    def ask_llm(self, query):
        try:
            resp = self.assistant.ask(query)
            GLib.idle_add(lambda: self.text_view.get_buffer().set_text(resp))
        except:
            GLib.idle_add(lambda: self.text_view.get_buffer().set_text(":( AI is not doing well"))
    
