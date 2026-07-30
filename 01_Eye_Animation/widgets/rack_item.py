from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QPushButton

class RackItem(QPushButton):
    clicked_signal = pyqtSignal(str)

    def __init__(self, rack_name: str, parent=None):
        super().__init__(rack_name, parent)

        self._rack_name = rack_name
        self._selected = False

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.setFixedSize(198, 78)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_style()

    def setup_connections(self):
        self.clicked.connect(self._emit_clicked)

    def _emit_clicked(self):
        self.clicked_signal.emit(self._rack_name)

    def set_selected(self, selected: bool):
        self._selected = selected
        self.update_style()


    def update_style(self):
        if self._selected:
            self.setStyleSheet("""
                QPushButton{
                    background:#e8f3ff;
                    border:2px solid #1677d2;
                    border-radius:8px;
                    color:#0f172a;
                    font-size:18px;
                    font-weight:700;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton{
                    background:#ffffff;
                    border:1px solid #cfd6df;
                    border-radius:8px;
                    color:#101828;
                    font-size:18px;
                    font-weight:700;
                }
                QPushButton:hover{
                    background:#f4f9ff;
                    border:1px solid #8abef2;
                }
                QPushButton:pressed{
                    background:#eaf4ff;
                }
            """)

if __name__ == "__main__":

    import sys

    from PyQt6.QtWidgets import (QApplication,QWidget,QVBoxLayout,)

    app = QApplication(sys.argv)

    window = QWidget()

    window.setStyleSheet("""background:white;""")

    layout = QVBoxLayout(window)

    rack1 = RackItem("Rack 1")
    rack2 = RackItem("Rack 2")

    racks = [rack1, rack2]

    def rack_clicked(name):
        for rack in racks:
            rack.set_selected(rack.text() == name)

        print(f"Selected: {name}")

    layout.addWidget(rack1)
    layout.addWidget(rack2)

    window.resize(260, 220)
    window.show()

    sys.exit(app.exec())
