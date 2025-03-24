from time import sleep

from gpiozero import OutputDevice

motor_A_1 = OutputDevice(4)  # motor_A_1ピン
motor_A_2 = OutputDevice(17)  # motor_A_2ピン


print("モーター正転")
motor_A_1.on()
motor_A_2.off()
sleep(2)

print("モーター逆転")
motor_A_1.off()
motor_A_2.on()
sleep(2)

print("モーター停止")
motor_A_1.off()
motor_A_2.off()
sleep(2)


# 本プログラムは動作理解のサンプルであり、実際には動かせない
