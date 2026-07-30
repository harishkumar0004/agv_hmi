from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot

class JSBridge(QObject):
    """
    Bridge between Js and Python
    """

    faceTouched = pyqtSignal()

    @pyqtSlot()
    def onFaceTouched(self):
        print("JS -> Python: face touched")
        self.faceTouched.emit()