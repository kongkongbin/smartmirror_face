# ocr/product_ocr.py (patched)
import easyocr
import cv2
import numpy as np
import re

# EasyOCR 초기화(지연 초기화 대신 모듈 전역 1회)
# 한국어 우선 + 영어 보조
reader = easyocr.Reader(['ko', 'en'], gpu=False)

def _resize_keep_ratio(img, max_w=1280):
    h, w = img.shape[:2]
    if w > max_w:
        r = max_w / float(w)
        return cv2.resize(img, (max_w, int(h*r)), interpolation=cv2.INTER_AREA)
    return img

def _enhance(image):
    # 그레이스케일 + CLAHE + 가벼운 샤프닝
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    # 샤프닝 커널
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]], dtype=np.float32)
    sharp = cv2.filter2D(gray, -1, kernel)
    return sharp

def _korean_ratio(s: str) -> float:
    if not s:
        return 0.0
    total = max(1, len(s))
    ko = sum(1 for ch in s if '\uAC00' <= ch <= '\uD7A3')
    return ko / total

def _read_text(img) -> tuple[str, float]:
    # detail=1로 confidence 확보
    results = reader.readtext(img, detail=1, paragraph=True, contrast_ths=0.05, adjust_contrast=0.7)
    texts = []
    confs = []
    for r in results:
        try:
            _, txt, conf = r
        except ValueError:
            # 일부 버전은 (bbox, text, conf)
            txt = r[1] if len(r) > 1 else ""
            conf = r[2] if len(r) > 2 else 0.0
        if isinstance(txt, str) and txt.strip():
            texts.append(txt.strip())
            try:
                confs.append(float(conf))
            except Exception:
                pass
    joined = " ".join(texts)
    clean = re.sub(r"[\n\r\t]+", " ", joined).strip()
    mean_conf = float(np.mean(confs)) if confs else 0.0
    return clean, mean_conf

def process_ocr(image_bgr: np.ndarray) -> str:
    """전처리 + 원본/좌우반전 모두 시도 후 더 그럴듯한 텍스트 반환"""
    try:
        img = _resize_keep_ratio(image_bgr, max_w=1280)
        enh = _enhance(img)

        t1, c1 = _read_text(enh)
        t2, c2 = _read_text(cv2.flip(enh, 1))

        s1 = 0.6 * _korean_ratio(t1) + 0.4 * c1
        s2 = 0.6 * _korean_ratio(t2) + 0.4 * c2

        best = t1 if s1 >= s2 else t2
        best = re.sub(r"\s+", " ", best).strip()
        return best
    except Exception as e:
        print(f"OCR 처리 중 오류 발생: {e}")
        return ""