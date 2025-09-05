
# product_analysis_worker.py
import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from ocr.product_ocr import process_ocr

class ProductAnalysisWorker(QThread):
    finished_ok = pyqtSignal(dict)
    finished_err = pyqtSignal(str)

    def __init__(self, img_bgr, db_manager, parent=None):
        super().__init__(parent)
        self.img_bgr = img_bgr
        self.db_manager = db_manager

    def _resize_keep_ratio(self, img, max_width=1024):
        h, w = img.shape[:2]
        if w > max_width:
            r = max_width / float(w)
            return cv2.resize(img, (max_width, int(h*r)), interpolation=cv2.INTER_AREA)
        return img

    def run(self):
        try:
            if self.img_bgr is None:
                self.finished_err.emit("이미지 프레임이 비어 있습니다.")
                return

            resized = self._resize_keep_ratio(self.img_bgr, 1024)
            text = (process_ocr(resized) or "").strip()
            if not text:
                self.finished_err.emit("이미지에서 텍스트를 인식할 수 없어요. 제품 라벨을 또렷하게 비춰주세요.")
                return

            # DB 매칭: 메서드 호환
            product = None
            if hasattr(self.db_manager, "get_products_by_name"):
                product = self.db_manager.get_products_by_name(text)
            elif hasattr(self.db_manager, "get_product_by_name"):
                product = self.db_manager.get_product_by_name(text)

            if not product:
                self.finished_err.emit(f"'{text}' 제품을 데이터베이스에서 찾을 수 없어요.")
                return

            # personal_colors: "20_spring_warm,21_spring_warm" → 첫 항목 → spring_warm
            pc_str = (product.get("personal_colors") or "").strip()
            first_pc = pc_str.split(",")[0].strip() if pc_str else ""
            if "_" in first_pc:
                personal_color = "_".join(first_pc.split("_")[1:])
            else:
                personal_color = first_pc or None

            # skin_types: "지성,건성" → 첫 항목
            st_str = (product.get("skin_types") or "").strip()
            skin_type = st_str.split(",")[0].strip() if st_str else None

            # 추천(가능할 때만)
            recs = []
            if hasattr(self.db_manager, "get_products_by_filter"):
                recs = self.db_manager.get_products_by_filter(
                    personal_color=personal_color,
                    skin_type=skin_type,
                    exclude_id=product.get("id"),
                    limit=6
                )

            self.finished_ok.emit({
                "found_product": product,
                "recommendations": recs
            })

        except Exception as e:
            self.finished_err.emit(f"제품 분석 중 오류가 발생했습니다: {str(e)}")
