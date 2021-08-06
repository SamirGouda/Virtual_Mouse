import cv2
import mediapipe as mp
import time
import math


class HandDetector:
    def __init__(self, mode=False, max_num_hands=2, detection_confidence=0.5, track_confidence=0.5):
        self.mode = mode
        self.max_num_hands = max_num_hands
        self.detection_confidence = detection_confidence
        self.track_confidence = track_confidence
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=self.mode,
                                         max_num_hands=self.max_num_hands,
                                         min_detection_confidence=self.detection_confidence,
                                         min_tracking_confidence=self.track_confidence)
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None
        self.landmarks = []

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        # print(results.multi_hand_landmarks)
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)

        return img

    def find_position(self, img, hand_no=0, draw=True):
        x_list = []
        y_list = []
        bounding_box = []
        self.landmarks = []
        if self.results.multi_hand_landmarks:
            hand_lms = self.results.multi_hand_landmarks[hand_no]
            for lm_id, landmark in enumerate(hand_lms.landmark):
                # print(id, landmark)
                height, width, channels = img.shape
                cx, cy = int(landmark.x * width), int(landmark.y * height)
                # print(id, cx, cy)
                x_list.append(cx)
                y_list.append(cy)
                self.landmarks.append([lm_id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 2, (0, 0, 255), cv2.FILLED)
            xmin, xmax = min(x_list), max(x_list)
            ymin, ymax = min(y_list), max(y_list)
            bounding_box = [xmin, ymin, xmax, ymax]
            if draw:
                cv2.rectangle(img, (xmin-10, ymin-10), (xmax+10, ymax+10), (0, 255, 0), 2)

        return self.landmarks, bounding_box

    def find_distance(self, p1, p2, img, draw=True):
        x1, y1 = self.landmarks[p1][1:]
        x2, y2 = self.landmarks[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        if draw:
            cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
            cv2.circle(img, (cx, cy), 10, (0, 0, 255), cv2.FILLED)
        length = math.hypot(x2-x1, y2-y1)
        return length, img, [x1, y1, x2, y2, cx, cy]


def main():
    prev_time = 0
    cap = cv2.VideoCapture(0)
    detector = HandDetector()
    while cap.isOpened():
        success, img = cap.read()
        img = detector.find_hands(img)
        lm_list = detector.find_position(img)
        if len(lm_list) != 0:
            print(lm_list[4])
            length, _, _ = detector.find_distance(8, 12, img)
            print(length)
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 255), 3)
        cv2.imshow('image', img)
        if cv2.waitKey(1) & 0XFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            break


if __name__ == '__main__':
    main()
