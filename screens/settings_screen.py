"""
settings_screen.py — Admin configuration screen.

Reached via gear icon → PIN keypad overlay → this screen.
Contains placeholder panels for future config options.
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider
)


class SettingsScreen(QWidget):
    """
    ┌─────────────────────────────────────────┐
    │  ⚙️ Settings                [Back]      │
    │                                         │
    │  Wi-Fi: [Not connected]    [Configure]  │
    │  Brightness: [━━━━●━━━━]                │
    │  Volume:     [━━━━━●━━━]                │
    │                                         │
    │  Racks: 3    Tables: 20    [Change]     │
    │                                         │
    │  [Diagnostics]  [Restart App]           │
    │  [Restart Pi]   [Shutdown]              │
    │  [Exit to Desktop]                      │
    └─────────────────────────────────────────┘
    """

    back_pressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(15)

        # --- Header ---
        header = QHBoxLayout()
        title = QLabel("⚙️ Settings", self)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #fff;")
        header.addWidget(title)
        header.addStretch()

        back_btn = QPushButton("← Back", self)
        back_btn.setFixedSize(100, 40)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #555;
                color: white;
                font-size: 14px;
                border-radius: 8px;
            }
        """)
        back_btn.clicked.connect(self.back_pressed.emit)
        header.addWidget(back_btn)
        layout.addLayout(header)

        # --- Wi-Fi ---
        wifi_row = QHBoxLayout()
        wifi_label = QLabel("Wi-Fi:", self)
        wifi_label.setStyleSheet("color: #ccc; font-size: 16px;")
        wifi_row.addWidget(wifi_label)

        self.wifi_status = QLabel("Not connected", self)
        self.wifi_status.setStyleSheet("color: #e74c3c; font-size: 16px;")
        wifi_row.addWidget(self.wifi_status)
        wifi_row.addStretch()

        wifi_btn = QPushButton("Configure", self)
        wifi_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
            }
        """)
        wifi_row.addWidget(wifi_btn)
        layout.addLayout(wifi_row)

        # --- Brightness ---
        layout.addWidget(self._make_slider_row("Brightness:", 50))

        # --- Volume ---
        layout.addWidget(self._make_slider_row("Volume:", 70))

        # --- Rack/Table count ---
        counts_row = QHBoxLayout()
        counts_row.addWidget(QLabel("Racks: 3  |  Tables: 20", self))
        counts_row.addStretch()
        change_btn = QPushButton("Change", self)
        change_btn.setStyleSheet("""
            QPushButton {
                background-color: #555;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
            }
        """)
        counts_row.addWidget(change_btn)
        layout.addLayout(counts_row)

        # --- Action buttons ---
        actions_grid = QHBoxLayout()
        for label, color in [
            ("Diagnostics", "#9b59b6"),
            ("Restart App", "#f39c12"),
            ("Restart Pi", "#e67e22"),
            ("Shutdown", "#e74c3c"),
        ]:
            btn = QPushButton(label, self)
            btn.setFixedHeight(50)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 8px;
                }}
            """)
            actions_grid.addWidget(btn)
        layout.addLayout(actions_grid)

        # --- Exit to desktop ---
        exit_btn = QPushButton("🖥️ Exit to Desktop", self)
        exit_btn.setFixedHeight(50)
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                font-size: 16px;
                border-radius: 8px;
            }
        """)
        layout.addWidget(exit_btn)

        layout.addStretch()
        self.setLayout(layout)

    def _make_slider_row(self, label_text, default_value):
        """Helper to create a labeled slider row."""
        row = QHBoxLayout()
        label = QLabel(label_text, self)
        label.setFixedWidth(100)
        label.setStyleSheet("color: #ccc; font-size: 16px;")
        row.addWidget(label)

        slider = QSlider(Qt.Horizontal, self)
        slider.setRange(0, 100)
        slider.setValue(default_value)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: #444;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                width: 20px;
                background: #3498db;
                border-radius: 10px;
            }
        """)
        row.addWidget(slider)

        value_label = QLabel(f"{default_value}%", self)
        value_label.setFixedWidth(50)
        value_label.setStyleSheet("color: #888;")
        row.addWidget(value_label)

        container = QWidget(self)
        container.setLayout(row)
        return container

    # ═══════════════════════════════════════════════════════
    # PUBLIC API
    # ═══════════════════════════════════════════════════════

    def on_enter(self):
        pass

    def on_exit(self):
        pass
