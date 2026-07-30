# Controller never know about stackWidgets it only know which screen to display in the main_window

from core.screen import Screen
from main_window import MainWindow
from core.emotion import Emotion

class HMIController:

    def __init__(self, main_window: MainWindow):
        self.main_window = main_window
        self.idle_screen = self.main_window.screens[Screen.IDLE]
        self.idle_screen.face_touched.connect(self.on_face_touched)

    def show_idle(self):
        self.set_emotion(Emotion.NORMAL)
        self.main_window.show_screen(Screen.IDLE)

    def show_assignment(self):
        self.main_window.show_screen(Screen.ASSIGNMENT)

    def show_confirmation(self):
        self.set_emotion(Emotion.HAPPY)
        self.main_window.show_screen(Screen.CONFIRMATION)

    def show_status(self):
        self.set_emotion(Emotion.EXCITED)
        self.main_window.show_screen(Screen.STATUS)

    def show_arrived(self):
        self.set_emotion(Emotion.HAPPY)
        self.main_window.show_screen(Screen.ARRIVED)

    def on_face_touched(self):
        print("Switching to Assignment")
        self.show_assignment()

    def set_emotion(self, emotion: Emotion):
        self.idle_screen.play_emotion(emotion)