import cv2
import mediapipe as mp

class HandDetector:
    """
    Wraps MediaPipe Hands for easy landmark detection and hand type identification.
    """
    def __init__(self, maxHands=2, detectionCon=0.7, trackCon=0.7):
        self.mpHands = mp.solutions.hands
        self.hands   = self.mpHands.Hands(
            static_image_mode=False,
            max_num_hands=maxHands,
            min_detection_confidence=detectionCon,
            min_tracking_confidence=trackCon
        )
        self.mpDraw  = mp.solutions.drawing_utils
        self.results = None

    def findHands(self, img, draw=True):
        """Process frame and optionally draw landmarks. Returns annotated frame."""
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if draw and self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, hand_no=0):
        """
        Returns list of (id, x, y) for each landmark of specified hand.
        Pixel coordinates based on frame size.
        """
        lmList = []
        if self.results and self.results.multi_hand_landmarks:
            if hand_no < len(self.results.multi_hand_landmarks):
                h, w, _ = img.shape
                for id, lm in enumerate(self.results.multi_hand_landmarks[hand_no].landmark):
                    lmList.append((id, int(lm.x * w), int(lm.y * h)))
        return lmList

    def getHandType(self, hand_no=0):
        """Returns 'Left' or 'Right' for specified hand index."""
        if self.results and self.results.multi_handedness:
            if hand_no < len(self.results.multi_handedness):
                return self.results.multi_handedness[hand_no].classification[0].label
        return None

    def handCount(self):
        """Returns number of detected hands."""
        if self.results and self.results.multi_hand_landmarks:
            return len(self.results.multi_hand_landmarks)
        return 0