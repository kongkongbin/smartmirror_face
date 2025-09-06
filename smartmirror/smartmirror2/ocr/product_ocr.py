# ocr/product_ocr.py
import cv2
import numpy as np
import re

# Optional backends
_BACKEND = None
_reader = None

def _try_import_easyocr():
    global _BACKEND, _reader
    try:
        import easyocr
        _reader = easyocr.Reader(['ko', 'en'], gpu=False)  # Jetson/CPU에서도 동작
        _BACKEND = "easyocr"
    except Exception:
        _BACKEND = None

def _try_import_tesseract():
    global _BACKEND
    try:
        import pytesseract  # noqa: F401
        _BACKEND = "tesseract"
    except Exception:
        _BACKEND = None

def _ensure_backend():
    if _BACKEND is None:
        _try_import_easyocr()
        if _BACKEND is None:
            _try_import_tesseract()
    return _BACKEND

def _preprocess(img_bgr):
    # 종횡비 유지로 적당히 확대(가로 최대 1280)
    h, w = img_bgr.shape[:2]
    if w > 1280:
        r = 1280 / float(w)
        img_bgr = cv2.resize(img_bgr, (1280, int(h*r)), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    return gray

def _korean_ratio(s):
    if not s: return 0.0
    total = len(s)
    ko = sum(1 for ch in s if '\uAC00' <= ch <= '\uD7A3')
    return ko / max(1, total)

def _run_easyocr(gray):
    results = _reader.readtext(gray, detail=0)
    txt = " ".join(results)
    return txt

def _run_tesseract(gray):
    import pytesseract
    cfg = "--oem 3 --psm 6 -l kor+eng"
    txt = pytesseract.image_to_string(gray, config=cfg)
    return txt

def process_ocr(image):
    """
    EasyOCR을 우선 사용. 사용 불가 시 Tesseract로 폴백.
    좌우반전(미러) 입력 가능성을 고려하여 원본/미러 모두 시도.
    """
    try:
        backend = _ensure_backend()
        if backend is None:
            # 백엔드가 하나도 없는 경우
            return ""

        gray = _preprocess(image)
        gray_flip = cv2.flip(gray, 1)

        if backend == "easyocr":
            t1 = _run_easyocr(gray)
            t2 = _run_easyocr(gray_flip)
        else:
            t1 = _run_tesseract(gray)
            t2 = _run_tesseract(gray_flip)

        def _clean(s):
            s = re.sub(r'[\n\r\t]+', ' ', s)
            # 극단적 특수문자 제거
            s = re.sub(r'[^0-9A-Za-z가-힣 \-_/\.]+', ' ', s)
            return re.sub(r'\s+', ' ', s).strip()

        c1, c2 = _clean(t1), _clean(t2)
        # 한글 비율을 우선 가중치로 선택
        s1 = 0.6 * _korean_ratio(c1) + 0.4 * (len(c1) > 0)
        s2 = 0.6 * _korean_ratio(c2) + 0.4 * (len(c2) > 0)

        return c1 if s1 >= s2 else c2

    except Exception as e:
        print(f"OCR 처리 중 오류 발생: {e}")
        return ""
