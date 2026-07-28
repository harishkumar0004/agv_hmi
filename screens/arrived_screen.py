"""
arrived_screen.py — Customer pickup screen.

Contains ONLY:
  - Greeting message ("Your order has arrived — please collect it")
  - FaceWidget (happy mood)
  - "Done" button
  - Reminder banner (hidden, shown after 45s timeout)

No status bar, no rack numbers exposed to customer (internal detail).
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

from widgets.face_widget import FaceWidget


class ArrivedScreen(QWidget):
    """
    ┌─────────────────────────────┐
    │                             │
    │  Your order has arrived     │
    │  Please collect it          │
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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(25)

        # --- Greeting message ---
        self.greeting_label = QLabel("Your order has arrived", self)
        self.greeting_label.setAlignment(Qt.AlignCenter)
        self.greeting_label.setStyleSheet("""
            QLabel {
                color: #fff;
                font-size: 28px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.greeting_label)

        self.sub_label = QLabel("Please collect it", self)
        self.sub_label.setAlignment(Qt.AlignCenter)
        self.sub_label.setStyleSheet("""
            QLabel {
                color: #aaa;
                font-size: 20px;
            }
        """)
        layout.addWidget(self.sub_label)

        # --- Happy face ---
        self.face = FaceWidget(size=180, parent=self)
        layout.addWidget(self.face, alignment=Qt.AlignCenter)

        # --- Confirm button ---
        self.confirm_btn = QPushButton("✓ I'm Done", self)
        self.confirm_btn.setFixedSize(220, 70)
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
