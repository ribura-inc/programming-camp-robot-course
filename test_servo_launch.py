from gpiozero import AngularServo
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory

# SG90のピン設定
SERVO_PIN = 12  # SG90-1

MIN_DEGREE = 85      # 000 : -90degree
MAX_DEGREE = 0       # 180 : +90degree

def main():
    factory = PiGPIOFactory()
    # min_pulse_width, max_pulse_width, frame_width =>SG90仕様
    servo = AngularServo(SERVO_PIN, min_angle=MIN_DEGREE, max_angle=MAX_DEGREE, initial_angle=MAX_DEGREE,
                         min_pulse_width=0.5/1000, max_pulse_width=2.4/1000, frame_width=1/50, pin_factory=factory)

    # reset
    print("reset")
    servo.angle = MAX_DEGREE
    sleep(2)

    # launch
    print("launch")
    servo.angle = MIN_DEGREE
    sleep(0.2)
    
    # reset
    print("reset")
    servo.angle = MAX_DEGREE
    sleep(0.4)
    return

if __name__ == "__main__":
    main()