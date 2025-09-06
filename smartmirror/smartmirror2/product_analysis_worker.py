# product_analysis_worker.py

import sys
import cv2
import tempfile
import os
import json
from PyQt5.QtCore import QThread, pyqtSignal

# OCR 모듈 임포트
from ocr.product_ocr import process_ocr

class ProductAnalysisWorker(QThread):
    finished_ok = pyqtSignal(dict)
    finished_err = pyqtSignal(str)

    def __init__(self, img_bgr, db_manager, parent=None):
        super().__init__(parent)
        self.img_bgr = img_bgr
        self.db_manager = db_manager

    def run(self):
        try:
            resized_bgr = cv2.resize(self.img_bgr, (640, 480), interpolation=cv2.INTER_AREA)
            recognized_text = process_ocr(resized_bgr)
            
            if not recognized_text:
                self.finished_err.emit("이미지에서 텍스트를 인식할 수 없어요. 제품명을 명확하게 비춰주세요.")
                return

            product_data = self.db_manager.get_product_by_name(recognized_text)
            
            if product_data:
                # OCR로 인식된 텍스트와 DB의 제품명을 함께 출력 (디버깅용)
                print(f"OCR 인식 텍스트: {recognized_text}")
                print(f"DB에서 찾은 제품명: {product_data.get('name')}")
                
                personal_colors_list = product_data.get('personal_colors', '').split('_')
                personal_color = personal_colors_list[-1] if len(personal_colors_list) > 1 else ''
                skin_type = product_data.get('skin_types', '').split(',')[0]
                
                recommendations = self.db_manager.get_products_by_filter(
                    personal_color=personal_color,
                    skin_type=skin_type
                )
                
                self.finished_ok.emit({
                    'found_product': product_data,
                    'recommendations': recommendations
                })
            else:
                self.finished_err.emit(f"'{recognized_text}' 제품을 데이터베이스에서 찾을 수 없어요.")

        except Exception as e:
            self.finished_err.emit(f"제품 분석 중 오류가 발생했습니다: {str(e)}")