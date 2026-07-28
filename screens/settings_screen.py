"""
settings_screen.py — Admin configuration screen.

Reached from AssignmentScreen via gear icon → PIN.
Contains ONLY:
  - Volume slider
  - Brightness slider
  - Rack / Table count config
  - Shutdown button
  - Return-to-desktop button
  - Back button

No Wi-Fi config panel (stub), no diagnostics, no restart app.
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
    │  Volume:     [━━━━━●━━━]                │
    │  Brightness: [━━━━●━━━━]                │
    │                                         │
    │  Racks: 3    Tables: 20    [Change]     │
    │                                         │
    │  [Shutdown]  [Return to Desktop]        │
    └─────────────────────────────────────────┘
    """

    back_pressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)

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

        # --- Volume ---
        layout.addWidget(self._make_slider_row("Volume:", 70))

        # --- Brightness ---
        layout.addWidget(self._make_slider_row("Brightness:", 50))

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
        actions_row = QHBoxLayout()

        shutdown_btn = QPushButton("⏻ Shutdown", self)
        shutdown_btn.setFixedHeight(50)
        shutdown_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }
        """)
        actions_row.addWidget(shutdown_btn)

        desktop_btn = QPushButton("🖥️ Return to Desktop", self)
        desktop_btn.setFixedHeight(50)
        desktop_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                font-size: 16px;
                border-radius: 8px;
            }
        """)
        actions_row.addWidget(desktop_btn)

        layout.addLayout(actions_row)
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
