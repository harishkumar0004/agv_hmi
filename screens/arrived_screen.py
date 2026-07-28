"""
arrived_screen.py — Customer pickup screen.

Contains:
  - Pickup instruction ("Please collect from Rack N")
  - Small happy face
  - "I'm done" confirm button
  - Reminder banner (hidden, shown after 45s timeout)

The 45s timer is managed by MainWindow (not this screen) so that
screen transitions don't accidentally kill the timer.
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

from widgets.face_widget import FaceWidget


class ArrivedScreen(QWidget):
    """
    ┌─────────────────────────────┐
    │                             │
    │  Please collect from Rack 2 │
    │                             │
    │         [😊]                │
    │                             │
    │    [  ✓ I'm Done  ]         │
    │                             │
    │  ⚠️ Please don't forget!   │  ← appears after 45s
    │                             │
    └─────────────────────────────┘
    """

    confirmed = pyqtSignal()   # "I'm done" button tapped

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # --- Pickup instruction ---
        self.pickup_label = QLabel("Please collect your item", self)
        self.pickup_label.setAlignment(Qt.AlignCenter)
        self.pickup_label.setStyleSheet("""
            QLabel {
                color: #fff;
                font-size: 28px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.pickup_label)

        # --- Happy face ---
        self.face = FaceWidget(size=150, parent=self)
        layout.addWidget(self.face, alignment=Qt.AlignCenter)

        # --- Confirm button ---
        self.confirm_btn = QPushButton("✓ I'm Done", self)
        self.confirm_btn.setFixedSize(200, 70)
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-size: 22px;
                font-weight: bold;
                border-radius: 15px;
            }
            QPushButton:pressed {
                background-color: #27ae60;
            }
        """)
        self.confirm_btn.clicked.connect(self._on_confirm)
        layout.addWidget(self.confirm_btn, alignment=Qt.AlignCenter)

        # --- Reminder banner (hidden by default) ---
        self.reminder_banner = QLabel("⚠️ Please don't forget to collect your item!", self)
        self.reminder_banner.setAlignment(Qt.AlignCenter)
        self.reminder_banner.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 18px;
                font-weight: bold;
                background-color: #2c0000;
                padding: 15px;
                border-radius: 10px;
                border: 2px solid #e74c3c;
            }
        """)
        self.reminder_banner.hide()
        layout.addWidget(self.reminder_banner)

        self.setLayout(layout)

    # ═══════════════════════════════════════════════════════
    # PUBLIC API
    # ═══════════════════════════════════════════════════════

    def on_enter(self):
        """Reset banner, set happy face."""
        self.reminder_banner.hide()
        self.face.set_mood("happy")

    def on_exit(self):
        """Clean up when leaving."""
        self.reminder_banner.hide()

    def set_rack(self, rack_number):
        """Update the pickup instruction with rack number."""
        self.pickup_label.setText(f"Please collect from Rack {rack_number}")

    def show_reminder(self):
        """Show the worry banner (called by MainWindow after 45s)."""
        self.reminder_banner.show()
        self.face.set_mood("worried")

    # ═══════════════════════════════════════════════════════
    # PRIVATE SLOTS
    # ═══════════════════════════════════════════════════════

    def _on_confirm(self):
        """Customer confirmed pickup."""
        self.confirmed.emit()
