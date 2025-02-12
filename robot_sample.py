import random
from time import sleep

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

MOVE_SPEED = 0.8
ROTATE_SPEED = 0.7
SEARCH_ATTEMPTS = 3
COLOR_THRESHOLD = 0.05
CLOSE_DISTANCE_THRESHOLD = 0.2
SLEEP_INTERVAL = 0.1

LOWER_COLOR1 = np.array([90, 100, 100])  # 水色の下限
UPPER_COLOR1 = np.array([120, 255, 255])  # 青色の上限


class ColorObjectTracker:
    def __init__(self):
        # カメラ初期化
        self.cap = cv2.VideoCapture(CAMERA_INDEX)

        # モータードライバのピン設定
        self.AIN1 = DigitalOutputDevice(AIN1_PIN)
        self.AIN2 = DigitalOutputDevice(AIN2_PIN)
        self.PWMA = PWMOutputDevice(PWMA_PIN)
        self.BIN1 = DigitalOutputDevice(BIN1_PIN)
        self.BIN2 = DigitalOutputDevice(BIN2_PIN)
        self.PWMB = PWMOutputDevice(PWMB_PIN)

        # サーボモーターの設定（ロケットランチャー用）
        factory = PiGPIOFactory()
        self.servo = AngularServo(
            SERVO_PIN,
            min_angle=SERVO_MIN_ANGLE,
            max_angle=SERVO_MAX_ANGLE,
            initial_angle=SERVO_MAX_ANGLE,
            min_pulse_width=SERVO_MIN_PULSE,
            max_pulse_width=SERVO_MAX_PULSE,
            frame_width=SERVO_FRAME_WIDTH,
            pin_factory=factory,
        )
        self.servo.angle = SERVO_MAX_ANGLE

        # 速度設定
        self.speed = MOVE_SPEED
        self.rotate_speed = ROTATE_SPEED

    def move_forward(self):
        self.AIN1.off()
        self.AIN2.on()
        self.BIN1.off()
        self.BIN2.on()
        self.PWMA.value = self.speed
        self.PWMB.value = self.speed

    def rotate_left(self):
        self.AIN1.on()
        self.AIN2.off()
        self.BIN1.off()
        self.BIN2.on()
        self.PWMA.value = self.rotate_speed
        self.PWMB.value = self.rotate_speed

    def rotate_right(self):
        self.AIN1.off()
        self.AIN2.on()
        self.BIN1.on()
        self.BIN2.off()
        self.PWMA.value = self.rotate_speed
        self.PWMB.value = self.rotate_speed

    def stop(self):
        self.AIN1.on()
        self.AIN2.on()
        self.BIN1.on()
        self.BIN2.on()
        self.PWMA.value = 0
        self.PWMB.value = 0

    def detect_color_object(self):
        ret, frame = self.cap.read()
        if not ret:
            return False

        # HSV変換
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, LOWER_COLOR1, UPPER_COLOR1)

        # 色の占有率を計算
        color_ratio = np.sum(mask > 0) / (frame.shape[0] * frame.shape[1])

        return color_ratio > COLOR_THRESHOLD

    def launch(self):
        print("launch")
        self.servo.angle = SERVO_MIN_ANGLE
        sleep(0.2)

        print("reset")
        self.servo.angle = SERVO_MAX_ANGLE
        sleep(0.1)
        return

    def run(self):
        try:
            while True:
                if self.detect_color_object():
                    print("色物体を検出！近づきます")
                    self.move_forward()
                    sleep(SLEEP_INTERVAL)

                    if self.detect_color_object():
                        color_ratio = np.sum(
                            cv2.inRange(
                                cv2.cvtColor(self.cap.read()[1], cv2.COLOR_BGR2HSV),
                                LOWER_COLOR1,
                                UPPER_COLOR1,
                            )
                            > 0
                        ) / (self.cap.read()[1].shape[0] * self.cap.read()[1].shape[1])
                        if color_ratio > CLOSE_DISTANCE_THRESHOLD:
                            print("近づきました！発射！！！")
                            self.stop()
                            self.launch()
                            exit()
                else:
                    print("色物体が見つかりません。探索します")
                    self.stop()
                    self.rotate_left()
                    sleep(0.02 * random.randint(1, 5))
                    self.stop()

        except KeyboardInterrupt:
            print("プログラムを終了します")
        finally:
            self.stop()
            self.cap.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    tracker = ColorObjectTracker()
    tracker.run()
