#!/usr/bin/env python3

# セットアップ：https://www.notion.so/ribura/1c078ae31335800f844fddba40d46527?pvs=4

from gpiozero import PWMOutputDevice, AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory

# 全モーターを停止
left_forward = PWMOutputDevice(15)
left_backward = PWMOutputDevice(14)
right_forward = PWMOutputDevice(23)
right_backward = PWMOutputDevice(18)
left_forward.value = 0
left_backward.value = 0
right_forward.value = 0
right_backward.value = 0

# サーボ0度へ
SERVO_PIN = 4
SERVO_MAX_ANGLE = 0
SERVO_MIN_PULSE = 0.5 / 1000
SERVO_MAX_PULSE = 2.4 / 1000
SERVO_FRAME_WIDTH = 1 / 50

factory = PiGPIOFactory()
servo = AngularServo(
    SERVO_PIN,
    max_angle=SERVO_MAX_ANGLE,
    initial_angle=SERVO_MAX_ANGLE,
    min_pulse_width=SERVO_MIN_PULSE,
    max_pulse_width=SERVO_MAX_PULSE,
    frame_width=SERVO_FRAME_WIDTH,
    pin_factory=factory,
)
servo.angle = SERVO_MAX_ANGLE
