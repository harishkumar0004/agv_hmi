"""
setting_button.py

Reusable Settings button for the AGV HMI.
Uses QSvgWidget for crisp SVG rendering.
"""

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QPushButton,
    QWidget,
    QHBoxLayout,
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
# --------------------------------------------------------
# Assets
# --------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"

SETTINGS_ICON = ASSETS_DIR / "setting.svg"


class SettingsButton(QPushButton):

    clicked_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):

        self.setFixedSize(44, 44)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setFlat(True)

        if SETTINGS_ICON.exists():
            self.setIcon(QIcon(str(SETTINGS_ICON)))
            self.setFixedSize(44, 44)
            self.setIconSize(QSize(28, 28))
        else:
            print(f"[ERROR] SVG Not Found : {SETTINGS_ICON}")


        self.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 20px;
                background: transparent;
            }

            QPushButton:hover {
                background-color: #2F343F;
            }

            QPushButton:pressed {
                background: #444B58;
            }
        """)

    def setup_connections(self):

        self.clicked.connect(self.clicked_signal.emit)


# --------------------------------------------------------
# Standalone Test
# --------------------------------------------------------

if __name__ == "__main__":

    import sys

    app = QApplication(sys.argv)      # MUST be first

    window = QWidget()
    window.setWindowTitle("Settings Button Test")

    window.setStyleSheet("""
        background:white;
    """)

    layout = QVBoxLayout(window)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    button = SettingsButton()

    button.clicked_signal.connect(
        lambda: print("Settings button clicked.")
    )

    layout.addWidget(button)

    window.resize(250,180)

    window.show()

    sys.exit(app.exec())