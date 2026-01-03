
from PySide6.QtCore import Qt

def movable(cls):
    orig_press = getattr(cls, 'mousePressEvent', None)
    orig_move = getattr(cls, 'mouseMoveEvent', None)
    orig_release = getattr(cls, 'mouseReleaseEvent', None)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = True
            self._drag_start_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        elif orig_press:
            orig_press(self, event)

    def mouseMoveEvent(self, event):
        if getattr(self, '_drag_active', False) and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_start_pos)
            event.accept()
        elif orig_move:
            orig_move(self, event)
    
    def mouseReleaseEvent(self, event):
        if self._drag_active and self._drag_start_pos:
            distance = (event.pos() - self._drag_start_pos).manhattanLength()
            if distance < 3: 
                orig_press(self, event) 
        
        self._drag_active = False
        if orig_release:
            orig_release(self, event)

    cls.mousePressEvent = mousePressEvent
    cls.mouseMoveEvent = mouseMoveEvent
    cls.mouseReleaseEvent = mouseReleaseEvent
    
    orig_init = cls.__init__
    def new_init(self, *args, **kwargs):
        self._drag_active = False
        self._drag_start_pos = None
        orig_init(self, *args, **kwargs)
    
    cls.__init__ = new_init
    return cls
