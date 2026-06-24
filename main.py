import cv2
import mediapipe as mp
import time

# ── Import all modules ──
from utils             import build_landmark_list
from gestures          import detect_right_gesture, detect_left_gesture
from mouse_control     import (move_cursor, do_left_click, do_right_click,
                                do_scroll, draw_cursor_dot,
                                CLICK_COOLDOWN, RIGHT_CLICK_THRESH,
                                LEFT_CLICK_THRESH, SCROLL_AMOUNT,
                                GESTURE_HOLD, scroll_cooldown)
from volume_control    import adjust_volume, get_volume_percent, draw_volume_bar
from brightness_control import adjust_brightness, get_brightness, draw_brightness_bar

# ===================== CAMERA & MEDIAPIPE =====================
cap      = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands    = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75
)
draw = mp.solutions.drawing_utils

# ===================== STATE =====================
last_click_time      = 0
last_scroll_time     = 0
last_brightness_time = 0
BRIGHTNESS_COOLDOWN  = 0.15

gesture_state        = "idle"
gesture_reset_time   = 0

prev_two_finger_y    = 0
prev_three_finger_y  = 0

# ===================== MAIN LOOP =====================
print("✅ Touchless System Running — Press Q to quit")
print("─" * 55)
print("RIGHT HAND:")
print("  ☝  Index finger        → Move cursor")
print("  🤏 Thumb + Index        → Left Click")
print("  🤏 Thumb + Middle       → Right Click")
print("  ✌  Two fingers swipe ↑  → Scroll Up")
print("  ✌  Two fingers swipe ↓  → Scroll Down")
print("LEFT HAND:")
print("  🤟 Three fingers swipe ↑ → Volume Up")
print("  🤟 Three fingers swipe ↓ → Volume Down")
print("  👍 Fist + Thumb Up       → Brightness Up")
print("  👎 Fist + Thumb Down     → Brightness Down")
print("─" * 55)

while True:
    success, img = cap.read()
    if not success:
        continue

    img   = cv2.flip(img, 1)
    img_h, img_w = img.shape[:2]
    rgb   = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    status_right = ""
    status_left  = ""
    now          = time.time()

    try:
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                hand_label = results.multi_handedness[hand_idx].classification[0].label
                draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                lm = build_landmark_list(hand_landmarks, img_w, img_h)

                # ─────────────────────────────────────
                # RIGHT HAND — Mouse Control
                # ─────────────────────────────────────
                if hand_label == "Right":
                    move_cursor(lm, img_w, img_h)
                    draw_cursor_dot(img, lm)

                    gesture, scroll_dir, prev_two_finger_y = detect_right_gesture(
                        lm, gesture_state, gesture_reset_time,
                        last_click_time, last_scroll_time,
                        prev_two_finger_y, now,
                        LEFT_CLICK_THRESH, RIGHT_CLICK_THRESH,
                        SCROLL_AMOUNT, CLICK_COOLDOWN,
                        GESTURE_HOLD, scroll_cooldown
                    )

                    if gesture == "left_click":
                        do_left_click()
                        last_click_time    = now
                        gesture_state      = "left_click"
                        gesture_reset_time = now
                        status_right       = "LEFT CLICK"

                    elif gesture == "right_click":
                        do_right_click()
                        last_click_time    = now
                        gesture_state      = "right_click"
                        gesture_reset_time = now
                        status_right       = "RIGHT CLICK"

                    elif gesture in ("scroll_up", "scroll_down"):
                        do_scroll(scroll_dir)
                        last_scroll_time = now
                        status_right     = "SCROLL UP ↑" if scroll_dir > 0 else "SCROLL DOWN ↓"

                    elif gesture_state != "idle":
                        status_right = gesture_state.replace("_", " ").upper()

                    # Reset gesture state after hold period
                    if gesture_state != "idle" and now - gesture_reset_time > GESTURE_HOLD:
                        gesture_state = "idle"

                # ─────────────────────────────────────
                # LEFT HAND — Volume + Brightness
                # ─────────────────────────────────────
                elif hand_label == "Left":
                    gesture, vol_dir, bri_dir, prev_three_finger_y = detect_left_gesture(
                        lm, now, last_scroll_time, last_brightness_time,
                        prev_three_finger_y, scroll_cooldown, BRIGHTNESS_COOLDOWN
                    )

                    if gesture == "volume" and vol_dir != 0:
                        adjust_volume(vol_dir)
                        last_scroll_time = now
                        vol_pct          = get_volume_percent()
                        draw_volume_bar(img, vol_pct)
                        status_left = f"Volume {'Up ↑' if vol_dir > 0 else 'Down ↓'} {vol_pct}%"

                    elif gesture == "brightness" and bri_dir != 0:
                        bri_pct = adjust_brightness(bri_dir)
                        last_brightness_time = now
                        draw_brightness_bar(img, bri_pct)
                        status_left = f"Brightness {'Up ☀' if bri_dir > 0 else 'Down 🌙'} {bri_pct}%"

                    # Show bars even when not actively changing
                    elif gesture == "volume":
                        draw_volume_bar(img, get_volume_percent())
                    elif gesture == "brightness":
                        draw_brightness_bar(img, get_brightness())

        else:
            cv2.putText(img, "Place hand in view", (img_w // 2 - 130, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 80, 255), 2)

    except Exception as e:
        print(f"Runtime error: {e}")

    # ── HUD OVERLAY ──
    if status_right:
        color = (0, 255, 150) if "CLICK" in status_right else (255, 220, 0)
        cv2.putText(img, f"R: {status_right}", (img_w - 320, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

    if status_left:
        cv2.putText(img, f"L: {status_left}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 220, 255), 2)

    # Instructions strip
    cv2.rectangle(img, (0, img_h - 35), (img_w, img_h), (30, 30, 30), -1)
    cv2.putText(img,
        "R: Idx=Move | T+I=LClick | T+M=RClick | 2Swipe=Scroll  |  L: 3Swipe=Vol | Fist+Thumb=Bri",
        (10, img_h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

    cv2.imshow("Touchless System Control", img)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("👋 Touchless System closed.")