"""
idle_screen.py — The default screen when robot is docked and waiting.

Contains ONLY:
  - Large FaceWidget (fullscreen, centered)

No top bar, no status text, no icons, no branding visible.
The face IS the entire screen — tap for fun, long-press to enter assignment.
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from widgets.face_widget import FaceWidget


class IdleScreen(QWidget):
    """
    ┌─────────────────────────────┐
    │                             │
    │                             │
    │         [  FACE  ]          │  ← tap = fun reaction
    │         (fullscreen)        │  ← hold 2.5s = enter assignment
    │                             │
    │                             │
    └─────────────────────────────┘
    """

    request_assignment = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Build the idle screen — face only, edge to edge."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        # --- The face (ONLY interactive element, fills the screen) ---
        self.face = FaceWidget(size=280, parent=self)
        self.face.tapped.connect(self._on_face_tapped)
        self.face.long_pressed.connect(self._on_face_long_pressed)
        layout.addWidget(self.face, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    # ═══════════════════════════════════════════════════════
    # PUBLIC API (called by MainWindow)
    # ═══════════════════════════════════════════════════════

    def on_enter(self):
        """Called when this screen becomes visible."""
        self.face.set_mood("neutral")

    def on_exit(self):
        """Called when leaving this screen."""
        pass

    # ═══════════════════════════════════════════════════════
    # PRIVATE SLOTS
    # ═══════════════════════════════════════════════════════

    def _on_face_tapped(self):
        """Short tap — FaceWidget handles its own surprised animation."""
        pass

    def _on_face_long_pressed(self):
        """Long press — waiter wants to assign deliveries."""
        self.request_assignment.emit()
