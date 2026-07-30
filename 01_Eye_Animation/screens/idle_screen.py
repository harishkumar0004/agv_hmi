from pathlib import Path
from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

from bridge.js_bridge import JSBridge
from screens.base_screen import BaseScreen
from core.emotion import Emotion

class IdleScreen(BaseScreen):
    face_touched = pyqtSignal()
    def __init__(self):
        super().__init__()

        self.web_view = QWebEngineView()
        

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.web_view)

        self.load_face()
        self.web_view.loadFinished.connect(self.on_page_loaded)
        self.channel = QWebChannel()
        self.bridge = JSBridge()
        self.channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)
        self.bridge.faceTouched.connect(self.face_touched.emit)
        
        

    def on_page_loaded(self, ok: bool):
        if ok:
            print("Face loaded.")
        else:
            print("Failed to load face.")

    def load_face(self):
        """
        Load the local html face animation.
        """

        html_path = (Path(__file__).resolve().parent.parent / "assets"/"face"/"index.html")
        self.web_view.setUrl(QUrl.fromLocalFile(str(html_path)))

    # Single Gateway from python to Js
    def execute_js(self, script: str):
        """
        Execute Javascript inside the web page.
        """
        self.web_view.page().runJavaScript(script)

    def play_emotion(self, emotion: Emotion):
        """
        Render the requested emotion on the robot face.
        """
        self.execute_js(f"playEmotion('{emotion.value}')")

