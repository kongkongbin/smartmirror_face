import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
import platform, cv2

class WebcamThread(QThread):
    # UI 표시용(QImage, 미러 적용) + 분석용 원본 ndarray(미러 미적용)
    change_pixmap_signal = pyqtSignal(QImage, object)

    def __init__(self, rotate=False, mirror=True, parent=None):
        super().__init__(parent)
        self._running = True
        self.cap = None
        self.rotate = rotate
        self.mirror = mirror

    def run(self):
        # CAP_DSHOW는 Windows에서 카메라 초기화 속도 개선
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            print("Error: 웹캠을 열 수 없습니다.")
            self._running = False
            return

        while self._running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            # 분석용 원본 프레임(미러 미적용)
            raw = frame.copy()

            # 회전은 두 경로 모두 동일하게 적용(필요시 옵션)
            if self.rotate:
                raw = cv2.rotate(raw, cv2.ROTATE_90_COUNTERCLOCKWISE)

            # 화면 표시용은 보기 좋게 미러 적용 가능
            disp = raw.copy()
            if self.mirror:
                disp = cv2.flip(disp, 1)

            h, w, ch = disp.shape
            bytes_per_line = ch * w
            qimg = QImage(disp.data, w, h, bytes_per_line, QImage.Format_BGR888).copy()  # 수명 안전

            self.change_pixmap_signal.emit(qimg, raw)

        if self.cap:
            self.cap.release()

        def _gst_pipeline_csi(width=1280, height=720, fps=30, flip_method=0):
            return (
                f"nvarguscamerasrc ! video/x-raw(memory:NVMM), width={width}, height={height}, "
                f"format=NV12, framerate={fps}/1 ! nvvidconv flip-method={flip_method} ! "
                f"video/x-raw, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink"
            )

    def _gst_pipeline_usb(dev_index=0, width=1280, height=720, fps=30):
        return (
            f"v4l2src device=/dev/video{dev_index} ! video/x-raw, width={width}, height={height}, framerate={fps}/1 ! "
            f"videoconvert ! video/x-raw, format=BGR ! appsink"
        )
    
    def open_capture(prefer_csi=True):
        is_jetson = (platform.machine() == "aarch64")
        if not is_jetson:
            return cv2.VideoCapture(0)  # Windows/일반 PC
        # Jetson: GStreamer 사용
        pipeline = _gst_pipeline_csi() if prefer_csi else _gst_pipeline_usb()
        cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
        if not cap.isOpened():
            # 폴백: USB 카메라 혹은 기본 0시도
            cap = cv2.VideoCapture(0)
        return cap

    def stop(self):
        self._running = False
        if self.cap:
            self.cap.release()
        self.wait()