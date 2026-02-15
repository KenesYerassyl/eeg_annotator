from typing import Optional, Tuple

from PyQt6.QtCore import QObject, pyqtSignal

class AppState(QObject):
    scale_changed = pyqtSignal()
    montage_changed = pyqtSignal()
    montage_list_changed = pyqtSignal()
    filter_changed = pyqtSignal()
    
    label_clicked = pyqtSignal()
    draw_mode_changed = pyqtSignal(bool)
    spinner_value_changed = pyqtSignal(int)
    goto_input_return_pressed = pyqtSignal(int)
    undo_clicked = pyqtSignal()
    enable_undo_button = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._montage = 'AVERAGE'
        self._filter = (None, None)
        self._montage_list = []
        self._scale = 0

    def set_montage_list(self, montage_list):
        if montage_list != self._montage_list:
            self._montage_list = montage_list
            self.montage_list_changed.emit()

    @property
    def montage_list(self):
        return self._montage_list

    def set_montage(self, montage):
        if montage != self._montage:
            self._montage = montage
            self.montage_changed.emit()
    
    @property
    def montage(self) -> str:
        return self._montage

    def set_filter(self, filter):
        if filter != self._filter:
            self._filter = filter
            self.filter_changed.emit()
    
    @property
    def filter(self) -> Tuple[Optional[float], Optional[float]]:
        return self._filter
    
    def set_scale(self, scale):
        if scale != self._scale:
            self._scale = scale
            self.scale_changed.emit()
    
    @property
    def scale(self) -> int:
        return self._scale