from PyQt6.QtWidgets import QLabel, QVBoxLayout

from .base_screen import BaseScreen

class IdleScreen(BaseScreen):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Idle Screen"))