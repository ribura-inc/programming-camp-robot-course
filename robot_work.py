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
BIN1_PIN = 25
BIN2_PIN = 8
PWMB_PIN = 7


LOWER_COLOR1 = np.array([90, 100, 100])  # [TODO] 検出する色の下限を設定する
UPPER_COLOR1 = np.array([120, 255, 255])  # [TODO] 検出する色の上限を設定する

### 初期化処理 (変更しなくてOK）###

capture = cv2.VideoCapture(CAMERA_INDEX)
AIN1 = DigitalOutputDevice(AIN1_PIN)
AIN2 = DigitalOutputDevice(AIN2_PIN)
PWMA = PWMOutputDevice(PWMA_PIN)
BIN1 = DigitalOutputDevice(BIN1_PIN)
BIN2 = DigitalOutputDevice(BIN2_PIN)
PWMB = PWMOutputDevice(PWMB_PIN)

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


def detect_color_object() -> tuple[float, float] | None:
    """カメラ画像から特定の色を検出し、その中心座標(0~1)を返す. 見つからない場合はNoneを返す."""
    ret, frame = capture.read()
    if not ret:
        return False

    # 画像をHSVに変換
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_COLOR1, UPPER_COLOR1)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        # 最大面積の輪郭を取得
        max_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(max_contour)
        if M["m00"] != 0:
            cx = M["m10"] / M["m00"]
            cy = M["m01"] / M["m00"]
            return cx / frame.shape[1], cy / frame.shape[0]
    return None


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
