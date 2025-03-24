from time import sleep

from gpiozero import Motor

# モータードライバのピン設定
motor_left = Motor(forward=15, backward=14)
motor_right = Motor(forward=23, backward=18)


print("前進")
motor_left.forward()
motor_right.forward()

sleep(3)


print("後進")
motor_left.backward()
motor_right.backward()

sleep(3)

print("斜め左")
motor_left.forward(speed=0.5)
motor_right.forward()

sleep(3)
