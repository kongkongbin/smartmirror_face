from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QGridLayout
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QFont

class WebcamGuideLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #000; color: #fff;")
        self.setAlignment(Qt.AlignCenter)
        self.guide_mode = False

    def setGuideMode(self, mode):
        self.guide_mode = mode
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        
        if self.guide_mode:
            qp = QPainter(self)
            qp.setPen(QPen(QColor(255, 255, 255, 150), 5))
            
            rect = self.rect()
            width = rect.width() * 0.8
            height = rect.height() * 0.8
            
            x = (rect.width() - width) / 2
            y = (rect.height() - height) / 2
            
            qp.drawEllipse(int(x), int(y), int(width), int(height))

class ProductCapturePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.webcam_label = QLabel()
        self.webcam_label.setStyleSheet("background: #000; color: #fff;")
        self.webcam_label.setAlignment(Qt.AlignCenter)
        
        button_container = QWidget()
        button_container.setAttribute(Qt.WA_TranslucentBackground, True)
        button_layout = QVBoxLayout(button_container)
        button_layout.setAlignment(Qt.AlignBottom | Qt.AlignCenter)
        button_layout.setContentsMargins(50, 50, 50, 50)
        
        self.capture_btn = QPushButton("촬영")
        self.capture_btn.setFixedSize(300, 100)
        self.capture_btn.setObjectName("capture_btn")
        
        self.home_btn = QPushButton("처음으로")
        self.home_btn.setFixedSize(300, 100)
        self.home_btn.setObjectName("home_btn")
        
        button_layout.addWidget(self.capture_btn)
        button_layout.addSpacing(20)
        button_layout.addWidget(self.home_btn)
        
        main_layout.addWidget(self.webcam_label, 0, 0)
        main_layout.addWidget(button_container, 0, 0)
        
    def update_frame(self, qimg, raw_bgr):
        if qimg and not qimg.isNull():
            scaled_qimg = qimg.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.webcam_label.setPixmap(QPixmap.fromImage(scaled_qimg))
        self.parent.webcam_last_frame = raw_bgr
        
class FaceCapturePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # WebcamGuideLabel 사용
        self.webcam_label = WebcamGuideLabel()
        
        button_container = QWidget()
        button_container.setAttribute(Qt.WA_TranslucentBackground, True)
        button_layout = QVBoxLayout(button_container)
        button_layout.setAlignment(Qt.AlignBottom | Qt.AlignCenter)
        button_layout.setContentsMargins(50, 50, 50, 50)
        
        self.capture_btn = QPushButton("촬영")
        self.capture_btn.setFixedSize(300, 100)
        self.capture_btn.setObjectName("capture_btn")
        
        self.home_btn = QPushButton("처음으로")
        self.home_btn.setFixedSize(300, 100)
        self.home_btn.setObjectName("home_btn")
        
        button_layout.addWidget(self.capture_btn)
        button_layout.addSpacing(20)
        button_layout.addWidget(self.home_btn)
        
        main_layout.addWidget(self.webcam_label, 0, 0)
        main_layout.addWidget(button_container, 0, 0)
    
    def update_frame(self, qimg, raw_bgr):
        if qimg and not qimg.isNull():
            scaled_qimg = qimg.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.webcam_label.setPixmap(QPixmap.fromImage(scaled_qimg))
        self.parent.webcam_last_frame = raw_bgr
        self.webcam_label.setGuideMode(True)