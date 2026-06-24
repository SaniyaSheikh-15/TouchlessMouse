from utils import dist

# ── RIGHT HAND GESTURE DETECTION ──

def detect_right_gesture(lm, gesture_state, gesture_reset_time,
                          last_click_time, last_scroll_time,
                          prev_two_finger_y, now,
                          LEFT_CLICK_THRESH, RIGHT_CLICK_THRESH,
                          SCROLL_AMOUNT, CLICK_COOLDOWN,
                          GESTURE_HOLD, scroll_cooldown):
    """
    Detects right hand gestures: left click, right click, scroll up/down.
    Returns: (gesture_name, scroll_direction, updated_prev_two_finger_y)
    """
    thumb  = lm[4]
    index  = lm[8]
    middle = lm[12]

    d_index_thumb  = dist(thumb, index)
    d_middle_thumb = dist(thumb, middle)
    two_finger_y   = (lm[8][1] + lm[12][1]) / 2

    gesture = None
    scroll_dir = 0  # -1 = down, +1 = up, 0 = none

    # Reset gesture state after hold period
    if gesture_state != "idle" and now - gesture_reset_time > GESTURE_HOLD:
        gesture_state = "idle"

    if gesture_state == "idle":

        # ── LEFT CLICK: Index + Thumb pinch ──
        if d_index_thumb < LEFT_CLICK_THRESH:
            if now - last_click_time > CLICK_COOLDOWN:
                gesture = "left_click"

        # ── RIGHT CLICK: Middle + Thumb pinch (index must NOT be pinching) ──
        elif d_middle_thumb < RIGHT_CLICK_THRESH and d_index_thumb > LEFT_CLICK_THRESH + 15:
            if now - last_click_time > CLICK_COOLDOWN:
                gesture = "right_click"

        # ── SCROLL: Both index + middle raised, detect swipe direction ──
        elif lm[8][1] < lm[5][1] and lm[12][1] < lm[9][1]:
            if now - last_scroll_time > scroll_cooldown:
                dy = two_finger_y - prev_two_finger_y
                if dy > 5:
                    scroll_dir = -1   # swipe down = scroll down
                    gesture = "scroll_down"
                elif dy < -5:
                    scroll_dir = 1    # swipe up = scroll up
                    gesture = "scroll_up"

    return gesture, scroll_dir, two_finger_y


# ── LEFT HAND GESTURE DETECTION ──

def detect_left_gesture(lm, now, last_scroll_time, last_brightness_time,
                         prev_three_finger_y, scroll_cooldown, BRIGHTNESS_COOLDOWN):
    """
    Detects left hand gestures: volume (3-finger swipe), brightness (thumb up/down).
    Returns: (gesture_name, volume_direction, brightness_direction, updated_prev_three_finger_y)
    gesture_name: 'volume' | 'brightness' | None
    volume_direction: -1 (down), +1 (up), 0 (none)
    brightness_direction: -1 (down), +1 (up), 0 (none)
    """
    index_up  = lm[8][1]  < lm[5][1]
    middle_up = lm[12][1] < lm[9][1]
    ring_up   = lm[16][1] < lm[13][1]
    pinky_up  = lm[20][1] < lm[17][1]

    gesture       = None
    vol_dir       = 0
    bri_dir       = 0
    three_finger_y = prev_three_finger_y

    # ── VOLUME: Index + Middle + Ring raised, pinky down ──
    if index_up and middle_up and ring_up and not pinky_up:
        gesture        = "volume"
        three_finger_y = (lm[8][1] + lm[12][1] + lm[16][1]) / 3
        if now - last_scroll_time > scroll_cooldown:
            dy = three_finger_y - prev_three_finger_y
            if dy < -6:
                vol_dir = 1     # swipe up = volume up
            elif dy > 6:
                vol_dir = -1    # swipe down = volume down

    # ── BRIGHTNESS: Fist (all fingers down), detect thumb direction ──
    elif not index_up and not middle_up and not ring_up and not pinky_up:
        gesture     = "brightness"
        wrist_y     = lm[0][1]
        thumb_tip_y = lm[4][1]
        if now - last_brightness_time > BRIGHTNESS_COOLDOWN:
            if thumb_tip_y < wrist_y - 40:      # thumb pointing up = brighter
                bri_dir = 1
            elif thumb_tip_y > wrist_y + 10:    # thumb pointing down = dimmer
                bri_dir = -1

    return gesture, vol_dir, bri_dir, three_finger_y