import sys
import os
import cv2
import tempfile
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QMessageBox, QDesktopWidget
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap

# UI 관련 모듈 임포트
from ui_pages.home_page import HomePage
from ui_pages.capture_page import ProductCapturePage, FaceCapturePage
from ui_pages.result_pages import FaceResultPage, ProductRecommendPage
from ui_pages.loading_page import LoadingPage

# 웹캠 스레드 모듈 임포트
from webcam_thread.webcam import WebcamThread

# 분석 스레드 모듈 임포트
from analysis_worker import AnalysisWorker
from product_analysis_worker import ProductAnalysisWorker

# 데이터베이스 관리 모듈 임포트
from db_manager.database import DatabaseManager

class BeautyFinderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI 뷰티 파인더")
        
        self.setGeometry(100, 100, 800, 600) 
        self.setFixedSize(self.width(), self.height())
        self.center()
        
        self.webcam_last_frame = None
        self.webcam_thread = None
        self.db_manager = DatabaseManager()

        self.user_tone = None
        self.user_color = None
        self.user_skin_type = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        self.create_pages()
        self.apply_styles()
        
        self.stacked_widget.setCurrentWidget(self.pages['home'])
    
    def create_pages(self):
        self.pages = {}
        
        self.pages['home'] = HomePage(self)
        self.pages['product_capture'] = ProductCapturePage(self)
        self.pages['face_capture'] = FaceCapturePage(self)
        self.pages['face_result'] = FaceResultPage(self)
        self.pages['product_recommend'] = ProductRecommendPage(self)
        self.pages['loading'] = LoadingPage(self)
        
        self.stacked_widget.addWidget(self.pages['home'])
        self.stacked_widget.addWidget(self.pages['product_capture'])
        self.stacked_widget.addWidget(self.pages['face_capture'])
        self.stacked_widget.addWidget(self.pages['face_result'])
        self.stacked_widget.addWidget(self.pages['product_recommend'])
        self.stacked_widget.addWidget(self.pages['loading'])
        
        self.pages['home'].product_btn.clicked.connect(self.show_product_capture)
        self.pages['home'].face_btn.clicked.connect(self.show_face_capture)
        self.pages['product_capture'].home_btn.clicked.connect(self.go_home)
        self.pages['face_capture'].home_btn.clicked.connect(self.go_home)
        self.pages['face_result'].go_home_btn.clicked.connect(self.go_home)
        self.pages['product_recommend'].go_home_btn.clicked.connect(self.go_home)
        
        self.pages['product_capture'].capture_btn.clicked.connect(self.start_product_analysis)
        self.pages['face_capture'].capture_btn.clicked.connect(self.start_face_analysis)

    def start_product_analysis(self):
        if self.webcam_last_frame is None or self.webcam_last_frame.size == 0:
            QMessageBox.warning(self, "안내", "웹캠 프레임을 아직 받지 못했어요.")
            return

        self.stop_webcam()
        self.pages['loading'].set_message("제품을 인식하고 있어요...", "잠시만 기다려 주세요")
        self.stacked_widget.setCurrentWidget(self.pages['loading'])
        QApplication.processEvents()
        
        self.product_analysis_thread = ProductAnalysisWorker(self.webcam_last_frame, self.db_manager)
        self.product_analysis_thread.finished_ok.connect(self.on_product_analysis_done)
        self.product_analysis_thread.finished_err.connect(self.on_product_analysis_error)
        self.product_analysis_thread.finished.connect(self.product_analysis_thread.deleteLater)
        self.product_analysis_thread.start()

    def on_product_analysis_done(self, result_data):
        # 안전 가드: 추천 페이지 메서드가 없는 경우에도 앱이 죽지 않도록 처리
        page = self.pages.get('product_recommend')
        if page and hasattr(page, 'update_recommendations'):
            try:
                page.update_recommendations(result_data)
                self.stacked_widget.setCurrentWidget(page)
                return
            except Exception as e:
                QMessageBox.critical(self, "표시 오류", f"추천 화면을 그리는 중 오류가 발생했어요: {str(e)}")
        # 폴백: 인식된 제품명만 안내하고 홈으로
        try:
            found = (result_data or {}).get('found_product') or {}
            pname = found.get('name') or found.get('brand') or '제품'
            QMessageBox.information(self, "제품 인식 완료", f"인식된 제품: {pname}\n추천 화면은 아직 준비 중이에요.")
        except Exception:
            QMessageBox.information(self, "제품 인식 완료", "추천 화면은 아직 준비 중이에요.")
        self.go_home()

    def on_product_analysis_error(self, msg):
        QMessageBox.critical(self, "OCR 분석 오류", msg)
        self.go_home()

    def start_face_analysis(self):
        if self.webcam_last_frame is None or self.webcam_last_frame.size == 0:
            QMessageBox.warning(self, "안내", "웹캠 프레임을 아직 받지 못했어요.")
            return

        self.stop_webcam()
        self.pages['loading'].set_message("피부톤을 분석하고 있어요...", "잠시만 기다려 주세요")
        self.stacked_widget.setCurrentWidget(self.pages['loading'])
        QApplication.processEvents()

        self.analysis_thread = AnalysisWorker(self.webcam_last_frame)
        self.analysis_thread.finished_ok.connect(self.on_analysis_done)
        self.analysis_thread.finished_err.connect(self.on_analysis_error)
        self.analysis_thread.finished.connect(self.analysis_thread.deleteLater)
        self.analysis_thread.start()

    def on_analysis_done(self, user_tone_num, user_color, brightness):
        self.user_tone = user_tone_num
        self.user_color = user_color

        QMessageBox.information(
            self, "피부 분석 결과",
            f"피부톤: {user_tone_num}호\n퍼스널 컬러: {user_color}\n피부 밝기: {brightness:.2f}"
        )

        result_data = self.db_manager.get_beauty_data(self.user_tone, self.user_color)
        if result_data:
            self.pages['face_result'].update_result(result_data)
            self.stacked_widget.setCurrentWidget(self.pages['face_result'])
        else:
            # DB 매칭이 없더라도 결과 화면은 표시
            fallback = {
                'title': f"{self.user_tone} {self.user_color}",
                'desc': 'DB에 매칭되는 제품이 아직 없어요. 결과만 먼저 보여드립니다.',
                'products': []
            }
            self.pages['face_result'].update_result(fallback)
            self.stacked_widget.setCurrentWidget(self.pages['face_result'])

            
    def on_analysis_error(self, msg):
        QMessageBox.critical(self, "분석 오류", msg)
        self.go_home()
    
    def apply_styles(self):
        self.setStyleSheet("""
            QWidget { background-color: #fdf6f9; }
            QPushButton#main_menu_btn {
                background-color: #ff87ab;
                color: white;
                font-size: 2.5em;
                font-weight: bold;
                padding: 40px 60px;
                border: 1px solid #ff87ab;
                border-radius: 20px;
            }
            QPushButton#main_menu_btn:hover {
                background-color: #e67a9a;
            }
            QPushButton#capture_btn {
                background-color: #87e3ff;
                color: white;
                font-size: 2em;
                font-weight: bold;
                padding: 30px;
                border-radius: 50px;
            }
            QPushButton#capture_btn:hover {
                background-color: #7ac8e6;
            }
            QPushButton#home_btn {
                background-color: #ccc;
                color: white;
                font-size: 2em;
                font-weight: bold;
                padding: 30px;
                border-radius: 50px;
            }
            QPushButton#home_btn:hover {
                background-color: #bbb;
            }
        """)

    def go_home(self):
        self.stop_webcam()
        self.stacked_widget.setCurrentWidget(self.pages['home'])

    def show_product_capture(self):
        self.start_webcam_and_connect(self.pages['product_capture'])
        self.stacked_widget.setCurrentWidget(self.pages['product_capture'])

    def show_face_capture(self):
        self.start_webcam_and_connect(self.pages['face_capture'])
        self.stacked_widget.setCurrentWidget(self.pages['face_capture'])
        
    def start_webcam_and_connect(self, page_widget):
        if self.webcam_thread is not None and self.webcam_thread.isRunning():
            self.webcam_thread.stop()
            self.webcam_thread.wait()
            
        self.webcam_thread = WebcamThread()
        self.webcam_thread.change_pixmap_signal.connect(page_widget.update_frame)
        self.webcam_thread.start()
    
    def stop_webcam(self):
        if self.webcam_thread is not None and self.webcam_thread.isRunning():
            self.webcam_thread.stop()
            self.webcam_thread.wait()
            
    def closeEvent(self, event):
        self.stop_webcam()
        event.accept()
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = BeautyFinderApp()
    main_app.show()
    sys.exit(app.exec_())