# Controller never know about stackWidgets it only know which screen to display in the main_window

from core.screen import Screen
from main_window import MainWindow

class HMIController:

    def __init__(self, main_window: MainWindow):
        self.main_window = main_window

    def show_idle(self):
        self.main_window.show_screen(Screen.IDLE)

    def show_assignment(self):
        self.main_window.show_screen(Screen.ASSIGNMENT)

    def show_confirmation(self):
        self.main_window.show_screen(Screen.CONFIRMATION)

    def show_status(self):
        self.main_window.show_screen(Screen.STATUS)

    def show_arrived(self):
        self.main_window.show_screen(Screen.ARRIVED)