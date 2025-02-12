from time import sleep

from gpiozero import DigitalOutputDevice, PWMOutputDevice

# モータードライバのピン設定
motor_A_1 = DigitalOutputDevice(14)
motor_A_2 = DigitalOutputDevice(15)
motor_A_pwm = PWMOutputDevice(18)

motor_B_1 = DigitalOutputDevice(8)
motor_B_2 = DigitalOutputDevice(25)
motor_B_pwm = PWMOutputDevice(7)


print("前進します")
motor_A_1.on()
motor_A_2.off()
motor_B_1.on()
motor_B_2.off()
motor_A_pwm.value = 1.0
motor_B_pwm.value = 1.0

sleep(2)


print("後進します")
motor_A_1.off()
motor_A_2.on()
motor_B_1.off()
motor_B_2.on()
motor_A_pwm.value = 0.6
motor_B_pwm.value = 0.6

sleep(2)


print("どう動く？？")
motor_A_1.on()
motor_A_2.off()
motor_B_1.on()
motor_B_2.off()
motor_A_pwm.value = 0.5
motor_B_pwm.value = 1.0

sleep(2)
