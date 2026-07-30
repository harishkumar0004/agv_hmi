"""
battery_widget.py - a polished, reusable, self-drawn battery indicator
for the AGV HMI (PyQt5).

Design goals
------------
- No image assets: geometry + percentage drive everything.
- Fully proportional layout - every measurement is a fraction of the
  widget's own width/height, so calling setFixedSize() later (e.g.
  shrinking it for the production top bar) scales the shape cleanly
  instead of distorting it. Develop it big, ship it small.
- Built in layers, in the same order you'd draw it by hand:
    Layer 1: body outline + terminal
    Layer 2: fill
    Layer 3: percentage label
    Layer 4: animated fill transitions   (set_percentage_animated)
    Layer 5: charging pulse animation    (set_charging)

Usage
-----
    battery = BatteryWidget()                  # defaults to dev size
    battery.set_percentage_animated(72)
    battery.set_charging(True)

    # later, for production, just shrink it - proportions hold:
    battery.setFixedSize(44, 22)
"""

import sys

from PyQt6.QtCore import (
    Qt, QRectF, QPointF, pyqtProperty, QPropertyAnimation, QEasingCurve,
)
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPainterPath, QPolygonF
from PyQt6.QtWidgets import (
    QWidget, QSizePolicy, QApplication, QMainWindow,
    QVBoxLayout, QSlider, QLabel, QPushButton,
)


class BatteryWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._percentage = 100.0
        self._charging = False
        self._bolt_opacity = 1.0

        # Development size - generous, easy to eyeball proportions.
        # Shrink this later for the real top bar; everything in
        # paintEvent is proportional to self.width()/self.height(),
        # so shrinking just scales the drawing.
        self.setFixedSize(140, 60)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # --- Layer 4: smooth fill transitions ---
        self._fill_anim = QPropertyAnimation(self, b"percentage")
        self._fill_anim.setDuration(500)
        self._fill_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # --- Layer 5: charging pulse (bolt breathes in/out) ---
        self._pulse_anim = QPropertyAnimation(self, b"boltOpacity")
        self._pulse_anim.setDuration(900)
        self._pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._pulse_anim.finished.connect(self._reverse_pulse)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def getPercentage(self):
        return self._percentage

    def setPercentage(self, value):
        self._percentage = max(0.0, min(100.0, value))
        self.update()

    # Exposed as a Qt property so QPropertyAnimation can interpolate it
    # frame-by-frame - this is what makes the fill glide instead of jump.
    percentage = pyqtProperty(float, getPercentage, setPercentage)

    def set_percentage_animated(self, value):
        """Call this from your telemetry handler - animates smoothly
        from the current level to the new one instead of snapping."""
        self._fill_anim.stop()
        self._fill_anim.setStartValue(self._percentage)
        self._fill_anim.setEndValue(max(0.0, min(100.0, float(value))))
        self._fill_anim.start()

    def getBoltOpacity(self):
        return self._bolt_opacity

    def setBoltOpacity(self, value):
        self._bolt_opacity = value
        self.update()

    boltOpacity = pyqtProperty(float, getBoltOpacity, setBoltOpacity)

    def set_charging(self, charging: bool):
        if charging == self._charging:
            return
        self._charging = charging
        if charging:
            self._pulse_anim.stop()
            self._pulse_anim.setStartValue(1.0)
            self._pulse_anim.setEndValue(0.25)
            self._pulse_anim.start()
        else:
            self._pulse_anim.stop()
            self.setBoltOpacity(1.0)
        self.update()

    def _reverse_pulse(self):
        """Ping-pongs the pulse animation while charging stays true."""
        if not self._charging:
            return
        start = self._pulse_anim.endValue()
        end = 1.0 if start == 0.25 else 0.25
        self._pulse_anim.setStartValue(start)
        self._pulse_anim.setEndValue(end)
        self._pulse_anim.start()

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------
    def _color_for_level(self):
        if self._percentage <= 15:
            return QColor("#e5484d")   # red
        if self._percentage <= 35:
            return QColor("#f5a623")   # amber
        return QColor("#3ecf8e")       # green

    def paintEvent(self, _event):
        w, h = self.width(), self.height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # --- shared proportions, all relative to widget size ---
        outline_w = max(2.0, h * 0.09)
        terminal_w = w * 0.055
        terminal_h = h * 0.36
        gap = w * 0.02
        body_w = w - terminal_w - gap
        radius = h * 0.20

        body_rect = QRectF(
            outline_w / 2, outline_w / 2,
            body_w - outline_w, h - outline_w,
        )

        # === Layer 1: body outline + terminal ===
        painter.setPen(QPen(QColor("#c8d0d8"), outline_w))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(body_rect, radius, radius)

        terminal_rect = QRectF(
            body_w + gap,
            (h - terminal_h) / 2,
            terminal_w,
            terminal_h,
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#c8d0d8"))
        painter.drawRoundedRect(terminal_rect, terminal_w * 0.35, terminal_w * 0.35)

        # === Layer 2: fill ===
        pad = h * 0.16
        inner = QRectF(
            body_rect.x() + pad,
            body_rect.y() + pad,
            body_rect.width() - pad * 2,
            body_rect.height() - pad * 2,
        )
        fill_w = inner.width() * (self._percentage / 100.0)
        fill_rect = QRectF(inner.x(), inner.y(), fill_w, inner.height())
        fill_radius = radius * 0.45
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._color_for_level())
        painter.drawRoundedRect(fill_rect, fill_radius, fill_radius)

        # === Layer 3: percentage label ===
        font = QFont("Arial", max(6, int(h * 0.30)), QFont.Weight.Bold,)
        text = f"{int(round(self._percentage))}%"

        path = QPainterPath()
        path.addText(0, 0, font, text)
        bounds = path.boundingRect()

        # shift the label slightly right when charging so it doesn't
        # collide with the bolt drawn at the left of the body
        offset_x = body_rect.width() * 0.06 if self._charging else 0
        tx = body_rect.center().x() - bounds.width() / 2 - bounds.x() + offset_x
        ty = body_rect.center().y() - bounds.height() / 2 - bounds.y()
        path.translate(tx, ty)

        painter.setPen(QPen(QColor(0, 0, 0, 140), max(1.0, h * 0.035)))
        painter.setBrush(QColor("#ffffff"))
        painter.drawPath(path)

        # === Layer 5: charging bolt, pulsing ===
        if self._charging:
            self._draw_bolt(painter, body_rect)

    def _draw_bolt(self, painter, body_rect):
        cx = body_rect.x() + body_rect.width() * 0.24
        cy = body_rect.center().y()
        s = body_rect.height() * 0.30

        bolt = QPolygonF([
            QPointF(cx - s * 0.28, cy - s), QPointF(cx + s * 0.45, cy - s * 0.12),
            QPointF(cx, cy - s * 0.12), QPointF(cx + s * 0.28, cy + s),
            QPointF(cx - s * 0.45, cy + s * 0.12), QPointF(cx, cy + s * 0.12),
        ])
        color = QColor("#ffe45c")
        color.setAlphaF(self._bolt_opacity)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawPolygon(bolt)


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

    battery = BatteryWidget()
    v.addWidget(battery, alignment=Qt.AlignmentFlag.AlignHCenter)
    v.addStretch(1)

    pct_label = QLabel("Percentage")
    pct_label.setStyleSheet("color: #eef3f8;")
    pct_slider = QSlider(Qt.Orientation.Horizontal)
    pct_slider.setRange(0, 100)
    pct_slider.setValue(100)
    pct_slider.valueChanged.connect(battery.set_percentage_animated)
    v.addWidget(pct_label)
    v.addWidget(pct_slider)

    charge_btn = QPushButton("Toggle charging")
    charge_btn.clicked.connect(lambda: battery.set_charging(not battery._charging))
    v.addWidget(charge_btn)

    window.resize(320, 260)
    window.show()
    sys.exit(app.exec())