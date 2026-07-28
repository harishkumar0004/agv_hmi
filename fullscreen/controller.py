"""Controller: owns the delivery task state machine.

This is the single source of truth for what the robot is doing.
Screens listen to its signals and update themselves -- they never
invent or guess state on their own, and never talk to each other
directly.

States: idle -> assigned -> navigating -> arrived -> (navigating again
if more stops, else) returning -> idle.
"""
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

import fullscreen.config


class Controller(QObject):
    # "idle" | "assigned" | "navigating" | "arrived" | "returning"
    state_changed = pyqtSignal(str)

    # "neutral" | "happy" | "focused" | "worried" | "content" | "concerned" | "surprised"
    mood_changed = pyqtSignal(str)

    # list of {"rack": int, "table": int}
    stops_updated = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.state = "idle"
        self.stops = []
        self.current_stop_index = 0

        self._arrived_timer = QTimer(singleShot=True)
        self._arrived_timer.timeout.connect(self._on_arrived_timeout)

    # ---- events coming FROM the display ----

    def assign_stops(self, stops):
        """Called by AssignmentScreen once the waiter has picked rack/table pairs."""
        self.stops = stops
        self.current_stop_index = 0
        self._set_state("assigned")
        self.stops_updated.emit(self.stops)

    def start_delivery(self):
        """Called when the waiter taps 'Start delivery'."""
        self._set_state("navigating")
        self.mood_changed.emit("focused")
        self._send_goto_current_stop()

    def confirm_pickup(self):
        """Called when the customer taps 'I'm done' on the Arrived screen."""
        self._arrived_timer.stop()
        self.current_stop_index += 1
        if self.current_stop_index < len(self.stops):
            self._set_state("navigating")
            self.mood_changed.emit("focused")
            self._send_goto_current_stop()
        else:
            self._set_state("returning")
            self.mood_changed.emit("content")
            self._send_return_home()

    # ---- events coming FROM the ESP32 link (wired up in a later part) ----

    def on_esp32_arrived(self):
        self._set_state("arrived")
        self.mood_changed.emit("happy")
        self._arrived_timer.start(config.ARRIVED_REMINDER_TIMEOUT_MS)

    def on_esp32_docked(self):
        self.stops = []
        self.current_stop_index = 0
        self._set_state("idle")
        self.mood_changed.emit("neutral")

    # ---- helpers ----

    def current_stop(self):
        if self.current_stop_index < len(self.stops):
            return self.stops[self.current_stop_index]
        return None

    def _set_state(self, new_state):
        self.state = new_state
        self.state_changed.emit(new_state)

    def _on_arrived_timeout(self):
        self.mood_changed.emit("worried")

    def _send_goto_current_stop(self):
        stop = self.current_stop()
        # TODO(part 7): esp32_link.send(f"GOTO {stop['table']}")
        pass

    def _send_return_home(self):
        # TODO(part 7): esp32_link.send("RETURN_HOME")
        pass