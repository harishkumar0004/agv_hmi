"""
clock_widget.py - a plain text time/date display for the AGV HMI top bar.

Design goals
------------
- No icon, no custom painting - just two QLabels (time + date), updated
  once a second by a QTimer. Meant to sit in the center of the top bar.
- Kept intentionally simple: unlike battery/Wi-Fi there's no visual
  "state" to represent beyond the text itself, so there's nothing here
  to draw by hand or animate.

Usage
-----
    clock = ClockWidget()
    # put stretch on both sides in your top bar's QHBoxLayout so this
    # widget lands in the true center regardless of what's to its left
    # and right (settings icon vs. wifi+battery are different widths):
    layout.addStretch(1)
    layout.addWidget(clock)
    layout.addStretch(1)
"""

import sys

from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication, QMainWindow,
)


class ClockWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet(
            "color: #eef3f8; font-size: 18px; font-weight: 600;"
        )

        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet(
            "color: #8a94a3; font-size: 12px;"
        )
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        layout.addWidget(self.time_label)
        layout.addWidget(self.date_label)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)
        self._tick()

    def _tick(self):
        now = QDateTime.currentDateTime()
        self.time_label.setText(now.toString("hh:mm:ss AP"))
        self.date_label.setText(now.toString("ddd, MMM d yyyy"))


# --------------------------------------------------------------------------
# Demo: shows the clock centered in a bar, the way it'll sit in your
# real top_bar.py once assembled.
# --------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setStyleSheet("background: #0c0f14;")
    central = QWidget()
    window.setCentralWidget(central)

    bar = QWidget()
    bar.setFixedHeight(50)
    bar.setStyleSheet("background: #12161c;")
    bar_layout = QHBoxLayout(bar)
    bar_layout.setContentsMargins(14, 4, 14, 4)

    bar_layout.addStretch(1)
    bar_layout.addWidget(ClockWidget())
    bar_layout.addStretch(1)

    outer = QVBoxLayout(central)
    outer.setContentsMargins(0, 0, 0, 0)
    outer.addWidget(bar)
    outer.addStretch(1)

    window.resize(420, 200)
    window.show()
    sys.exit(app.exec())