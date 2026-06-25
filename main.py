import cv2
import os
import logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.getLogger('tensorflow').setLevel(logging.FATAL)

from hand_detector      import HandDetector
from mouse_control      import move_cursor, check_left_click, check_right_click, check_scroll, draw_cursor_dot
from volume_control     import handle_volume
from brightness_control import handle_brightness

# ===================== CAMERA SETUP =====================
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

detector = HandDetector(maxHands=2, detectionCon=0.7, trackCon=0.7)

# ===================== STARTUP MESSAGE =====================
print("✅ Touchless System Running — Press ESC to quit")
print("─" * 55)
print("RIGHT HAND:")
print("  ☝  Index finger          → Move cursor")
print("  👍 Thumb + Ring finger    → Left Click")
print("  👍 Thumb + Middle finger  → Right Click")
print("  ✌  Middle finger move     → Scroll")
print("LEFT HAND:")
print("  🤏 Thumb + Index spread   → Volume control")
print("  💡 Middle down, Ring up   → Brightness Down")
print("  💡 Ring down, Middle up   → Brightness Up")
print("─" * 55)

# ===================== MAIN LOOP =====================
while True:
    success, img = cap.read()
    if not success:
        continue

    img = cv2.flip(img, 1)
    img = detector.findHands(img)

    status_right = ""
    status_left  = ""

    try:
        for hand_no in range(detector.handCount()):
            handType = detector.getHandType(hand_no)
            lmList   = detector.findPosition(img, hand_no)

            if not lmList or len(lmList) < 17:
                continue

            # ─────────────────────────────────────
            # RIGHT HAND — Mouse Control
            # ─────────────────────────────────────
            if handType == "Right":
                move_cursor(lmList)
                draw_cursor_dot(img, lmList)

                if check_left_click(lmList):
                    status_right = "LEFT CLICK"
                elif check_right_click(lmList):
                    status_right = "RIGHT CLICK"
                else:
                    scroll_status = check_scroll(lmList)
                    if scroll_status:
                        status_right = scroll_status

            # ─────────────────────────────────────
            # LEFT HAND — Volume + Brightness
            # ─────────────────────────────────────
            elif handType == "Left":
                vol_status = handle_volume(lmList, img)
                bri_status = handle_brightness(lmList, img)
                status_left = vol_status or bri_status

    except Exception as e:
        print(f"Runtime error: {e}")

    # ── HUD ──
    img_h, img_w = img.shape[:2]

    if status_right:
        color = (0, 255, 150) if "CLICK" in status_right else (255, 220, 0)
        cv2.putText(img, f"R: {status_right}", (img_w - 300, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

    if status_left:
        cv2.putText(img, f"L: {status_left}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 220, 255), 2)

    # Instructions strip
    cv2.rectangle(img, (0, img_h - 35), (img_w, img_h), (30, 30, 30), -1)
    cv2.putText(img,
        "R: Idx=Move | T+Ring=LClick | T+Mid=RClick | Mid Move=Scroll  |  L: T+Idx=Vol | Mid/Ring=Bri",
        (10, img_h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 200, 200), 1)

    cv2.imshow("Touchless System Control", img)

    if cv2.waitKey(1) & 0xFF == 27:   # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
print("👋 Touchless System closed.")