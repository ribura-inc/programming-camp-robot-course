import random
import time

import cv2
import numpy as np

LOWER_HSV = np.array([65, 110, 105])  # TODO: 適切な値に変更
UPPER_HSV = np.array([105, 200, 230])  # TODO: 適切な値に変更

# カメラ初期化
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Failed to open camera.")
    exit()

# 状態管理用変数
state = "search_rotate"
state_start_time = time.time()
rotation_direction = random.choice([1, -1])


def detect_object():
    """カメラ画像から物体を検出する."""
    ret, frame = cap.read()
    if not ret:
        print("Failed to read frame.")
        return False, None, 0.0, np.array([])

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_HSV, UPPER_HSV)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return False, None, 0.0, frame

    largest_contour = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest_contour)
    frame_area = frame.shape[0] * frame.shape[1]
    area_ratio = area / frame_area
    if area_ratio < 0.01:
        return False, None, area_ratio, frame

    M = cv2.moments(largest_contour)
    if M["m00"] == 0:
        return False, None, area_ratio, frame
    centroid_x = int(M["m10"] / M["m00"])
    centroid_y = int(M["m01"] / M["m00"])
    return True, (centroid_x, centroid_y), area_ratio, frame


if __name__ == "__main__":
    try:
        while True:
            detected, centroid, area_ratio, _ = detect_object()
            print(detected, centroid, area_ratio)
    except KeyboardInterrupt:
        cap.release()
