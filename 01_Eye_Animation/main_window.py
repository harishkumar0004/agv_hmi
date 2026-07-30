from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtGui import QShortcut, QKeySequence

from core.screen import Screen
from screens.assignment_screen import AssignmentScreen
from screens.confirmation_screen import ConfirmationScreen
from screens.idle_screen import IdleScreen
from screens.status_screen import StatusScreen
from screens.arrived_screen import ArrivedScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AGV HMI")
        self.resize(1024, 600)
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
        self.setup_shortcuts()

    def show_screen(self, screen: Screen):
        """
        Switch to anotheer screen.
        Automatically calls:
            current.on_exit()
            new_screen.on_enter()
        """
        current = self.stack.currentWidget()
        new_screen = self.screens[screen]

        if current == new_screen:
            return

        if current:
            current.on_exit()

        self.stack.setCurrentWidget(new_screen)
        new_screen.on_enter()

    # Developmenet Uptilities, shortcuts for developer
    def setup_shortcuts(self):
        """
        Register all developer keyboard shortcuts.
        """
        self.exit_shortcut = QShortcut(QKeySequence("Esc"), self)
        self.exit_shortcut.activated.connect(self.close)

        self.idle_shortcut = QShortcut(QKeySequence("F1"), self)
        self.idle_shortcut.activated.connect(lambda: self.show_screen(Screen.IDLE))

        self.assignment_shortcut = QShortcut(QKeySequence("F2"), self)
        self.assignment_shortcut.activated.connect(lambda: self.show_screen(Screen.ASSIGNMENT))

        self.confirmation_shortcut = QShortcut(QKeySequence("F3"), self)
        self.confirmation_shortcut.activated.connect(lambda: self.show_screen(Screen.CONFIRMATION))

        self.status_shortcut = QShortcut(QKeySequence("F4"), self)
        self.status_shortcut.activated.connect(lambda: self.show_screen(Screen.STATUS))

        self.arrived_shortcut = QShortcut(QKeySequence("F5"), self)
        self.arrived_shortcut.activated.connect(lambda: self.show_screen(Screen.ARRIVED))
                                        
