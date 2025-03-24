from time import sleep

from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory

# SG90のピン設定
SERVO_PIN = 4  # SG90-1



def main():
    factory = PiGPIOFactory()
    # min_pulse_width, max_pulse_width, frame_width =>SG90仕様
    servo = AngularServo(
        SERVO_PIN,
        initial_angle=0,
        min_pulse_width=0.5 / 1000,
        max_pulse_width=2.4 / 1000,
        frame_width=1 / 50,
        pin_factory=factory,
    )

    # reset
    print("reset")
    servo.angle = 0
    sleep(2)

    # launch
    print("launch")
    servo.angle = -90
    sleep(0.4)

    # reset
    print("reset")
    servo.angle = 0
    sleep(0.4)
    return


if __name__ == "__main__":
    main()
