"""MainWindow: routes Controller state changes to the correct screen.

This file should stay 'dumb' forever -- its only job is switching
which screen is visible and calling on_enter()/on_exit() on it. Real
screen logic belongs inside each screen's own file, never here.

Screens are placeholders in this first part. They get replaced with
real screens (idle_screen.py, assignment_screen.py, ...) in parts 3-6.
"""
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QLabel, QVBoxLayout

from fullscreen.controller import Controller

# DEV-ONLY: lets you exit the fullscreen kiosk with Esc while developing.
# Remove this before real deployment -- see the system design doc's
# note on disabling escape shortcuts on the public-facing kiosk.
DEV_MODE = True


class PlaceholderScreen(QWidget):
    """Temporary stand-in until the real screen for this state exists."""

    def __init__(self, label_text):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 28px;")
        layout.addWidget(label)
        # Development shortcut


    def on_enter(self):
        pass

    def on_exit(self):
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = Controller()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.pages = {
            "idle":       PlaceholderScreen("IDLE -- long-press the face to assign a delivery"),
            "assigned":   PlaceholderScreen("ASSIGNMENT -- pick racks and tables"),
            "navigating": PlaceholderScreen("NAVIGATING -- heading to table"),
            "arrived":    PlaceholderScreen("ARRIVED -- waiting for 'I'm done'"),
            "returning":  PlaceholderScreen("RETURNING -- heading back to dock"),
        }
        for page in self.pages.values():
            self.stack.addWidget(page)

        self.controller.state_changed.connect(self._on_state_changed)
        self._on_state_changed(self.controller.state)
        self.exit_shortcut = QShortcut(QKeySequence("Esc"), self)
        self.exit_shortcut.activated.connect(self.close)

    def keyPressEvent(self, event):
        if DEV_MODE and event.key() == Qt.Key_Escape:
            QApplication.quit()
            return
        super().keyPressEvent(event)

    def _on_state_changed(self, new_state):
        self.stack.currentWidget().on_exit()
        self.stack.setCurrentWidget(self.pages[new_state])
        self.stack.currentWidget().on_enter()