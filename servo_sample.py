from gpiozero import AngularServo
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory

# SG90のピン設定
SERVO_PIN = 12  # SG90-1

MIN_DEGREE = -90       # 000 : -90degree
MAX_DEGREE = 90       # 180 : +90degree

def main():
    factory = PiGPIOFactory()
    # min_pulse_width, max_pulse_width, frame_width =>SG90仕様
    servo = AngularServo(SERVO_PIN, min_angle=MIN_DEGREE, max_angle=MAX_DEGREE, 
                         min_pulse_width=0.5/1000, max_pulse_width=2.4/1000, frame_width=1/50, pin_factory=factory)

    # SG90を -60度 <-> +60度で角度を変える
    try:
        for _ in range(5):
            servo.angle = 60
            sleep(1.0)
            servo.angle = -60
            sleep(1.0)
    except KeyboardInterrupt:
        print("stop")

    return

if __name__ == "__main__":
    main()