
import platform
import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

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

def _open_capture(prefer_csi=True):
    is_jetson = (platform.machine() == "aarch64")
    if is_jetson:
        # Try CSI first then USB
        if prefer_csi:
            cap = cv2.VideoCapture(_gst_pipeline_csi(), cv2.CAP_GSTREAMER)
            if cap.isOpened():
                return cap
            cap = cv2.VideoCapture(_gst_pipeline_usb(), cv2.CAP_GSTREAMER)
            if cap.isOpened():
                return cap
        else:
            cap = cv2.VideoCapture(_gst_pipeline_usb(), cv2.CAP_GSTREAMER)
            if cap.isOpened():
                return cap
            cap = cv2.VideoCapture(_gst_pipeline_csi(), cv2.CAP_GSTREAMER)
            if cap.isOpened():
                return cap
        # Fallback
        cap = cv2.VideoCapture(0)
        return cap
    # Non-Jetson platforms: default camera
    return cv2.VideoCapture(0)

class WebcamThread(QThread):
    # QImage(display), object(raw_bgr_original)
    change_pixmap_signal = pyqtSignal(QImage, object)

    def __init__(self, rotate=False, mirror=True, prefer_csi=True, parent=None):
        super().__init__(parent)
        self.running = True
        self.cap = None
        self.rotate = rotate
        self.mirror = mirror
        self.prefer_csi = prefer_csi

    def run(self):
        self.cap = _open_capture(prefer_csi=self.prefer_csi)
        if not self.cap or not self.cap.isOpened():
            print("Error: 카메라를 열 수 없습니다.")
            self.running = False
            return

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            raw_bgr = frame  # 분석용 원본(미러/회전 적용 금지)

            display = frame
            if self.rotate:
                display = cv2.rotate(display, cv2.ROTATE_90_COUNTERCLOCKWISE)
            if self.mirror:
                display = cv2.flip(display, 1)

            h, w, ch = display.shape
            bytes_per_line = ch * w
            qimg = QImage(display.data, w, h, bytes_per_line, QImage.Format_BGR888)

            # 화면: 미러 적용 QImage, 분석: 원본 BGR
            self.change_pixmap_signal.emit(qimg, raw_bgr)

        if self.cap:
            self.cap.release()

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.wait()
