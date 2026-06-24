import pyautogui
import numpy as np
import pygame
import os
import cv2

# ===================== CONFIG =====================
pyautogui.FAILSAFE = False

SMOOTHING         = 0.18   # 0 = no movement, 1 = no smoothing
DEAD_ZONE         = 8      # pixels — ignore micro-tremors below this
LEFT_CLICK_THRESH  = 45    # pinch distance in camera pixels
RIGHT_CLICK_THRESH = 45
SCROLL_THRESH      = 45
SCROLL_AMOUNT      = 20
CLICK_COOLDOWN     = 0.8   # seconds between clicks
GESTURE_HOLD       = 0.3   # seconds before gesture resets to idle
scroll_cooldown    = 0.08  # seconds between scroll ticks

# ===================== SOUND =====================
pygame.mixer.init()
_click_sound = None
_sound_file  = "click.mp3"

if os.path.exists(_sound_file):
    _click_sound = pygame.mixer.Sound(_sound_file)
else:
    print("⚠ click.mp3 not found — running without click sound.")

def play_click_sound():
    if _click_sound:
        _click_sound.play()

# ===================== STATE =====================
screen_w, screen_h = pyautogui.size()
smooth_x  = screen_w // 2
smooth_y  = screen_h // 2

# ===================== MOUSE MOVEMENT =====================
def move_cursor(lm, img_w, img_h):
    """
    Move cursor smoothly using index finger tip (landmark 8).
    Applies exponential smoothing + dead zone filtering.
    Returns (smooth_x, smooth_y) for external use.
    """
    global smooth_x, smooth_y

    index_x, index_y = lm[8]

    # Map camera space → screen space (40px border margin)
    raw_x = np.interp(index_x, [40, img_w - 40], [0, screen_w])
    raw_y = np.interp(index_y, [40, img_h - 40], [0, screen_h])

    delta_x = raw_x - smooth_x
    delta_y = raw_y - smooth_y

    # Only move if beyond dead zone
    if abs(delta_x) > DEAD_ZONE or abs(delta_y) > DEAD_ZONE:
        smooth_x += SMOOTHING * delta_x
        smooth_y += SMOOTHING * delta_y
        pyautogui.moveTo(int(smooth_x), int(smooth_y))

    # Draw yellow dot on index tip
    return smooth_x, smooth_y

# ===================== CLICKS =====================
def do_left_click():
    pyautogui.click()
    play_click_sound()

def do_right_click():
    pyautogui.rightClick()
    play_click_sound()

# ===================== SCROLL =====================
def do_scroll(direction):
    """
    direction: +1 = scroll up, -1 = scroll down
    """
    pyautogui.scroll(direction * SCROLL_AMOUNT)

# ===================== HUD =====================
def draw_cursor_dot(img, lm):
    """Draw a dot on the index fingertip for visual feedback."""
    index_x, index_y = lm[8]
    cv2.circle(img, (index_x, index_y), 8, (0, 255, 255), -1)