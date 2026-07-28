"""
transit_screen.py — Shows current destination while robot is moving.

Contains:
  - Destination label ("Heading to Table X")
  - Small face widget (focused mood)
  - Stops remaining indicator (if multi-stop delivery)
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

from widgets.face_widget import FaceWidget


class TransitScreen(QWidget):
    """
    ┌─────────────────────────────┐
    │                             │
    │    Heading to Table 5       │
    │                             │
    │         [😐]                │  ← focused face
    │                             │
    │    2 more stops after this  │
    │                             │
    └─────────────────────────────┘
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # --- Destination heading ---
        self.destination_label = QLabel("Heading to...", self)
        self.destination_label.setAlignment(Qt.AlignCenter)
        self.destination_label.setStyleSheet("""
            QLabel {
                color: #fff;
                font-size: 32px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.destination_label)

        # --- Focused face ---
        self.face = FaceWidget(size=150, parent=self)
        layout.addWidget(self.face, alignment=Qt.AlignCenter)

        # --- Stops remaining ---
        self.stops_label = QLabel("", self)
        self.stops_label.setAlignment(Qt.AlignCenter)
        self.stops_label.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 16px;
            }
        """)
        layout.addWidget(self.stops_label)

        self.setLayout(layout)

    # ═══════════════════════════════════════════════════════
    # PUBLIC API
    # ═══════════════════════════════════════════════════════

    def on_enter(self):
        """Called when this screen becomes visible."""
        self.face.set_mood("focused")

    def on_exit(self):
        """Called when leaving this screen."""
        pass

    def set_destination(self, stop, total_stops, current_index):
        """
        Update display for current stop.

        Args:
            stop: dict with "rack" and "table" keys
            total_stops: total number of stops in delivery
            current_index: 0-based index of current stop
        """
        self.destination_label.setText(
            f"Heading to Table {stop['table']}"
        )

        remaining = total_stops - current_index - 1
        if remaining > 0:
            self.stops_label.setText(
                f"{remaining} more stop{'s' if remaining > 1 else ''} after this"
            )
            self.stops_label.show()
        else:
            self.stops_label.hide()
