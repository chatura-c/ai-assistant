import sys
import math
from PySide6.QtWidgets import (QApplication, QWidget, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame)
from PySide6.QtCore import (QRect, Qt, QPropertyAnimation, Signal,
                           QEasingCurve, QParallelAnimationGroup, QSize, QTimer)
from PySide6.QtGui import QPixmap, QPainter, QBrush, QColor, QPen

class ChatHeadWidget(QPushButton):
    """An orbital button designed to act like a Chat Head with icons."""
    def __init__(self, session_id, icon_path=None, parent=None):
        super().__init__(parent)
        self.session_id = session_id
        self._is_center = False
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFlat(True)
        
        self.pixmap = None
        if icon_path:
            self.pixmap = QPixmap(icon_path)

    def set_center_state(self, is_center):
        self._is_center = is_center
        self.update_style()

    def update_style(self):
        radius = self.width() // 2
        bg = "#3b82f6" if self._is_center else "#ffffff"
        border_color = "#1d4ed8" if self._is_center else "#cbd5e1"
        border_width = 4 if self._is_center else 2
        
        # We use stylesheet for the base and text, but paintEvent for the icon
        self.setStyleSheet(f"""
            QPushButton {{
                border-radius: {radius}px;
                background-color: {bg};
                border: {border_width}px solid {border_color};
                outline: none;
            }}
        """)

    def paintEvent(self, event):
        # Let the stylesheet draw the background and border
        super().paintEvent(event)
        
        if self.pixmap and not self.pixmap.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            
            # Draw pixmap centered and scaled
            margin = 15 if self._is_center else 10
            target_rect = self.rect().adjusted(margin, margin, -margin, -margin)
            scaled_pix = self.pixmap.scaled(target_rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Center the scaled pixmap in the target rect
            x = target_rect.x() + (target_rect.width() - scaled_pix.width()) // 2
            y = target_rect.y() + (target_rect.height() - scaled_pix.height()) // 2
            painter.drawPixmap(x, y, scaled_pix)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_style()

class OrbitalContainer(QWidget):
    clicked = Signal(str) # Emits session_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.center_widget = None
        self.satellites = []
        self.radius = 160 
        self.anim_group = QParallelAnimationGroup(self)
        
        self.center_size = 100
        self.satellite_size = 60

    def add_chat_head(self, session_id, icon_path=None):
        # Don't add if already exists, just swap to center
        for head in [self.center_widget] + self.satellites:
            if head and head.session_id == session_id:
                self.handle_click(head)
                return

        btn = ChatHeadWidget(session_id, icon_path, self)
        btn.clicked.connect(lambda: self.handle_click(btn))
        
        if not self.center_widget:
            self.center_widget = btn
            btn.set_center_state(True)
            btn.setFixedSize(self.center_size, self.center_size)
        else:
            self.satellites.append(btn)
            btn.set_center_state(False)
            btn.setFixedSize(self.satellite_size, self.satellite_size)
            
        btn.show()
        self.refresh_layout(animated=True)

    def handle_click(self, clicked_widget):
        if clicked_widget == self.center_widget or self.anim_group.state() == self.anim_group.State.Running:
            # If clicking active head, emit signal for the main app to handle (e.g., open chat)
            if clicked_widget == self.center_widget:
                self.clicked.emit(clicked_widget.session_id)
            return

        idx = self.satellites.index(clicked_widget)
        old_center = self.center_widget
        
        self.center_widget = clicked_widget
        self.satellites[idx] = old_center
        
        self.center_widget.set_center_state(True)
        old_center.set_center_state(False)
        
        self.refresh_layout(animated=True)

    def refresh_layout(self, animated=True):
        if not self.center_widget: return
        if animated: self.anim_group.clear()
            
        cx, cy = self.width() // 2, self.height() // 2
        
        # Center Target
        center_rect = QRect(cx - self.center_size // 2, cy - self.center_size // 2, self.center_size, self.center_size)
        self._setup_anim(self.center_widget, center_rect, animated)

        # Satellite Targets
        count = len(self.satellites)
        if count > 0:
            start_angle = 0
            end_angle = math.pi
            for i, widget in enumerate(self.satellites):
                angle = start_angle + (i / (count - 1) if count > 1 else 0.5) * (end_angle - start_angle)
                x = cx + self.radius * math.cos(angle) - self.satellite_size // 2
                y = cy + self.radius * math.sin(angle) - self.satellite_size // 2
                self._setup_anim(widget, QRect(int(x), int(y), self.satellite_size, self.satellite_size), animated)

        if animated: self.anim_group.start()

    def _setup_anim(self, widget, target, animated):
        widget.setMinimumSize(0, 0)
        widget.setMaximumSize(16777215, 16777215)
        if animated:
            anim = QPropertyAnimation(widget, b"geometry")
            anim.setDuration(500)
            anim.setStartValue(widget.geometry())
            anim.setEndValue(target)
            anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self.anim_group.addAnimation(anim)
        else:
            widget.setGeometry(target)

    def resizeEvent(self, event):
        self.refresh_layout(animated=False)

class CircleApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orbital Chat Heads")
        self.resize(800, 600)
        self.setStyleSheet("background-color: #f1f5f9;")

        self.layout = QVBoxLayout(self)
        
        self.orbital_view = OrbitalContainer()
        self.orbital_view.clicked.connect(self.on_head_clicked)
        self.layout.addWidget(self.orbital_view, 1)

        # Mock Control Panel
        controls = QHBoxLayout()
        add_btn = QPushButton("Add Mock Chat Session")
        add_btn.setStyleSheet("padding: 10px; background: #1e293b; color: white; border-radius: 5px;")
        add_btn.clicked.connect(self.add_mock_session)
        controls.addStretch()
        controls.addWidget(add_btn)
        controls.addStretch()
        self.layout.addLayout(controls)

        # Initial Sessions
        self.session_count = 0
        for i in range(3): self.add_mock_session()

    def add_mock_session(self):
        self.session_count += 1
        sid = f"session_{self.session_count}"
        # Using a placeholder colored circle via session_id if no icon provided
        self.orbital_view.add_chat_head(sid)

    def on_head_clicked(self, session_id):
        print(f"Opening chat window for: {session_id}")

