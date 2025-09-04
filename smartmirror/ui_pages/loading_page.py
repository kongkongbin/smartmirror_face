# ui_pages/loading_page.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class LoadingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel("피부톤을 분석하고 있어요...")
        title_label.setStyleSheet("font-size: 2em; color: #ff87ab; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        
        loader_label = QLabel("잠시만 기다려 주세요")
        loader_label.setStyleSheet("font-size: 1.2em; color: #555;")
        loader_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addSpacing(20)
        layout.addWidget(loader_label)