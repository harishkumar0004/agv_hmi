"""
face_widget.py — The robot's face, reused across multiple screens.

This widget handles:
  - Tap vs long-press gesture detection
  - Mood-based pixmap swapping (neutral, happy, focused, worried, content)
  - Idle blink animation (when mood is "neutral")

It emits signals so the SCREEN (not this widget) decides what to do.
"""

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap

from config import LONG_PRESS_MS, IDLE_BLINK_INTERVAL_MS


class FaceWidget(QWidget):
    """
    A large tappable face that distinguishes short tap from long hold.

    Signals:
        tapped()      — quick press-and-release (fun reaction for kids)
        long_pressed() — held for LONG_PRESS_MS (enter assignment mode)
    """

    tapped = pyqtSignal()       # short tap
    long_pressed = pyqtSignal()  # long hold

    def __init__(self, size=200, parent=None):
        super().__init__(parent)

        self._size = size
        self._mood = "neutral"
        self._is_pressed = False
        self._long_press_fired = False

        # --- Build UI ---
        self._setup_ui()

        # --- Timers ---
        # Timer for detecting long press
        self._long_press_timer = QTimer(self)
        self._long_press_timer.setSingleShot(True)
        self._long_press_timer.timeout.connect(self._on_long_press)

        # Timer for idle blinking (only when mood == "neutral")
        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._on_blink)

        # Start blink loop if we're neutral
        self._update_blink_timer()

    def _setup_ui(self):
        """Create the label that displays the face image."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        self._label = QLabel(self)
        self._label.setFixedSize(self._size, self._size)
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                border-radius: %dpx;
                border: 3px solid #444;
            }
        """ % (self._size // 2))

        # Placeholder text until we have real face images
        self._label.setText("🤖")
        font = self._label.font()
        font.setPointSize(self._size // 4)
        self._label.setFont(font)

        layout.addWidget(self._label)
        self.setLayout(layout)

        # Enable mouse tracking for press/hold detection
        self.setMouseTracking(True)
        self._label.setMouseTracking(True)

    # ═══════════════════════════════════════════════════════
    # PUBLIC API
    # ═══════════════════════════════════════════════════════

    def set_mood(self, mood):
        """
        Change the face mood. Valid moods:
        "neutral", "happy", "focused", "worried", "content", "surprised"
        """
        self._mood = mood
        self._update_face_display()
        self._update_blink_timer()

    # ═══════════════════════════════════════════════════════
    # MOUSE EVENTS — gesture detection
    # ═══════════════════════════════════════════════════════

    def mousePressEvent(self, event):
        """Finger/click went DOWN — start measuring hold time."""
        if event.button() == Qt.LeftButton:
            self._is_pressed = True
            self._long_press_fired = False
            self._long_press_timer.start(LONG_PRESS_MS)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Finger/click went UP — was it a tap or did long-press already fire?"""
        if event.button() == Qt.LeftButton:
            self._is_pressed = False
            self._long_press_timer.stop()

            if not self._long_press_fired:
                # Released BEFORE timer fired → it's a short tap
                self._on_tap()

            self._long_press_fired = False
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        """If finger drags off the widget, cancel the long-press."""
        if self._is_pressed and not self.rect().contains(event.pos()):
            self._is_pressed = False
            self._long_press_timer.stop()
            self._long_press_fired = False
        super().mouseMoveEvent(event)

    # ═══════════════════════════════════════════════════════
    # PRIVATE SLOTS / HANDLERS
    # ═══════════════════════════════════════════════════════

    def _on_tap(self):
        """Short tap detected — brief surprised reaction, then back to mood."""
        self.tapped.emit()
        # Brief "surprised" flash
        old_mood = self._mood
        self._label.setText("😮")
        QTimer.singleShot(300, lambda: self.set_mood(old_mood))

    def _on_long_press(self):
        """Long press threshold reached — fire the signal."""
        self._long_press_fired = True
        self.long_pressed.emit()

    def _on_blink(self):
        """Idle blink animation — close eyes briefly."""
        if self._mood == "neutral":
            self._label.setText("😑")  # eyes closed
            QTimer.singleShot(200, lambda: self._label.setText("🤖"))

    # ═══════════════════════════════════════════════════════
    # PRIVATE HELPERS
    # ═══════════════════════════════════════════════════════

    def _update_face_display(self):
        """Update the label text based on current mood (placeholder emojis)."""
        mood_map = {
            "neutral":   "🤖",
            "happy":     "😊",
            "focused":   "😐",
            "worried":   "😟",
            "content":   "😌",
            "surprised": "😮",
            "concerned": "😰",
        }
        self._label.setText(mood_map.get(self._mood, "🤖"))

    def _update_blink_timer(self):
        """Start/stop blink timer based on whether we're in neutral mood."""
        if self._mood == "neutral":
            if not self._blink_timer.isActive():
                self._blink_timer.start(IDLE_BLINK_INTERVAL_MS)
        else:
            if self._blink_timer.isActive():
                self._blink_timer.stop()
