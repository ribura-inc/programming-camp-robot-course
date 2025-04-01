import random
import time

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

# モータードライバのピン設定
# モータードライバのピン設定（PWM制御に変更）
left_forward = PWMOutputDevice(15)
left_backward = PWMOutputDevice(14)
right_forward = PWMOutputDevice(23)
right_backward = PWMOutputDevice(18)


# サーボモーターの設定（射出用）
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

# カメラ初期化
cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    print("Failed to open camera.")
    exit(1)

# 状態管理用変数
state = "search_rotate"
state_start_time = time.time()
rotation_direction = random.choice([1, -1])


def launch():
    """射出動作を実施する."""
    print("launch")
    servo.angle = SERVO_MIN_ANGLE
    time.sleep(0.4)
    print("reset")
    servo.angle = SERVO_MAX_ANGLE
    time.sleep(0.2)


def set_motor_speed(left_speed: float, right_speed: float):
    """左右モーターの速度を設定する."""
    # 前進のみ対応（必要に応じて後退にも拡張可能）
    left_forward.value = max(0, min(1, left_speed))
    left_backward.value = 0
    right_forward.value = max(0, min(1, right_speed))
    right_backward.value = 0


def stop():
    """モーターを停止する."""
    left_forward.value = 0
    left_backward.value = 0
    right_forward.value = 0
    right_backward.value = 0


def detect_object():
    """カメラ画像から物体を検出する."""
    ret, frame = cap.read()
    if not ret:
        print("Failed to open camera.")
        exit(1)

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


def run():
    """メインループを実行する."""
    global state, state_start_time, rotation_direction
    try:
        while True:
            current_time = time.time()
            detected, centroid, area_ratio, _ = detect_object()

            if detected and centroid is not None:
                print(detected, centroid, area_ratio)
                if state != "tracking":
                    state = "tracking"
                    state_start_time = current_time
                set_motor_speed(1.0, 1.0)
                if area_ratio > 0.1 and (current_time - state_start_time >= 2.0):
                    stop()
                    launch()
                    break
            else:
                if state not in ["search_rotate", "search_forward"]:
                    state = "search_rotate"
                    state_start_time = current_time
                    rotation_direction = random.choice([1, -1])
                # search_rotate 時の回転制御も PWM に置き換え
                if state == "search_rotate":
                    if rotation_direction == 1:
                        left_forward.value = 0.8
                        left_backward.value = 0
                        right_forward.value = 0
                        right_backward.value = 0.8
                    else:
                        left_forward.value = 0
                        left_backward.value = 0.8
                        right_forward.value = 0.8
                        right_backward.value = 0

                    if current_time - state_start_time >= 1.5:
                        state = "search_forward"
                        state_start_time = current_time
                elif state == "search_forward":
                    set_motor_speed(0.9, 0.9)
                    if current_time - state_start_time >= 2.0:
                        state = "search_rotate"
                        state_start_time = current_time
                        rotation_direction = random.choice([1, -1])
            time.sleep(0.02)
    except KeyboardInterrupt:
        print("プログラムを終了します")
    finally:
        cap.release()  # 注意：これを忘れると、USBの抜き差しが必要になってしまう！！
        stop()


if __name__ == "__main__":
    run()
