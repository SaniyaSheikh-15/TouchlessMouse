from utils import draw_bar

# ===================== BRIGHTNESS SETUP =====================
brightness_available = False
current_brightness   = 50   # tracked internally for incremental control

try:
    from screen_brightness_control import set_brightness as _set_brightness
    brightness_available = True
    print("✅ Brightness control ready.")
except Exception:
    print("⚠ Brightness control unavailable on this display (external monitor or unsupported).")

# ===================== BRIGHTNESS CONTROL =====================
def adjust_brightness(direction):
    """
    Adjust screen brightness incrementally.
    direction: +1 = brighter, -1 = dimmer
    Returns updated brightness value.
    """
    global current_brightness, brightness_available

    if not brightness_available:
        return current_brightness

    step = 5
    current_brightness = max(0, min(100, current_brightness + (step * direction)))

    try:
        _set_brightness(current_brightness)
    except Exception:
        brightness_available = False
        print("⚠ Brightness control failed — disabling.")

    return current_brightness

def get_brightness():
    """Returns current tracked brightness level."""
    return current_brightness

def draw_brightness_bar(img, bri_pct):
    """Draw brightness bar on frame."""
    draw_bar(img, bri_pct, 80, 300, 22, 200, (0, 220, 255), "Bri")