import cv2
import numpy as np
import time
import fingers_module as fm
import autopy


prev_time = 0
cap = cv2.VideoCapture(0)
# set webcam height and width
cam_width, cam_height = 640, 480
cap.set(3, cam_width)
cap.set(4, cam_height)
# find screen size
screen_width, screen_height = autopy.screen.size()
# define frame for cam in which the mouse should be controlled
frame = 80
# mouse move smooth
smoothening = 5
prev_x, prev_y = 0, 0
curr_x, curr_y = 0, 0

fingers = fm.Fingers(max_num_hands=1, detection_confidence=0.7)

while cap.isOpened():
    success, img = cap.read()
    # flip frame around the y-axis to reverse webcam effect
    img = cv2.flip(img, 1)
    # find hand and its landmarks
    img = fingers.find_hands(img)
    landmarks, _ = fingers.find_position(img, False)

    if len(landmarks) != 0:
        # identify up fingers
        up_fingers = fingers.identify_up_fingers()
        # find the tip of the index and middle fingers
        index = landmarks[fingers.index_tip_id][1:]
        middle = landmarks[fingers.middle_tip_id][1:]
        # extract x-y coordinates from index and middle fingers
        xi, yi = index
        xm, ym = middle
        # draw frame
        cv2.rectangle(img, (frame, frame), (cam_width-frame, cam_height-frame), (255, 0, 255), 2)
        # move mode when index only up, click when both index and middle fingers are up
        # move mode
        if fingers.index and not fingers.middle:
            # scale frame size to screen size
            x = np.interp(xi, (frame, cam_width-frame), (0, screen_width))
            y = np.interp(yi, (frame, cam_height-frame), (0, screen_height))
            # smoothen
            curr_x = prev_x + (x - prev_x) / smoothening
            curr_y = prev_x + (y - prev_y) / smoothening
            # if frame is not flipped --> autopy.mouse.smooth_move(cam_width-x, y)
            autopy.mouse.smooth_move(curr_x, curr_y)
            cv2.circle(img, (xi, yi), 10, (255, 0, 255), cv2.FILLED)
            x_prev, y_prev = curr_x, curr_y
        # click mode
        if fingers.index and fingers.middle:
            distance, img, points = fingers.find_distance(fingers.index_tip_id, fingers.middle_tip_id, img)
            # click if distance between index and middle fingers are below a threshold
            if distance < 25:
                cv2.circle(img, points[-2:], 10, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click(button=autopy.mouse.Button.LEFT)

    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time

    cv2.putText(img, f"fps: {int(fps)}", (50, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 3)
    cv2.imshow('virtual mouse', img)

    if cv2.waitKey(1) & 0XFF == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        break
