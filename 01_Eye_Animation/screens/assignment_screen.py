from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .base_screen import BaseScreen
from widgets.top_bar import TopBar
from widgets.rack_item import RackItem
from widgets.table_item import TableItem
import sys

class AssignmentScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.showFullScreen()
        self.resize(1024, 600)
        self.rack_buttons = []
        self.table_buttons = []
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            AssignmentScreen {
                background: #f4f7fb;
                font-family: Arial;
            }
            QLabel#sectionTitle {
                color: #111827;
                font-size: 24px;
                font-weight: 700;
            }
            QLabel#sectionHint {
                color: #667085;
                font-size: 14px;
            }
            QFrame#rackPanel,
            QFrame#tablePanel {
                background: #ffffff;
                border: 1px solid #dfe5ed;
                border-radius: 8px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.topbar = TopBar()
        main_layout.addWidget(self.topbar)

        content = QWidget()
        main_layout.addWidget(content, 1)

        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(36, 30, 36, 34)
        content_layout.setSpacing(28)

        left_panel = self.create_rack_panel()
        right_panel = self.create_table_panel()

        content_layout.addWidget(left_panel, 0)
        content_layout.addWidget(right_panel, 1)

        if self.rack_buttons:
            self._select_rack(self.rack_buttons[0].text())

    def create_rack_panel(self):
        panel = QFrame()
        panel.setObjectName("rackPanel")
        panel.setFixedWidth(250)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("Racks")
        title.setObjectName("sectionTitle")
        hint = QLabel("Select pickup rack")
        hint.setObjectName("sectionHint")

        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addSpacing(10)

        for name in ("Rack 1", "Rack 2"):
            rack = RackItem(name)
            rack.clicked_signal.connect(self._select_rack)
            self.rack_buttons.append(rack)
            layout.addWidget(rack)

        layout.addStretch(1)
        return panel

    def create_table_panel(self):
        panel = QFrame()
        panel.setObjectName("tablePanel")
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(20)

        title = QLabel("Tables")
        title.setObjectName("sectionTitle")
        hint = QLabel("Select delivery table")
        hint.setObjectName("sectionHint")

        header = QVBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(4)
        header.addWidget(title)
        header.addWidget(hint)

        layout.addLayout(header)

        grid = QGridLayout()
        grid.setContentsMargins(0, 8, 0, 0)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(16)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        for i in range(8):
            table = TableItem(f"Table {i+1}")
            table.clicked_signal.connect(self._select_table)
            self.table_buttons.append(table)

            row = i % 4
            col = i // 4
            grid.addWidget(table, row, col, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(grid, 1)
        return panel

    def _select_rack(self, rack_name):
        for rack in self.rack_buttons:
            rack.set_selected(rack.text() == rack_name)

    def _select_table(self, table_name):
        for table in self.table_buttons:
            table.set_selected(table.text() == table_name)

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = AssignmentScreen()

    window.show()

    sys.exit(app.exec())
