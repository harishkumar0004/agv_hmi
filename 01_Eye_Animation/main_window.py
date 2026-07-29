from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from core.screen import Screen
from screens.base_screen import BaseScreen
from screens.assignment_screen import AssignmentScreen
from screens.confirmation_screen import ConfirmationScreen
from screens.idle_screen import IdleScreen
from screens.status_screen import StatusScreen
from screens.arrived_screen import ArrivedScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.screens = {
            Screen.IDLE: IdleScreen(),
            Screen.ASSIGNMENT: AssignmentScreen(),
            Screen.CONFIRMATION: ConfirmationScreen(),
            Screen.STATUS: StatusScreen(),
            Screen.ARRIVED: ArrivedScreen(),
        }

        for screen in self.screens.values():
            self.stack.addWidget(screen)

        self.show_screen(Screen.IDLE)

    def show_screen(self, screen: Screen):
        current = self.stack.currentWidget()
        new_screen = self.screens[screen]

        if current == new_screen:
            return

        if current:
            current.on_exit()

        self.stack.setCurrentWidget(new_screen)
        new_screen.on_enter()

