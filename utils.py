import numpy as np
import cv2

def draw_bar(img, value, x, y, w, h, color, label):
    """Draw a vertical progress bar on the frame."""
    cv2.rectangle(img, (x, y), (x + w, y + h), (200, 200, 200), 2)
    fill_y = int(y + h - (value / 100) * h)
    cv2.rectangle(img, (x, fill_y), (x + w, y + h), color, -1)
    cv2.putText(img, f"{label}: {value}%", (x - 5, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1)

def dist(p1, p2):
    """Euclidean distance between two (x, y) points."""
    return np.hypot(p1[0] - p2[0], p1[1] - p2[1])