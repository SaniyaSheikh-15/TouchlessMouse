import cv2
from utils import draw_bar

# ===================== BRIGHTNESS SETUP =====================
brightness_available = False

try:
    import screen_brightness_control as sbc
    brightness_available = True
    print("✅ Brightness control ready.")
except Exception:
    print("⚠ Brightness control unavailable (external monitor or unsupported).")

# ===================== BRIGHTNESS CONTROL =====================
def handle_brightness(lmList, img):
    """
    Brightness control using Left Hand finger positions:
    - Middle finger (12) DOWN + Ring finger (16) UP  → Brightness Down
    - Ring finger (16) DOWN + Middle finger (12) UP  → Brightness Up
    - Otherwise → Hold (no change)
    Returns status string.
    """
    if not brightness_available:
        return ""

    index_y  = lmList[8][2]
    middle_y = lmList[12][2]
    ring_y   = lmList[16][2]

    status = ""
    try:
        current = sbc.get_brightness(display=0)[0]

        if middle_y > index_y and ring_y < index_y:
            # Middle below index, ring above index = Brightness Down
            sbc.set_brightness(max(0, current - 2))
            status = "Brightness Down 🌙"

        elif ring_y > index_y and middle_y < index_y:
            # Ring below index, middle above index = Brightness Up
            sbc.set_brightness(min(100, current + 2))
            status = "Brightness Up ☀"

        else:
            status = "Brightness Hold"

        draw_bar(img, current, 80, 300, 22, 200, (0, 220, 255), "Bri")

    except Exception:
        pass

    return status