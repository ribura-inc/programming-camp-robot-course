from time import sleep

from gpiozero import PWMOutputDevice

# 左モーターのピン（forward: GPIO15, backward: GPIO14）
left_forward = PWMOutputDevice(15)
left_backward = PWMOutputDevice(14)

# 右モーターのピン（forward: GPIO23, backward: GPIO18）
right_forward = PWMOutputDevice(23)
right_backward = PWMOutputDevice(18)


def stop_all():
    left_forward.value = 0
    left_backward.value = 0
    right_forward.value = 0
    right_backward.value = 0


print("前進（100%）")
left_forward.value = 1.0
left_backward.value = 0
right_forward.value = 1.0
right_backward.value = 0
sleep(3)
stop_all()

print("後進（100%）")
left_forward.value = 0
left_backward.value = 1.0
right_forward.value = 0
right_backward.value = 1.0
sleep(3)
stop_all()

print("斜め左（左モーター50%, 右モーター100%）")
left_forward.value = 0.5
left_backward.value = 0
right_forward.value = 1.0
right_backward.value = 0
sleep(3)
stop_all()


print("右回転")
left_forward.value = 1.0
left_backward.value = 0
right_forward.value = 0
right_backward.value = 1.0
sleep(3)
stop_all()
