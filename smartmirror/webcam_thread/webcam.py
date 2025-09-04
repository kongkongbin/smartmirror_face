# webcam_thread/webcam.py

import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

class WebcamThread(QThread):
    # QImage 형식의 프레임과 원본 numpy 배열을 보내는 시그널
    change_pixmap_signal = pyqtSignal(QImage, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True

    def run(self):
        # 웹캠 초기화 (cv2.CAP_DSHOW를 명시하여 백엔드 변경)
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            print("Error: 웹캠을 열 수 없습니다.")
            self.running = False
            return

        while self.running:
            ret, frame = self.cap.read()
            if ret:
                # 젯슨 나노의 세로 모니터 환경에 맞춰 프레임 회전
                # 세로 캠 설치 시, 가로 프레임을 회전하여 세로로 만들어야 합니다.
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

                # 좌우반전
                frame = cv2.flip(frame, 1)

                # OpenCV BGR 포맷을 PyQt QImage 포맷으로 변환
                h, w, ch = frame.shape
                qimg = QImage(frame.data, w, h, ch * w, QImage.Format_BGR888)
                
                # 메인 UI로 시그널 전송
                self.change_pixmap_signal.emit(qimg, frame)

        self.cap.release()

    def stop(self):
        self.running = False
        self.wait()