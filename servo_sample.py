from time import sleep

from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory

# SG90のピン設定
SERVO_PIN = 12  # SG90のピン番号

# おまじない
factory = PiGPIOFactory()

# min_pulse_width, max_pulse_width, frame_width => SG90仕様
servo = AngularServo(
    SERVO_PIN,
    min_pulse_width=0.5 / 1000,
    max_pulse_width=2.4 / 1000,
    frame_width=20 / 1000,
    initial_angle=0,
    pin_factory=factory,
)


servo.angle = 60
sleep(1.0)
servo.angle = -60
sleep(1.0)
