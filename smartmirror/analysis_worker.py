# analysis_worker.py

import sys
import cv2
import tempfile
import os
from PyQt5.QtCore import QThread, pyqtSignal
from personal_color_analysis.detect_face import DetectFace
from personal_color_analysis.color_extract import DominantColors
from personal_color_analysis.tone_analysis import is_warm, is_spr, is_smr
from colormath.color_objects import LabColor, sRGBColor, HSVColor
from colormath.color_conversions import convert_color
import numpy as np

class AnalysisWorker(QThread):
    finished_ok = pyqtSignal(str, str)
    finished_err = pyqtSignal(str)

    def __init__(self, img_bgr, parent=None):
        super().__init__(parent)
        self.img_bgr = img_bgr

    def run(self):
        tmp_path = None
        try:
            fd, tmp_path = tempfile.mkstemp(suffix=".jpg")
            os.close(fd)
            cv2.imwrite(tmp_path, self.img_bgr)
            
            df = DetectFace(tmp_path)
            face = [df.left_cheek, df.right_cheek, df.left_eyebrow, df.right_eyebrow, df.left_eye, df.right_eye]
            temp = []
            clusters = 4
            for f in face:
                dc = DominantColors(f, clusters)
                face_part_color, _ = dc.getHistogram()
                temp.append(np.array(face_part_color[0]))
            
            cheek = np.mean([temp[0], temp[1]], axis=0)
            eyebrow = np.mean([temp[2], temp[3]], axis=0)
            eye = np.mean([temp[4], temp[5]], axis=0)

            Lab_b, hsv_s = [], []
            color = [cheek, eyebrow, eye]
            for i in range(3):
                rgb = sRGBColor(color[i][0], color[i][1], color[i][2], is_upscaled=True)
                lab = convert_color(rgb, LabColor, through_rgb_type=sRGBColor)
                hsv = convert_color(rgb, HSVColor, through_rgb_type=sRGBColor)
                Lab_b.append(float(format(lab.lab_b, ".2f")))
                hsv_s.append(float(format(hsv.hsv_s, ".2f")) * 100)

            Lab_weight = [30, 20, 5]
            hsv_weight = [10, 1, 1]
            
            if is_warm(Lab_b, Lab_weight):
                if is_spr(hsv_s, hsv_weight):
                    tone = 'spring_warm'
                else:
                    tone = 'fall_warm'
            else:
                if is_smr(hsv_s, hsv_weight):
                    tone = 'summer_cool'
                else:
                    tone = 'winter_cool'
            
            gray = cv2.cvtColor(self.img_bgr, cv2.COLOR_BGR2GRAY)
            brightness = float(gray.mean())
            user_tone_num = '20' if brightness >= 120 else '21'

            self.finished_ok.emit(user_tone_num, tone)
            
        except RuntimeError as e:
            if str(e) == "No face detected in the image.":
                cv2.imwrite('error_image.jpg', self.img_bgr)
                self.finished_err.emit("이미지에서 얼굴을 찾을 수 없어요. 조명과 얼굴 위치를 확인해주세요.")
            else:
                self.finished_err.emit(str(e))
        except Exception as e:
            self.finished_err.emit(f"분석 중 오류가 발생했습니다: {str(e)}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass