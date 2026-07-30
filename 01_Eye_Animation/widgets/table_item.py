from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QPushButton

class TableItem(QPushButton):
    clicked_signal = pyqtSignal(str)

    def __init__(self, table_name: str, parent=None):
        super().__init__(table_name, parent)

        self._table_name = table_name
        self._selected = False

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        self.setFixedSize(178, 68)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_style()

    def setup_connections(self):
        self.clicked.connect(self._emit_clicked)

    def _emit_clicked(self):
        self.clicked_signal.emit(self._table_name)

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
    from PyQt6.QtWidgets import (QApplication,QWidget,QGridLayout,)

    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Table Item Test")
    window.setStyleSheet("background:white;")

    layout = QGridLayout(window)
    layout.setSpacing(15)

    tables = []

    def table_clicked(name):
        for table in tables:
            table.set_selected(table.text() == name)

        print(f"Selected: {name}")

    # Create 8 tables
    for i in range(8):
        table = TableItem(f"Table {i+1}")
        table.clicked_signal.connect(table_clicked)
        tables.append(table)

    # Arrange in 2 columns × 4 rows
    positions = [
        (0, 0), (1, 0), (2, 0), (3, 0),
        (0, 1), (1, 1), (2, 1), (3, 1),
    ]

    for table, (row, col) in zip(tables, positions):
        layout.addWidget(table, row, col)

    window.show()

    sys.exit(app.exec())
