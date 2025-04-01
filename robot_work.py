import cv2
import numpy as np
from gpiozero import AngularServo, PWMOutputDevice
from gpiozero.pins.pigpio import PiGPIOFactory

# 定数定義
CAMERA_INDEX = 0
SERVO_PIN = 4
SERVO_MIN_ANGLE = -90
SERVO_MAX_ANGLE = 0
SERVO_MIN_PULSE = 0.5 / 1000
SERVO_MAX_PULSE = 2.4 / 1000
SERVO_FRAME_WIDTH = 1 / 50

LOWER_HSV = np.array([65, 110, 105])  # TODO: 適切な値に変更
UPPER_HSV = np.array([105, 200, 230])  # TODO: 適切な値に変更

### 初期化処理 (変更しなくてOK）###
cap = cv2.VideoCapture(CAMERA_INDEX)

left_forward = PWMOutputDevice(15)
left_backward = PWMOutputDevice(14)
right_forward = PWMOutputDevice(23)
right_backward = PWMOutputDevice(18)

factory = PiGPIOFactory()
servo = AngularServo(
    SERVO_PIN,
    initial_angle=SERVO_MAX_ANGLE,
    min_pulse_width=SERVO_MIN_PULSE,
    max_pulse_width=SERVO_MAX_PULSE,
    frame_width=SERVO_FRAME_WIDTH,
    pin_factory=factory,
)
servo.angle = SERVO_MAX_ANGLE

### 以下に関数を実装する ###


def move_forward(speed):
    # [TODO] 前進する処理を実装する
    raise NotImplementedError


def rotate_left(speed):
    # [TODO] 左に回転する処理を実装する
    raise NotImplementedError


def rotate_right(speed):
    # [TODO] 右に回転する処理を実装する
    raise NotImplementedError


def stop():
    # [TODO] モーターを停止する処理を実装する
    raise NotImplementedError


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


def launch():
    # [TODO] ミサイル発射の処理を実装する
    raise NotImplementedError


### 下記のアルゴリズムを自由に実装してみよう！！！ ###
def run():
    while True:
        # [TODO]
        raise NotImplementedError


### Pythonファイルが実行された場合下記が実行される ###
if __name__ == "__main__":
    run()
