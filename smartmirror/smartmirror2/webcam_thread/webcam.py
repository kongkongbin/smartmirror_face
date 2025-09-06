import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

class WebcamThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage, object)

    def __init__(self, rotate=False, mirror=True, parent=None):
        super().__init__(parent)
        self.running = True
        self.cap = None
        self.rotate = rotate
        self.mirror = mirror

    def run(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            print("Error: 웹캠을 열 수 없습니다.")
            self.running = False
            return

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            if self.rotate:
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            
            if self.mirror:
                frame = cv2.flip(frame, 1)

            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_BGR888)

            self.change_pixmap_signal.emit(qimg, frame)

        self.cap.release()

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.wait()