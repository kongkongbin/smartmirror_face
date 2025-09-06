# ocr/product_ocr.py

import easyocr
import cv2
import numpy as np
import re

# EasyOCR 리더 객체 초기화 (최초 실행 시 시간이 걸릴 수 있음)
# 한글과 영어를 모두 인식하도록 'ko', 'en' 언어 설정
reader = easyocr.Reader(['ko', 'en'], gpu=False) 

def process_ocr(image):
    """
    EasyOCR을 사용해 이미지에서 텍스트를 인식하고 전처리하여 반환합니다.
    """
    try:
        results = reader.readtext(image, detail=0)
        
        recognized_text = " ".join(results)
        clean_text = re.sub(r'[\n\r\t]+', ' ', recognized_text).strip()
        
        return clean_text
    
    except Exception as e:
        print(f"OCR 처리 중 오류 발생: {e}")
        return ""