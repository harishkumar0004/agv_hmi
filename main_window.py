"""
main_window.py — The ONLY place that reacts to Controller signals.

Architecture rule:
  - MainWindow listens to Controller.state_changed
  - When state changes, it calls on_exit() on old screen, setCurrentWidget(), on_enter() on new screen
  - Screens NEVER talk to each other directly
  - This file has ZERO business logic — just routing
  - NO global top bar — each screen owns its own chrome (or none at all)
"""

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QStackedWidget
)

from controller import Controller
from screens import (
    IdleScreen, AssignmentScreen, TransitScreen,
    ArrivedScreen, SettingsScreen
)
from widgets.face_widget import FaceWidget
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FULLSCREEN,
    ARRIVAL_REMINDER_MS
)


class MainWindow(QMainWindow):
    """
    ┌─────────────────────────────────────────┐
    │                                         │
    │         [ ACTIVE SCREEN ]               │  ← QStackedWidget (full area)
    │                                         │
    │                                         │
    └─────────────────────────────────────────┘

    No global top bar. Idle screen is FaceWidget only, fullscreen.
    Settings gear lives on AssignmentScreen (staff-facing).
    """

    def __init__(self, controller: Controller, parent=None):
        super().__init__(parent)

        self.controller = controller

        # --- Track all FaceWidget instances for mood broadcasts ---
        self.all_face_widgets = []

        self._setup_window()
        self._setup_ui()
        self._connect_signals()
        self._setup_reminder_timer()

    def _setup_window(self):
        """Configure window geometry and appearance."""
        self.setWindowTitle("AGV Delivery HMI")
        self.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

        if FULLSCREEN:
            self.showFullScreen()

        # Dark theme background
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QWidget {
                background-color: #121212;
            }
        """)

    def _setup_ui(self):
        """Build the main layout: just the stacked screens, edge to edge."""
        central = QWidget(self)
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ═══════ STACKED WIDGET: All screens (fills entire window) ═══════
        self.stack = QStackedWidget(self)

        # Create each screen
        self.idle_screen = IdleScreen(self)
        self.assignment_screen = AssignmentScreen(self)
        self.transit_screen = TransitScreen(self)
        self.arrived_screen = ArrivedScreen(self)
        self.settings_screen = SettingsScreen(self)

        # Add to stack
        self.stack.addWidget(self.idle_screen)       # index 0
        self.stack.addWidget(self.assignment_screen) # index 1
        self.stack.addWidget(self.transit_screen)    # index 2
        self.stack.addWidget(self.arrived_screen)    # index 3
        self.stack.addWidget(self.settings_screen)   # index 4

        # Map state names to screen widgets
        self.pages = {
            "idle": self.idle_screen,
            "assignment": self.assignment_screen,
            "navigating": self.transit_screen,
            "arrived": self.arrived_screen,
            "returning": self.transit_screen,  # reuse transit screen
            "settings": self.settings_screen,
        }

        # Collect all FaceWidgets for mood broadcasting
        self.all_face_widgets = [
            self.idle_screen.face,
            self.transit_screen.face,
            self.arrived_screen.face,
        ]

        main_layout.addWidget(self.stack)

    def _setup_reminder_timer(self):
        """45s timer for arrival reminder (worried face + banner)."""
        self._reminder_timer = QTimer(self)
        self._reminder_timer.setSingleShot(True)
        self._reminder_timer.timeout.connect(self._on_reminder_timeout)

    def _connect_signals(self):
        """Wire Controller signals to MainWindow slots."""

        # Controller → Screen switching
        self.controller.state_changed.connect(self.on_state_changed)

        # Controller → Mood broadcast to ALL face widgets
        self.controller.mood_changed.connect(self.on_mood_changed)

        # Controller → Transit screen updates
        self.controller.current_stop_changed.connect(self._on_current_stop_changed)

        # Screen → Controller (user actions)
        self.idle_screen.request_assignment.connect(
            self.controller.to_assignment
        )
        self.assignment_screen.start_delivery.connect(
            self.controller.start_delivery
        )
        self.assignment_screen.assignment_cancelled.connect(
            self.controller.to_idle
        )
        self.assignment_screen.request_settings.connect(
            self.controller.to_settings
        )
        self.arrived_screen.confirmed.connect(
            self.controller.confirm_pickup
        )
        self.settings_screen.back_pressed.connect(
            self.controller.return_from_settings
        )

    # ═══════════════════════════════════════════════════════
    # SLOTS — React to Controller signals
    # ═══════════════════════════════════════════════════════

    def on_state_changed(self, new_state):
        """
        THE CORE ROUTER.

        1. Call on_exit() on the CURRENT screen (cleanup)
        2. Switch to the new screen via QStackedWidget
        3. Call on_enter() on the NEW screen (setup)
        """
        current = self.stack.currentWidget()
        if current and hasattr(current, 'on_exit'):
            current.on_exit()

        # Special handling for "returning" — reuse transit screen
        if new_state == "returning":
            self.transit_screen.destination_label.setText("Heading back to dock...")
            self.transit_screen.stops_label.hide()

        # Switch page
        if new_state in self.pages:
            self.stack.setCurrentWidget(self.pages[new_state])

        new_screen = self.stack.currentWidget()
        if new_screen and hasattr(new_screen, 'on_enter'):
            new_screen.on_enter()

        # Debug: log to console instead of screen
        print(f"[DEBUG] State changed to: {new_state}")

        # Handle arrival reminder timer
        if new_state == "arrived":
            self._reminder_timer.start(ARRIVAL_REMINDER_MS)
        else:
            self._reminder_timer.stop()

    def on_mood_changed(self, mood):
        """Broadcast mood change to every FaceWidget instance."""
        for face in self.all_face_widgets:
            face.set_mood(mood)

    # ═══════════════════════════════════════════════════════
    # PRIVATE SLOTS
    # ═══════════════════════════════════════════════════════

    def _on_current_stop_changed(self, stop):
        """Controller moved to next stop — update transit display."""
        self.transit_screen.set_destination(
            stop,
            len(self.controller.stops),
            self.controller._current_stop_index
        )

    def _on_reminder_timeout(self):
        """45s passed since arrival — show reminder banner."""
        if self.controller.state == "arrived":
            self.arrived_screen.show_reminder()
            self.controller.set_mood("worried")
