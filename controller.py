"""
controller.py — The single source of truth for all AGV state.

This is a plain QObject (not a QWidget). It owns the delivery state machine
and emits signals when things change. NO UI CODE HERE — just state + signals.

Key concept: The Controller NEVER imports anything from screens/ or widgets/.
It only knows about itself. Screens listen to Controller signals.
"""

from PyQt5.QtCore import QObject, pyqtSignal

from config import RACK_COUNT, TABLE_COUNT


class Controller(QObject):
    """
    ┌─────────────────────────────────────────────────────────┐
    │  STATE MACHINE — these are the ONLY valid states        │
    │                                                         │
    │  idle        → waiting at dock, face blinking           │
    │  assignment  → waiter selecting racks & tables          │
    │  navigating  → robot moving to a table                  │
    │  arrived     → at table, waiting for customer pickup    │
    │  returning   → heading back to dock                   │
    │  settings    → admin config screen (separate flow)      │
    └─────────────────────────────────────────────────────────┘
    """

    # ═══════════════════════════════════════════════════════
    # SIGNALS — these are how the Controller talks to the UI
    # ═══════════════════════════════════════════════════════
    state_changed = pyqtSignal(str)
    mood_changed = pyqtSignal(str)
    stops_updated = pyqtSignal(list)
    current_stop_changed = pyqtSignal(dict)

    # ═══════════════════════════════════════════════════════
    # CONSTRUCTOR
    # ═══════════════════════════════════════════════════════
    def __init__(self, parent=None):
        super().__init__(parent)

        self._state = "idle"
        self._mood = "neutral"
        self._stops = []
        self._current_stop_index = 0
        self._pre_settings_state = "idle"  # remember where we were before settings

    # ═══════════════════════════════════════════════════════
    # PROPERTIES
    # ═══════════════════════════════════════════════════════
    @property
    def state(self):
        return self._state

    @property
    def mood(self):
        return self._mood

    @property
    def stops(self):
        return list(self._stops)

    @property
    def current_stop(self):
        if 0 <= self._current_stop_index < len(self._stops):
            return self._stops[self._current_stop_index]
        return None

    @property
    def has_more_stops(self):
        return self._current_stop_index < len(self._stops) - 1

    # ═══════════════════════════════════════════════════════
    # STATE TRANSITION METHODS
    # ═══════════════════════════════════════════════════════

    def to_idle(self):
        """Reset everything and go back to idle (dock detected)."""
        self._state = "idle"
        self._stops = []
        self._current_stop_index = 0
        self._set_mood("neutral")
        self.stops_updated.emit(self._stops)
        self.state_changed.emit("idle")

    def to_assignment(self):
        """Waiter long-pressed the face — open assignment screen."""
        self._state = "assignment"
        self._stops = []
        self._current_stop_index = 0
        self.stops_updated.emit(self._stops)
        self.state_changed.emit("assignment")

    def add_stop(self, rack, table):
        """Add a rack→table pair to the delivery queue."""
        stop = {"rack": rack, "table": table}
        self._stops.append(stop)
        self.stops_updated.emit(self._stops)

    def remove_stop(self, rack, table):
        """Remove a specific rack→table pair."""
        self._stops = [
            s for s in self._stops
            if not (s["rack"] == rack and s["table"] == table)
        ]
        self.stops_updated.emit(self._stops)

    def start_delivery(self):
        """Waiter tapped "Start" — begin navigating to first stop."""
        if not self._stops:
            return
        self._current_stop_index = 0
        self._state = "navigating"
        self._set_mood("focused")
        self.current_stop_changed.emit(self.current_stop)
        self.state_changed.emit("navigating")

    def report_arrived(self):
        """ESP32 says we've arrived at the current table."""
        self._state = "arrived"
        self._set_mood("happy")
        self.state_changed.emit("arrived")

    def confirm_pickup(self):
        """Customer tapped "I'm done" — move to next stop or return home."""
        if self.has_more_stops:
            self._current_stop_index += 1
            self._state = "navigating"
            self._set_mood("focused")
            self.current_stop_changed.emit(self.current_stop)
            self.state_changed.emit("navigating")
        else:
            self._state = "returning"
            self._set_mood("content")
            self.state_changed.emit("returning")

    def report_docked(self):
        """ESP32 says we're back at the dock."""
        self.to_idle()

    def to_settings(self):
        """Open settings (gear icon tapped, PIN already verified)."""
        self._pre_settings_state = self._state
        self._state = "settings"
        self.state_changed.emit("settings")

    def return_from_settings(self):
        """Back button pressed in settings — return to previous state."""
        if self._pre_settings_state == "idle" or not self._stops:
            self.to_idle()
        else:
            self._state = self._pre_settings_state
            self.state_changed.emit(self._state)

    def set_mood(self, mood):
        """External override (e.g., timer wants 'worried' after 45s)."""
        self._set_mood(mood)

    # ═══════════════════════════════════════════════════════
    # PRIVATE HELPERS
    # ═══════════════════════════════════════════════════════
    def _set_mood(self, mood):
        if self._mood != mood:
            self._mood = mood
            self.mood_changed.emit(mood)
