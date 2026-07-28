"""
main.py — Entry point. Creates QApplication and launches the HMI.

Run with:
    python3 main.py

For kiosk mode on Raspberry Pi:
    QT_QPA_PLATFORM=eglfs python3 main.py
"""

import sys
from PyQt5.QtWidgets import QApplication

from controller import Controller
from main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    # Create the brain (state machine)
    controller = Controller()

    # Create the window (router + screens)
    window = MainWindow(controller)
    window.show()

    # Start in idle state
    controller.to_idle()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
