import numpy as np
from utils import draw_bar

# ===================== VOLUME SETUP =====================
volume_control  = None
vol_min         = -65.25
vol_max         = 0.0
volume_available = False

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL

    devices          = AudioUtilities.GetSpeakers()
    interface        = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_control   = cast(interface, POINTER(IAudioEndpointVolume))
    vol_min, vol_max = volume_control.GetVolumeRange()[:2]
    volume_available = True
    print("✅ Volume control ready.")
except Exception as e:
    print(f"⚠ Volume control unavailable: {e}")

# ===================== VOLUME CONTROL =====================
def adjust_volume(direction):
    """
    Adjust system volume incrementally.
    direction: +1 = louder, -1 = quieter
    """
    if not volume_available:
        return
    current = volume_control.GetMasterVolumeLevel()
    new_vol = current + (1.5 * direction)
    new_vol = max(vol_min, min(vol_max, new_vol))
    volume_control.SetMasterVolumeLevel(new_vol, None)

def get_volume_percent():
    """Returns current volume as 0–100 integer."""
    if not volume_available:
        return 0
    current = volume_control.GetMasterVolumeLevel()
    return int(np.interp(current, [vol_min, vol_max], [0, 100]))

def draw_volume_bar(img, vol_pct):
    """Draw volume bar on frame."""
    draw_bar(img, vol_pct, 40, 300, 22, 200, (100, 255, 100), "Vol")