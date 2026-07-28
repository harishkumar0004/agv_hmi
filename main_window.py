"""
main_window.py — The ONLY place that reacts to Controller signals.

Architecture rule:
  - MainWindow listens to Controller.state_changed
  - When state changes, it calls on_exit() on old screen, setCurrentWidget(), on_enter() on new screen
  - Screens NEVER talk to each other directly
  - This file has ZERO business logic — just routing
"""
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton
)

from controller import Controller
from screens import (
    IdleScreen, AssignmentScreen, TransitScreen,
    ArrivedScreen, SettingsScreen
)
from widgets.face_widget import FaceWidget
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FULLSCREEN,
    ARRIVAL_REMINDER_MS, ADMIN_PIN
)


class MainWindow(QMainWindow):
    """
    ┌─────────────────────────────────────────┐
    │  [🤖]  AGV Delivery Bot          [⚙️]  │  ← status bar
    │─────────────────────────────────────────│
    │                                         │
    │         [ ACTIVE SCREEN ]               │  ← QStackedWidget
    │                                         │
    │                                         │
    └─────────────────────────────────────────┘
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
        # Development shortcut
        self.exit_shortcut = QShortcut(QKeySequence("Esc"), self)
        self.exit_shortcut.activated.connect(self.close)

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
        """Build the main layout: status bar + stacked screens."""
        central = QWidget(self)
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        # ═══════ TOP BAR: Status + Settings gear ═══════
        top_bar = QHBoxLayout()

        self.status_label = QLabel("🤖 AGV Ready", self)
        self.status_label.setStyleSheet("color: #888; font-size: 14px;")
        top_bar.addWidget(self.status_label)
        top_bar.addStretch()

        # Small gear icon to enter settings
        self.settings_btn = QPushButton("⚙️", self)
        self.settings_btn.setFixedSize(40, 40)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                font-size: 20px;
                border: none;
            }
            QPushButton:pressed {
                color: #fff;
            }
        """)
        self.settings_btn.clicked.connect(self._on_settings_clicked)
        top_bar.addWidget(self.settings_btn)

        main_layout.addLayout(top_bar)

        # ═══════ STACKED WIDGET: All screens ═══════
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

        # ═══════ PIN OVERLAY (hidden by default) ═══════
        self._setup_pin_overlay()

    def _setup_pin_overlay(self):
        """Modal PIN keypad overlay for settings access."""
        from PyQt5.QtWidgets import QGridLayout, QLineEdit

        self.pin_overlay = QWidget(self.centralWidget())
        self.pin_overlay.setGeometry(200, 100, 400, 400)
        self.pin_overlay.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border: 2px solid #444;
                border-radius: 15px;
            }
        """)
        self.pin_overlay.hide()

        overlay_layout = QVBoxLayout(self.pin_overlay)
        overlay_layout.setAlignment(Qt.AlignCenter)

        pin_title = QLabel("Enter PIN", self.pin_overlay)
        pin_title.setAlignment(Qt.AlignCenter)
        pin_title.setStyleSheet("font-size: 20px; color: #fff;")
        overlay_layout.addWidget(pin_title)

        self.pin_display = QLineEdit(self.pin_overlay)
        self.pin_display.setAlignment(Qt.AlignCenter)
        self.pin_display.setEchoMode(QLineEdit.Password)
        self.pin_display.setReadOnly(True)
        self.pin_display.setStyleSheet("""
            QLineEdit {
                font-size: 24px;
                color: #fff;
                background: #333;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        overlay_layout.addWidget(self.pin_display)

        # PIN keypad grid
        keypad = QGridLayout()
        keypad.setSpacing(8)
        digits = [
            '1', '2', '3',
            '4', '5', '6',
            '7', '8', '9',
            'C', '0', '✓'
        ]
        for i, digit in enumerate(digits):
            btn = QPushButton(digit, self.pin_overlay)
            btn.setFixedSize(80, 60)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #333;
                    color: white;
                    font-size: 20px;
                    border-radius: 8px;
                }
                QPushButton:pressed {
                    background-color: #555;
                }
            """)
            if digit == 'C':
                btn.clicked.connect(self._pin_clear)
            elif digit == '✓':
                btn.clicked.connect(self._pin_verify)
            else:
                btn.clicked.connect(lambda checked, d=digit: self._pin_digit(d))
            keypad.addWidget(btn, i // 3, i % 3)

        overlay_layout.addLayout(keypad)

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

        # Update status bar
        self.status_label.setText(f"State: {new_state}")

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

    def _on_settings_clicked(self):
        """Gear icon tapped — show PIN overlay."""
        self._pin_clear()
        self.pin_overlay.show()
        self.pin_overlay.raise_()

    def _pin_digit(self, digit):
        """PIN keypad digit pressed."""
        current = self.pin_display.text()
        if len(current) < 6:
            self.pin_display.setText(current + digit)

    def _pin_clear(self):
        """Clear PIN entry."""
        self.pin_display.clear()

    def _pin_verify(self):
        """Check PIN and enter settings if correct."""
        if self.pin_display.text() == ADMIN_PIN:
            self.pin_overlay.hide()
            self._pin_clear()
            self.controller.to_settings()
        else:
            self.pin_display.setText("WRONG")
            QTimer.singleShot(800, self._pin_clear)


# Need QLabel import
from PyQt5.QtWidgets import QLabel
