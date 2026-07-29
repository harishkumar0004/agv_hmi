from PyQt6.QtWidgets import QLabel, QVBoxLayout

from .base_screen import BaseScreen

class StatusScreen(BaseScreen):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Status Screen"))
