# personal_color_analysis/color_extract.py
import cv2
import numpy as np
from itertools import compress

class DominantColors:
    CLUSTERS = None
    IMAGE = None
    COLORS = None
    LABELS = None

    def __init__(self, image, clusters=3):
        self.CLUSTERS = clusters
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.IMAGE = img.reshape((-1, 3)).astype(np.float32)

        # OpenCV k-means
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        flags = cv2.KMEANS_PP_CENTERS
        compactness, labels, centers = cv2.kmeans(self.IMAGE, self.CLUSTERS, None, criteria, 10, flags)

        self.COLORS = centers  # k x 3 (float32, RGB)
        self.LABELS = labels   # N x 1

    def getHistogram(self):
        labels = self.LABELS.flatten()
        hist = np.bincount(labels, minlength=self.CLUSTERS).astype("float")
        if hist.sum() > 0:
            hist /= hist.sum()

        colors = self.COLORS.copy()
        order = (-hist).argsort()
        colors = colors[order]
        hist = hist[order]

        # 정수로 캐스팅
        colors = colors.astype(np.int32)

        # 파란색 마스크 제거(원본 로직 유지: R>10, B<250)
        fil = [ (colors[i][2] < 250 and colors[i][0] > 10) for i in range(len(colors)) ]
        colors = list(compress(list(colors), fil))
        return colors, hist
