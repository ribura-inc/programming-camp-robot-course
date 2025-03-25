from time import sleep

from gpiozero import OutputDevice

left_forward = OutputDevice(15)  # left_forwardピン
left_backward = OutputDevice(14)  # left_backwardピン


print("モーター正転")
left_forward.on()
left_backward.off()
sleep(2)

print("モーター逆転")
left_forward.off()
left_backward.on()
sleep(2)

print("モーター停止")
left_forward.off()
left_backward.off()
sleep(2)


# 本プログラムは動作理解のサンプルであり、実際には動かせない
