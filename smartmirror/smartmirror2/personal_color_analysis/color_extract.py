# -*- coding: utf-8 -*-
"""
No-sklearn color extraction using OpenCV k-means.
Provides a DominantColors class compatible with previous API.
"""
import cv2
import numpy as np

class DominantColors:
    def __init__(self, img_bgr: np.ndarray, clusters: int = 3):
        if img_bgr is None or getattr(img_bgr, "size", 0) == 0:
            raise ValueError("Empty image for DominantColors")
        self.img_bgr = img_bgr
        self.clusters = int(clusters) if clusters and clusters > 0 else 3

    def _kmeans(self):
        Z = self.img_bgr.reshape((-1,3)).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        flags = cv2.KMEANS_PP_CENTERS
        compactness, labels, centers = cv2.kmeans(Z, self.clusters, None, criteria, 10, flags)
        centers = centers.astype(np.uint8)   # BGR
        counts = np.bincount(labels.flatten(), minlength=self.clusters)
        order = counts.argsort()[::-1]
        centers = centers[order]
        counts = counts[order]
        return centers, counts

    def getHistogram(self):
        """
        Returns (colors, hist)

        - colors: list of [R, G, B] for each cluster, sorted by frequency desc
        - hist: list of normalized frequencies (sum to 1.0)
        """
        centers_bgr, counts = self._kmeans()
        total = float(counts.sum()) if counts.sum() > 0 else 1.0
        hist = (counts.astype(np.float32) / total).tolist()
        # convert BGR -> RGB list
        colors_rgb = [[int(c[2]), int(c[1]), int(c[0])] for c in centers_bgr.tolist()]
        return colors_rgb, hist

# Backward compatible helper functions
def kmeans_colors_cv2(img_bgr: np.ndarray, k: int = 3, attempts: int = 10):
    dc = DominantColors(img_bgr, clusters=k)
    centers_rgb, hist = dc.getHistogram()
    # Return as BGR centers to be explicit
    centers_bgr = np.array([[c[2], c[1], c[0]] for c in centers_rgb], dtype=np.uint8)
    counts = np.array(hist) * (img_bgr.shape[0] * img_bgr.shape[1])
    return centers_bgr, counts.astype(np.int64)

def dominant_color_bgr(img_bgr: np.ndarray, k: int = 3) -> tuple:
    centers_bgr, counts = kmeans_colors_cv2(img_bgr, k=k, attempts=10)
    return tuple(int(x) for x in centers_bgr[0].tolist())

def palette_bgr(img_bgr: np.ndarray, k: int = 5) -> np.ndarray:
    centers_bgr, counts = kmeans_colors_cv2(img_bgr, k=k, attempts=10)
    return centers_bgr
