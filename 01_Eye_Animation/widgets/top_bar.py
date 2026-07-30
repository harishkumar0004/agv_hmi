

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QWidget

from .settings_button import SettingsButton
from .clock_widget import ClockWidget
from .wifi_widget import WifiWidget
from .battery_widget import BatteryWidget


class TopBar(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(60)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            TopBar {
                background-color: #111827;
                border: none;
            }
        """)

        self.settings_button = SettingsButton()

        self.clock = ClockWidget()

        self.wifi = WifiWidget()
        self.wifi.setFixedSize(28, 22)

        self.battery = BatteryWidget()
        self.battery.setFixedSize(44, 22)

        right_layout = QHBoxLayout()
        right_layout.setSpacing(12)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.wifi)
        right_layout.addWidget(self.battery)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 8, 18, 8)
        layout.setSpacing(0)

        layout.addWidget(self.settings_button)

        layout.addStretch()

        layout.addWidget(self.clock)

        layout.addStretch()

        layout.addLayout(right_layout)

    def set_battery_percentage(self, percentage):
        self.battery.set_percentage_animated(percentage)

    def set_battery_charging(self, charging):
        self.battery.set_charging(charging)

    def set_wifi_level(self, level):
        self.wifi.set_level_animated(level)

    def set_wifi_disconnected(self):
        self.wifi.set_disconnected()

if __name__ == "__main__":

    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow

    app = QApplication(sys.argv)

    window = QMainWindow()

    window.setStyleSheet("""
        QMainWindow {
            background: #0c0f14;
        }
    """)

    topbar = TopBar()

    window.setCentralWidget(topbar)

    window.resize(900, 80)

    window.show()

    sys.exit(app.exec())
