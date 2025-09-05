#!/usr/bin/env bash
set -euo pipefail

echo "[Option C] Python 3.6 compatibility fix starting..."

# 1) pip/setuptools/wheel pinned for Python 3.6
python3 -m pip install --upgrade "pip<21" "setuptools<60" "wheel<0.38"

# 2) Remove conflicting packages
python3 -m pip uninstall -y numpy scipy scikit-learn joblib threadpoolctl || true

# 3) Install locked set
python3 -m pip install -r requirements-py36-locked.txt

echo "Done. Verify versions:"
python3 - << 'PY'
import numpy, sklearn
print("NumPy:", numpy.__version__)
print("sklearn:", sklearn.__version__)
PY

echo "Reminder:"
echo " - On Jetson, install OpenCV and PyQt5 from apt:"
echo "     sudo apt-get install -y python3-opencv python3-pyqt5"
echo " - EasyOCR requires PyTorch; consider CPU-only or L4T-specific build later."
