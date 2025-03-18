import random
import time

import cv2
import numpy as np
from gpiozero import AngularServo, DigitalOutputDevice, PWMOutputDevice
from gpiozero.pins.pigpio import PiGPIOFactory

# 定数定義
CAMERA_INDEX = 0
SERVO_PIN = 12
SERVO_MIN_ANGLE = 85
SERVO_MAX_ANGLE = 0
SERVO_MIN_PULSE = 0.5 / 1000
SERVO_MAX_PULSE = 2.4 / 1000
SERVO_FRAME_WIDTH = 1 / 50

AIN1_PIN = 14
AIN2_PIN = 15
PWMA_PIN = 18
BIN1_PIN = 8
BIN2_PIN = 25
PWMB_PIN = 7

LOWER_HSV = np.array([30, 100, 100])  # TODO: 適切な値に変更
UPPER_HSV = np.array([60, 255, 255])  # TODO: 適切な値に変更

# モータードライバのピン設定
AIN1 = DigitalOutputDevice(AIN1_PIN)
AIN2 = DigitalOutputDevice(AIN2_PIN)
PWMA = PWMOutputDevice(PWMA_PIN)
BIN1 = DigitalOutputDevice(BIN1_PIN)
BIN2 = DigitalOutputDevice(BIN2_PIN)
PWMB = PWMOutputDevice(PWMB_PIN)

# サーボモーターの設定（射出用）
factory = PiGPIOFactory()
servo = AngularServo(
    SERVO_PIN,
    min_angle=SERVO_MIN_ANGLE,
    max_angle=SERVO_MAX_ANGLE,
    initial_angle=SERVO_MAX_ANGLE,
    min_pulse_width=SERVO_MIN_PULSE,
    max_pulse_width=SERVO_MAX_PULSE,
    frame_width=SERVO_FRAME_WIDTH,
    pin_factory=factory,
)
servo.angle = SERVO_MAX_ANGLE

# カメラ初期化
cap = cv2.VideoCapture(CAMERA_INDEX)

# 状態管理用変数
state = "search_rotate"
state_start_time = time.time()
rotation_direction = random.choice([1, -1])


def launch():
    """射出動作を実施する."""
    print("launch")
    servo.angle = SERVO_MIN_ANGLE
    time.sleep(0.2)
    print("reset")
    servo.angle = SERVO_MAX_ANGLE
    time.sleep(0.1)


def set_motor_speed(left_speed: float, right_speed: float):
    """左右モーターの速度を設定する."""
    AIN1.off()
    AIN2.on()
    BIN1.off()
    BIN2.on()
    PWMA.value = max(0, min(1, left_speed))
    PWMB.value = max(0, min(1, right_speed))


def stop():
    """モーターを停止する."""
    AIN1.on()
    AIN2.on()
    BIN1.on()
    BIN2.on()
    PWMA.value = 0
    PWMB.value = 0


def detect_object():
    """カメラ画像から物体を検出する."""
    ret, frame = cap.read()
    if not ret:
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
            detected, centroid, area_ratio, frame = detect_object()

            if detected and centroid is not None:
                if state != "tracking":
                    state = "tracking"
                    state_start_time = current_time
                set_motor_speed(0.5, 0.5)
                if area_ratio > 0.1 and (current_time - state_start_time >= 2.0):
                    stop()
                    launch()
                    break
            else:
                if state not in ["search_rotate", "search_forward"]:
                    state = "search_rotate"
                    state_start_time = current_time
                    rotation_direction = random.choice([1, -1])
                if state == "search_rotate":
                    if rotation_direction == 1:
                        AIN1.on()
                        AIN2.off()
                        BIN1.off()
                        BIN2.on()
                    else:
                        AIN1.off()
                        AIN2.on()
                        BIN1.on()
                        BIN2.off()
                    PWMA.value = 0.3
                    PWMB.value = 0.3
                    if current_time - state_start_time >= 1.5:
                        state = "search_forward"
                        state_start_time = current_time
                elif state == "search_forward":
                    set_motor_speed(0.4, 0.4)
                    if current_time - state_start_time >= 2.0:
                        state = "search_rotate"
                        state_start_time = current_time
                        rotation_direction = random.choice([1, -1])
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("プログラムを終了します")
    finally:
        stop()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    run()
