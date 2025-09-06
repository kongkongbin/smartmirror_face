import cv2
import platform
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

class WebcamThread(QThread):
    # UI 표시용 QImage, 분석용 원본 ndarray(BGR)
    change_pixmap_signal = pyqtSignal(QImage, object)

    def __init__(self, rotate=False, mirror=True, prefer_csi=True, parent=None):
        super().__init__(parent)
        self.running = True
        self.cap = None
        self.rotate = rotate
        self.mirror = mirror
        self.prefer_csi = prefer_csi

    def _gst_pipeline_csi(self, width=1280, height=720, fps=30, flip_method=0):
        return (
            "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), width=%d, height=%d, format=NV12, framerate=%d/1 ! "
            "nvvidconv flip-method=%d ! "
            "video/x-raw, format=BGRx ! "
            "videoconvert ! "
            "video/x-raw, format=BGR ! "
            "appsink" % (width, height, fps, flip_method)
        )

    def _gst_pipeline_usb(self, dev_index=0, width=1280, height=720, fps=30):
        return (
            "v4l2src device=/dev/video%d ! "
            "video/x-raw, width=%d, height=%d, framerate=%d/1 ! "
            "videoconvert ! "
            "video/x-raw, format=BGR ! "
            "appsink" % (dev_index, width, height, fps)
        )

    def _open_capture(self):
        is_jetson = (platform.machine() == "aarch64")
        if is_jetson:
            # 우선 CSI 카메라 시도
            if self.prefer_csi:
                pipeline = self._gst_pipeline_csi()
                cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
                if cap.isOpened():
                    return cap
            # USB 카메라 파이프라인 시도
            pipeline = self._gst_pipeline_usb()
            cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
            if cap.isOpened():
                return cap
            # 마지막 폴백
            cap = cv2.VideoCapture(0)
            return cap
        else:
            # 일반 PC(Windows/Linux): 기본 장치 오픈
            # (Windows에서 CAP_DSHOW는 기기/드라이버에 따라 실패 가능하므로 생략)
            return cv2.VideoCapture(0)

    def run(self):
        self.cap = self._open_capture()
        if not self.cap or not self.cap.isOpened():
            print("Error: 웹캠을 열 수 없습니다.")
            self.running = False
            return

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            raw_original = frame  # 분석용 원본 BGR

            display_frame = frame
            if self.rotate:
                display_frame = cv2.rotate(display_frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            if self.mirror:
                display_frame = cv2.flip(display_frame, 1)

            h, w, ch = display_frame.shape
            bytes_per_line = ch * w
            # QImage는 버퍼 수명에 민감하므로 copy=False로 생성 후 Qt가 그리기 전에 유효하도록 즉시 변환
            qimg = QImage(display_frame.data, w, h, bytes_per_line, QImage.Format_BGR888).copy()

            # UI에는 미러/회전 적용 이미지를, 분석에는 원본 프레임을 전달
            self.change_pixmap_signal.emit(qimg, raw_original)

        if self.cap:
            self.cap.release()

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.wait()
