
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
        # Expect BGR input; convert to RGB to keep original semantics
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        Z = img.reshape((-1, 3)).astype(np.float32)

        # Criteria: max 20 iters or epsilon 1.0
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        flags = cv2.KMEANS_PP_CENTERS
        compactness, labels, centers = cv2.kmeans(Z, self.CLUSTERS, None, criteria, 10, flags)

        self.COLORS = centers
        self.LABELS = labels.flatten()

    def getHistogram(self):
        numLabels = np.arange(0, self.CLUSTERS + 1)
        (hist, _) = np.histogram(self.LABELS, bins=numLabels)
        hist = hist.astype("float")
        hist /= hist.sum()

        colors = self.COLORS
        # 내림차순 정렬
        order = (-hist).argsort()
        colors = colors[order]
        hist = hist[order]
        for i in range(len(colors)):
            colors[i] = colors[i].astype(int)

        # 파란색 마스크 제거
        fil = [colors[i][2] < 250 and colors[i][0] > 10 for i in range(len(colors))]
        colors = list(compress(colors, fil))
        return colors, hist
