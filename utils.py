import numpy as np
import cv2

def dist(p1, p2):
    """Euclidean distance between two (x, y) points."""
    return np.hypot(p1[0] - p2[0], p1[1] - p2[1])

def draw_bar(img, value, x, y, w, h, color, label):
    """Draw a vertical progress bar on the frame."""
    cv2.rectangle(img, (x, y), (x + w, y + h), (200, 200, 200), 2)
    fill_y = int(y + h - (value / 100) * h)
    cv2.rectangle(img, (x, fill_y), (x + w, y + h), color, -1)
    cv2.putText(img, f"{label}: {value}%", (x - 5, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1)

def fingers_up(lm):
    """
    Returns list of booleans [thumb, index, middle, ring, pinky].
    True = finger is raised.
    """
    tips = [4, 8, 12, 16, 20]
    mcps = [2, 5,  9, 13, 17]
    result = []
    # Thumb: compare x (horizontal direction)
    result.append(lm[4][0] > lm[3][0])
    # Other fingers: tip Y above MCP Y = finger is up
    for tip, mcp in zip(tips[1:], mcps[1:]):
        result.append(lm[tip][1] < lm[mcp][1])
    return result

def build_landmark_list(hand_landmarks, img_w, img_h):
    """Convert MediaPipe landmarks to a list of (x, y) pixel coordinates."""
    lm = []
    for lm_data in hand_landmarks.landmark:
        lm.append((int(lm_data.x * img_w), int(lm_data.y * img_h)))
    return lm