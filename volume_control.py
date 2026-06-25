import numpy as np
import math
import cv2
from utils import draw_bar

# ===================== VOLUME SETUP =====================
volume_control   = None
vol_min, vol_max = -65.25, 0.0
volume_available = False

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL, cast, POINTER
    devices          = AudioUtilities.GetSpeakers()
    interface        = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_control   = cast(interface, POINTER(IAudioEndpointVolume))
    vol_min, vol_max = volume_control.GetVolumeRange()[:2]
    volume_available = True
    print("✅ Volume control ready.")
except Exception as e:
    print(f"⚠ Volume control unavailable: {e}")

# ===================== VOLUME CONTROL =====================
def handle_volume(lmList, img):
    """
    Volume control using Left Hand — Thumb (4) + Index (8) distance.
    Wider gap = louder, closer = quieter.
    Returns status string.
    """
    if not volume_available:
        return ""

    thumb_x,  thumb_y  = lmList[4][1],  lmList[4][2]
    index_x,  index_y  = lmList[8][1],  lmList[8][2]

    length = math.hypot(thumb_x - index_x, thumb_y - index_y)
    vol    = np.interp(length, [20, 200], [vol_min, vol_max])
    vol    = max(vol_min, min(vol_max, vol))
    volume_control.SetMasterVolumeLevel(vol, None)

    vol_pct = int(np.interp(length, [20, 200], [0, 100]))
    vol_pct = max(0, min(100, vol_pct))

    # Draw line between thumb and index
    cv2.line(img, (thumb_x, thumb_y), (index_x, index_y), (100, 255, 100), 2)
    draw_bar(img, vol_pct, 40, 300, 22, 200, (100, 255, 100), "Vol")

    return f"Volume {vol_pct}%"