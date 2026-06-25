import pyautogui
import numpy as np
import pygame
import os
import cv2
import time

# ===================== CONFIG =====================
pyautogui.FAILSAFE = False

# Cursor mapping region (camera pixels)
CAM_X_RANGE   = (100, 540)
CAM_Y_RANGE   = (100, 380)

# Click threshold (pixel distance between landmarks)
CLICK_THRESH   = 40

# Click cooldown to avoid repeated triggers
CLICK_COOLDOWN = 0.8
_last_click_time = 0

# ===================== SOUND =====================
pygame.mixer.init()
_click_sound = None
if os.path.exists("click.mp3"):
    _click_sound = pygame.mixer.Sound("click.mp3")
else:
    print("⚠ click.mp3 not found — running without sound.")

def _play_click():
    if _click_sound:
        _click_sound.play()

# ===================== SCREEN =====================
screen_w, screen_h = pyautogui.size()

# ===================== CURSOR MOVEMENT =====================
def move_cursor(lmList):
    """Move cursor using index finger tip (landmark 8)."""
    index_x = lmList[8][1]
    index_y = lmList[8][2]
    screen_x = np.interp(index_x, CAM_X_RANGE, (0, screen_w))
    screen_y = np.interp(index_y, CAM_Y_RANGE, (0, screen_h))
    pyautogui.moveTo(screen_x, screen_y, duration=0.05)

# ===================== CLICKS =====================
def check_left_click(lmList):
    """Left Click: Thumb (4) + Ring finger (16) pinch."""
    global _last_click_time
    thumb_x, thumb_y   = lmList[4][1],  lmList[4][2]
    ring_x,  ring_y    = lmList[16][1], lmList[16][2]
    if np.hypot(thumb_x - ring_x, thumb_y - ring_y) < CLICK_THRESH:
        if time.time() - _last_click_time > CLICK_COOLDOWN:
            pyautogui.click()
            _play_click()
            _last_click_time = time.time()
            return True
    return False

def check_right_click(lmList):
    """Right Click: Thumb (4) + Middle finger (12) pinch."""
    global _last_click_time
    thumb_x,  thumb_y  = lmList[4][1],  lmList[4][2]
    middle_x, middle_y = lmList[12][1], lmList[12][2]
    if np.hypot(thumb_x - middle_x, thumb_y - middle_y) < CLICK_THRESH:
        if time.time() - _last_click_time > CLICK_COOLDOWN:
            pyautogui.rightClick()
            _play_click()
            _last_click_time = time.time()
            return True
    return False

# ===================== SCROLL =====================
_prev_middle_y = 0

def check_scroll(lmList):
    """Scroll using middle finger (12) vertical movement."""
    global _prev_middle_y
    middle_y = lmList[12][2]
    status   = None
    if _prev_middle_y != 0:
        diff_y = middle_y - _prev_middle_y
        if abs(diff_y) > 2:   # ignore tiny jitter
            pyautogui.scroll(int(-diff_y * 2))
            status = "SCROLL DOWN ↓" if diff_y > 0 else "SCROLL UP ↑"
    _prev_middle_y = middle_y
    return status

# ===================== HUD =====================
def draw_cursor_dot(img, lmList):
    """Draw dot on index fingertip."""
    cx, cy = lmList[8][1], lmList[8][2]
    cv2.circle(img, (cx, cy), 8, (0, 255, 255), -1)