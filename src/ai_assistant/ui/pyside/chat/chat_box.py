from abc import abstractmethod
from PySide6.QtWidgets import (QLabel, QLineEdit, QPushButton, QScrollArea, QTextEdit, QWidget, 
                             QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy, 
                             QGraphicsDropShadowEffect, QTextBrowser)
from PySide6.QtCore import Qt, Signal, QThread, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QColor, QFont, QFontMetrics

# Assuming these imports exist in your project
from ai_assistant.ui.pyside.chat.chat_bubble import ChatBubbleContainer
from ai_assistant.ui.pyside.context_bar import ContextBar
from ai_assistant.ui.pyside.styles import scrollbar_style
from ai_assistant.ui.pyside.icons import dock_icon, pin_icon
from ai_assistant.ui.pyside.movable import movable

# UI Constants for easy tweaking
OPACITY = 0.65 

class AskWorker(QThread):
    finished = Signal(str)
    def __init__(self, provider_func, messages):
        super().__init__()
        self.provider_func = provider_func
        self.messages = messages

    def run(self):
        response = self.provider_func(self.messages)
        self.finished.emit(response) 

class LoadingIndicator(QFrame):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 10, 15, 10)
        self.layout.setSpacing(4)
        
        self.label = QLabel("Thinking")
        self.label.setStyleSheet("color: white; font-weight: 500; font-size: 12px; font-family: 'Segoe UI', sans-serif; background: transparent;")
        self.layout.addWidget(self.label)
        
        self.dots = QLabel("...")
        self.dots.setStyleSheet("color: #33ccff; font-weight: bold; font-size: 14px; background: transparent;")
        self.layout.addWidget(self.dots)
        self.layout.addStretch()
        
        self.setStyleSheet(f"""
            QFrame {{
                background: rgba(255, 255, 255, 0.15);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
        """)
        self.setFixedWidth(110)
        self.hide()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(500)
        self.dot_count = 0

    def _animate(self):
        self.dot_count = (self.dot_count + 1) % 4
        self.dots.setText("." * self.dot_count)


class AutoResizingTextEdit(QTextEdit):
    text_submitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Type a message...")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.textChanged.connect(self.adjust_height)
        self.adjust_height()

        self.setStyleSheet(f"""
            QTextEdit {{
                border-radius: 10px; 
                padding: 5px; 
                background: rgba(0, 0, 0, 0.3); 
                border: 1px solid rgba(255, 255, 255, 0.15);
                color: white;
                font-size: 13px;
            }}
            /* Style the scrollbar for when it hits 10+ lines */
            QScrollBar:vertical {{
                width: 4px;
                background: transparent;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(255, 255, 255, 0.2);
                border-radius: 2px;
            }}
        """)

    def adjust_height(self):
        doc = self.document()
        font_metrics = QFontMetrics(self.font())
        
        line_height = font_metrics.lineSpacing()
        margins = self.contentsMargins()
        padding = self.document().documentMargin()
        
        num_lines = doc.blockCount() 
        
        content_height = doc.size().height() + (margins.top() + margins.bottom() + 10)
        
        min_height = line_height + 20 
        max_height = (line_height * 10) + 20 
        
        if content_height <= min_height:
            new_height = min_height
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        elif content_height >= max_height:
            new_height = max_height
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        else:
            new_height = content_height
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setFixedHeight(new_height)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            modifiers = event.modifiers()
            if modifiers & Qt.ControlModifier:
                self.text_submitted.emit(self.toPlainText())
                return

            if modifiers & Qt.ShiftModifier:
                self.text_submitted.emit(self.toPlainText())
                return 

            if modifiers & Qt.AltModifier:
                self.text_submitted.emit(self.toPlainText())
                return

        super().keyPressEvent(event)

