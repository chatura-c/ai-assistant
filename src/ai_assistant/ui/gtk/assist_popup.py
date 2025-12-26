import gi
import threading

from ai_assistant.adapters.base_adapter import BaseAdapter
from assistant import AIAssistant

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

try:
    gi.require_version('GtkLayerShell', '0.1')
    from gi.repository import GtkLayerShell
except ValueError:
    raise ImportError("GTK Layer Shell not found. Install 'libgtk-layer-shell-dev'.")

from gi.repository import Gtk, Gdk, GLib

class AssistantPopup(Gtk.Window):
    assistant: AIAssistant
    adaptor: BaseAdapter

    def __init__(self, adaptor):
        super().__init__()
        self.adaptor = adaptor

        # State Variables
        self.is_expanded = False
        self.hide_timer = None
        
        # Dragging State
        self.drag_start_pos = None  # Offset within the window
        self.current_x = 100        # Current Margin Left
        self.current_y = 100        # Current Margin Top

        # 1. Initialize Layer Shell
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        
        # Anchor to Top-Left to treat margins as X/Y coordinates
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)

        # 2. UI Layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(self.main_box)

        # --- ICON VIEW (Minimized) ---
        self.icon_event_box = Gtk.EventBox()
        self.icon_image = Gtk.Image.new_from_icon_name("view-reveal-symbolic", Gtk.IconSize.DND)
        self.icon_event_box.add(self.icon_image)
        self.main_box.pack_start(self.icon_event_box, True, True, 0)

        # --- APP VIEW (Expanded) ---
        self.app_view = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.app_view.set_border_width(8)
        
        # Drag Handle for Expanded Mode
        self.drag_handle = Gtk.EventBox()
        self.drag_handle.set_size_request(-1, 15)
        # Visual cue for the handle
        handle_visual = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.drag_handle.add(handle_visual)
        self.app_view.pack_start(self.drag_handle, False, False, 0)

        self.entry = Gtk.Entry(placeholder_text="Ask AI...")
        self.entry.connect("activate", self.on_trigger_action)
        self.app_view.pack_start(self.entry, False, False, 0)

        self.text_view = Gtk.TextView(editable=True, wrap_mode=Gtk.WrapMode.WORD)
        scrolled = Gtk.ScrolledWindow(min_content_height=200, min_content_width=350)
        scrolled.add(self.text_view)
        self.app_view.pack_start(scrolled, True, True, 0)

        self.btn_use = Gtk.Button(label="Replace Selection")
        self.btn_use.connect("clicked", self.on_use_clicked)
        self.app_view.pack_start(self.btn_use, False, False, 0)

        self.main_box.pack_start(self.app_view, True, True, 0)

        # 3. Signals and Events
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | 
                        Gdk.EventMask.BUTTON_RELEASE_MASK | 
                        Gdk.EventMask.POINTER_MOTION_MASK)

        # Connect Dragging to both the Icon and the Handle
        for widget in [self.icon_event_box, self.drag_handle]:
            widget.connect("button-press-event", self.on_drag_start)
            widget.connect("motion-notify-event", self.on_drag_motion)
            widget.connect("button-release-event", self.on_drag_end)

        # Interaction to Expand
        self.icon_event_box.connect("enter-notify-event", self.expand_ui)

    # --- DRAG LOGIC ---
    def on_drag_start(self, widget, event):
        if event.button == 1: # Left Click
            # Store the relative offset of the click inside the widget
            self.drag_start_pos = (event.x, event.y)
            # Change cursor to 'grabbing'
            window = self.get_window()
            if window:
                window.set_cursor(Gdk.Cursor.new_from_name(Gdk.Display.get_default(), "grabbing"))
        return True

    def on_drag_motion(self, widget, event):
        if self.drag_start_pos is not None:
            # Update margins based on global mouse position minus the initial offset
            self.current_x = int(event.x_root - self.drag_start_pos[0])
            self.current_y = int(event.y_root - self.drag_start_pos[1])
            
            GtkLayerShell.set_margin(self, GtkLayerShell.Edge.LEFT, self.current_x)
            GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, self.current_y)
        return True

    def on_drag_end(self, widget, event):
        self.drag_start_pos = None
        # Reset cursor
        window = self.get_window()
        if window:
            window.set_cursor(None)
        return True

    # --- UI TRANSITIONS ---
    def on_context_updated(self):
        # Initial placement near mouse
        mx, my = self.adaptor.get_mouse_pos()
        self.current_x, self.current_y = mx + 10, my + 10
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.LEFT, self.current_x)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, self.current_y)
        self.show_as_icon()

    def show_as_icon(self):
        self.is_expanded = False
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.NONE)
        self.app_view.hide()
        self.icon_event_box.show()
        self.set_opacity(0.5)
        self.resize(32, 32)
        self.show_all()
        self.app_view.hide()

        if self.hide_timer: GLib.source_remove(self.hide_timer)
        self.hide_timer = GLib.timeout_add_seconds(3, self.hide_if_unexpanded)

    def expand_ui(self, widget, event):
        if self.is_expanded: return
        self.is_expanded = True
        if self.hide_timer: GLib.source_remove(self.hide_timer)
        
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)
        self.set_opacity(1.0)
        self.icon_event_box.hide()
        self.app_view.show_all()
        self.entry.grab_focus()

    def hide_if_unexpanded(self):
        if not self.is_expanded:
            self.hide()
        return False

    # --- ACTIONS ---
    def on_trigger_action(self, entry):
        query = f"{entry.get_text()} \n Context: {self.adaptor.get_context_text()}"
        threading.Thread(target=self.ask_llm, args=(query,), daemon=True).start()

    def ask_llm(self, query):
        try:
            resp = self.assistant.ask(query)
            GLib.idle_add(lambda: self.text_view.get_buffer().set_text(resp))
        except:
            GLib.idle_add(lambda: self.text_view.get_buffer().set_text("AI error..."))

    def on_use_clicked(self, btn):
        buf = self.text_view.get_buffer()
        text = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), True)
        self.adaptor.copy_text_into_clipboard(text)
        self.hide()
        GLib.timeout_add(200, lambda: self.adaptor.replace_selected_text(text))
