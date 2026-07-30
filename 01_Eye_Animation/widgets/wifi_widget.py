"""
wifi_widget.py - a polished, reusable, self-drawn Wi-Fi signal indicator
for the AGV HMI (PyQt6).

Design goals
------------
- No image assets: geometry + signal level drive everything, same
  philosophy as battery_widget.py.
- Fully proportional layout - every measurement is a fraction of the
  widget's own width/height, so it can be developed large and shrunk
  for the production top bar without redoing the math.
- Built in layers:
    Layer 1: four inactive bar outlines (always drawn as the base)
    Layer 2: active bar fill, driven by a continuous 0-4 level
    Layer 3: disconnected state (diagonal slash)
    Layer 4: animated level transitions   (set_level_animated)
    Layer 5: RSSI -> bar mapping          (set_rssi)

Usage
-----
    wifi = WifiWidget()
    wifi.set_level_animated(3)      # 0-4 bars directly
    wifi.set_rssi(-62)              # or feed raw dBm
    wifi.set_disconnected()         # shows a red slash instead

    # later, for production:
    wifi.setFixedSize(28, 22)
"""

import sys

from PyQt6.QtCore import Qt, QRectF, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtWidgets import (
    QWidget, QSizePolicy, QApplication, QMainWindow,
    QVBoxLayout, QSlider, QLabel, QPushButton,
)


class WifiWidget(QWidget):

    BAR_COUNT = 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self._level = 4.0          # continuous 0..4, animated
        self._connected = True

        # Development size - shrink later (e.g. setFixedSize(28, 22))
        # for the production top bar; drawing is fully proportional.
        self.setFixedSize(100, 60)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # --- Layer 4: smooth level transitions ---
        self._level_anim = QPropertyAnimation(self, b"level")
        self._level_anim.setDuration(400)
        self._level_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def getLevel(self):
        return self._level

    def setLevel(self, value):
        self._level = max(0.0, min(float(self.BAR_COUNT), value))
        self.update()

    # Exposed as a Qt property so QPropertyAnimation can interpolate it -
    # bars fade in/out smoothly instead of snapping between states.
    level = pyqtProperty(float, getLevel, setLevel)

    def set_level_animated(self, bars: int):
        """Call this from your telemetry handler with a 0-4 bar count."""
        self._connected = True
        target = max(0, min(self.BAR_COUNT, int(bars)))
        self._level_anim.stop()
        self._level_anim.setStartValue(self._level)
        self._level_anim.setEndValue(float(target))
        self._level_anim.start()

    def set_rssi(self, dbm: int):
        """Typical Wi-Fi RSSI-to-bar mapping used by most OSes."""
        if dbm >= -55:
            bars = 4
        elif dbm >= -65:
            bars = 3
        elif dbm >= -75:
            bars = 2
        elif dbm >= -85:
            bars = 1
        else:
            bars = 0
        self.set_level_animated(bars)

    def set_disconnected(self):
        self._connected = False
        self._level_anim.stop()
        self.update()

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------
    def paintEvent(self, _event):
        w, h = self.width(), self.height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        bar_gap = w * 0.06
        bar_w = (w - bar_gap * (self.BAR_COUNT - 1)) / self.BAR_COUNT
        max_bar_h = h * 0.85
        base_y = h * 0.92

        for i in range(self.BAR_COUNT):
            bar_h = max_bar_h * ((i + 1) / self.BAR_COUNT)
            x = i * (bar_w + bar_gap)
            y = base_y - bar_h
            rect = QRectF(x, y, bar_w, bar_h)
            corner = bar_w * 0.25

            # === Layer 1: inactive bar (always drawn as the base) ===
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#4a5560"))
            painter.drawRoundedRect(rect, corner, corner)

            # === Layer 2: active fill, faded in based on continuous level ===
            if self._connected:
                fill_amount = max(0.0, min(1.0, self._level - i))
                if fill_amount > 0:
                    active_color = QColor("#3ecf8e")
                    active_color.setAlphaF(fill_amount)
                    painter.setBrush(active_color)
                    painter.drawRoundedRect(rect, corner, corner)

        # === Layer 3: disconnected state ===
        if not self._connected:
            pen = QPen(QColor("#e5484d"), max(1.5, h * 0.05))
            painter.setPen(pen)
            painter.drawLine(0, int(h * 0.05), w, int(h * 0.95))


# --------------------------------------------------------------------------
# Demo: run this file directly to fine-tune proportions live.
# --------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setStyleSheet("background: #0c0f14;")
    central = QWidget()
    window.setCentralWidget(central)
    v = QVBoxLayout(central)
    v.setContentsMargins(24, 24, 24, 24)
    v.setSpacing(10)

    wifi = WifiWidget()
    v.addWidget(wifi, alignment=Qt.AlignmentFlag.AlignHCenter)
    v.addStretch(1)

    lvl_label = QLabel("Signal bars")
    lvl_label.setStyleSheet("color: #eef3f8;")
    lvl_slider = QSlider(Qt.Orientation.Horizontal)
    lvl_slider.setRange(0, 4)
    lvl_slider.setValue(4)
    lvl_slider.valueChanged.connect(wifi.set_level_animated)
    v.addWidget(lvl_label)
    v.addWidget(lvl_slider)

    disconnect_btn = QPushButton("Toggle disconnected")
    state = {"connected": True}

    def _toggle():
        state["connected"] = not state["connected"]
        if state["connected"]:
            wifi.set_level_animated(lvl_slider.value())
        else:
            wifi.set_disconnected()

    disconnect_btn.clicked.connect(_toggle)
    v.addWidget(disconnect_btn)

    window.resize(320, 260)
    window.show()
    sys.exit(app.exec())