@movable
class ChatBox(QWidget):
    dismissed = Signal(str)
    dock_clicked = Signal(str)

    pinned = False
    docked = False
    auto_send = False

    docked_at = 0,0

    context_text:str = ""

    def __init__(self, session_id, assistant):
        super().__init__()
        self.session_id = session_id
        self.assistant = assistant 
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(350)
        self.setMinimumHeight(500)

        self.idle_timer = QTimer(singleShot=True)
        self.idle_timer.timeout.connect(lambda: self.dismissed.emit(session_id))

        self.init_ui()

    def init_ui(self):
        self.content_widget = QWidget()
        self.content_widget.setObjectName("MainContent")
        
        self.content_widget.setStyleSheet(f"""
            QWidget#MainContent {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                            stop:0 rgba(51, 204, 255, {OPACITY}), 
                                            stop:1 rgba(238, 130, 238, {OPACITY}));
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.15);
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.content_widget.setGraphicsEffect(shadow)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.addWidget(self.content_widget)

        self.inner_layout = QVBoxLayout(self.content_widget)
        self.inner_layout.setContentsMargins(12, 12, 12, 12)
        self.inner_layout.setSpacing(10)
        
        self.header_layout = QHBoxLayout()

        header = QLabel("AI Assistant")
        header.setStyleSheet("color: white; font-weight: bold; font-size: 15px; padding: 5px; font-family: 'Segoe UI'; background: transparent;")
        self.header_layout.addWidget(header)

        self.pin_btn = QPushButton()
        self.pin_btn.setIcon(pin_icon())
        self.pin_btn.setFlat(True)
        self.pin_btn.clicked.connect(self.on_pin_clicked)
        self.header_layout.addWidget(self.pin_btn) 
    

        self.dock_btn = QPushButton()
        self.dock_btn.setIcon(dock_icon())
        self.dock_btn.setFlat(True)
        self.dock_btn.clicked.connect(self.on_dock_clicked)
        self.header_layout.addWidget(self.dock_btn)

        self.inner_layout.addLayout(self.header_layout)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.verticalScrollBar().setStyleSheet(scrollbar_style)

        self.container = QWidget()
        self.container.setAttribute(Qt.WA_TranslucentBackground)
        self.chat_layout = QVBoxLayout(self.container)
        self.chat_layout.setContentsMargins(2, 5, 2, 5)
        self.chat_layout.setSpacing(15)
        
        self.typing_indicator = LoadingIndicator()
        self.chat_layout.addWidget(self.typing_indicator)
        self.chat_layout.addStretch() 
        
        self.scroll.setWidget(self.container)
        self.inner_layout.addWidget(self.scroll)

        self.context_layout = QHBoxLayout()
        self.inner_layout.addLayout(self.context_layout)

        self.input_field = AutoResizingTextEdit()
        self.input_field.text_submitted.connect(self.on_text_entered)
        self.inner_layout.addWidget(self.input_field)
        self.input_field.setFocus()
        

    def on_context_text_received(self, text):
        self.remove_context()
        self.add_context(text)


    def on_context_text_dismissed(self):
        self.remove_context() 
    
    def add_context(self, text):
        self.ctx_txt = ContextBar(text)
        self.ctx_txt.context_dismissed.connect(self.on_context_text_dismissed)
        self.ctx_txt.context_clicked.connect(self.on_context_text_clicked)
        self.context_layout.addWidget(self.ctx_txt)

    def remove_context(self):
        if hasattr(self, 'ctx_txt') and self.ctx_txt is not None:
            self.ctx_txt.setParent(None)
            self.ctx_txt.deleteLater() 
            self.ctx_txt = None

    def get_context_text(self):
        if hasattr(self, 'ctx_txt') and self.ctx_txt is not None:
            text = self.ctx_txt.full_text
            if text is not None and text != "":
                return text
        
        return None


    def on_context_text_clicked(self, txt):
        self.input_field.setText(txt)
        self.remove_context()
      

    def on_text_entered(self, text):
        if not text or text == "":
            return

        ctx_text = self.get_context_text()
        self.remove_context() 
        
        messages = [] 
        
        if ctx_text is not None:
            messages.append(ctx_text)

        messages.append(text)
        
        for m in messages:
            self.add_message(m, is_user=True)
        self.show_typing(True)
        self.input_field.clear()
        self.process_chat(messages)

    def process_chat(self, texts):
        self.worker = AskWorker(self.assistant.ask, texts)
        self.worker.finished.connect(self.handle_assistant_response)
        self.worker.start()

    def handle_assistant_response(self, response):
        self.show_typing(False)
        self.add_message(response, is_user=False)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()

    def show_typing(self, visible: bool):
        if visible:
            self.typing_indicator.show()
        else:
            self.typing_indicator.hide()
        self.scroll_to_bottom()

    def add_message(self, text, is_user=True):
        msg = ChatBubbleContainer(text, is_user)
        idx = self.chat_layout.indexOf(self.typing_indicator)
        if idx == -1:
            idx = self.chat_layout.count() - 1
            
        self.chat_layout.insertWidget(idx, msg)
        msg.show()
        
        # QTimer.singleShot(10, lambda: self._refresh_layout(msg))
        # QTimer.singleShot(50, self.scroll_to_bottom)

    def _refresh_layout(self, msg_widget):
        """Forces the layout to recalculate and bubbles to adjust their internal height."""
        if hasattr(msg_widget, 'bubble'):
            msg_widget.bubble.adjust_height()
        self.container.updateGeometry()
        self.container.layout().activate()

    def scroll_to_bottom(self):
        bar = self.scroll.verticalScrollBar()
        bar.setValue(bar.maximum())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.dismissed.emit(self.session_id)
            event.accept()
        else:
            super().keyPressEvent(event)

    def leaveEvent(self, event) -> None:
        self.idle_timer.start(8000)

    def enterEvent(self, event) -> None:
        self.idle_timer.stop()

    def set_docked_at(self, pos):
        self.docked_at = pos
        print("Setting anchor", pos)

    def on_dock_clicked(self):
        self.docked = not self.docked
        if self.docked:
            self.dock_btn.setIcon(dock_icon("white"))
        else:
            self.dock_btn.setIcon(dock_icon("grey"))
        self.dock_clicked.emit(self.session_id)

    def on_pin_clicked(self):
        self.pinned = not self.pinned
        if self.pinned:
            self.pin_btn.setIcon(pin_icon("white"))
        else:
            self.pin_btn.setIcon(pin_icon("grey"))

