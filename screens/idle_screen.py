"""
idle_screen.py — The default screen when robot is docked and waiting.

Contains:
  - Large FaceWidget (tap for fun, long-press to enter assignment)
  - Optional branding label

Signals:
    request_assignment() — emitted when face is long-pressed
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)

from widgets.face_widget import FaceWidget


class IdleScreen(QWidget):
    """
    ┌─────────────────────────────┐
    │                             │
    │         [  FACE  ]          │  ← tap = fun reaction
    │         (large)             │  ← hold 2.5s = enter assignment
    │                             │
    │      AGV Delivery Bot       │
    │                             │
    └─────────────────────────────┘
    """

    request_assignment = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Build the idle screen layout."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # --- The face (main interactive element) ---
        self.face = FaceWidget(size=250, parent=self)
        self.face.tapped.connect(self._on_face_tapped)
        self.face.long_pressed.connect(self._on_face_long_pressed)
        layout.addWidget(self.face, alignment=Qt.AlignCenter)

        # --- Branding / status label ---
        self.branding = QLabel("AGV Delivery System", self)
        self.branding.setAlignment(Qt.AlignCenter)
        self.branding.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.branding)

        # --- Hint text ---
        self.hint = QLabel("Long-press the face to start delivery", self)
        self.hint.setAlignment(Qt.AlignCenter)
        self.hint.setStyleSheet("""
            QLabel {
                color: #555;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.hint)

        self.setLayout(layout)

    # ═══════════════════════════════════════════════════════
    # PUBLIC API (called by MainWindow)
    # ═══════════════════════════════════════════════════════

    def on_enter(self):
        """Called when this screen becomes visible."""
        self.face.set_mood("neutral")

    def on_exit(self):
        """Called when leaving this screen."""
        pass  # nothing to clean up

    # ═══════════════════════════════════════════════════════
    # PRIVATE SLOTS
    # ═══════════════════════════════════════════════════════

    def _on_face_tapped(self):
        """Short tap — just a fun reaction, nothing else."""
        pass  # FaceWidget handles its own surprised animation

    def _on_face_long_pressed(self):
        """Long press — waiter wants to assign deliveries."""
        self.request_assignment.emit()
