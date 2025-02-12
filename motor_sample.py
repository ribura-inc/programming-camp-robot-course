from time import sleep

from gpiozero import DigitalOutputDevice, PWMOutputDevice

# モータードライバのピン設定
AIN1 = DigitalOutputDevice(14)
AIN2 = DigitalOutputDevice(15)
PWMA = PWMOutputDevice(18)

BIN1 = DigitalOutputDevice(8)
BIN2 = DigitalOutputDevice(25)
PWMB = PWMOutputDevice(7)

# デューティ比（速度設定 0~1.0）
val = 0.6


# 前進する関数
def func_forward():
    print("前進します")
    AIN1.off()
    AIN2.on()
    BIN1.off()
    BIN2.on()
    PWMA.value = val
    PWMB.value = val


# 後進する関数
def func_back():
    print("後進します")
    AIN1.on()
    AIN2.off()
    BIN1.on()
    BIN2.off()
    PWMA.value = val
    PWMB.value = val


# 右回転する関数
def func_right():
    print("右に回転します")
    AIN1.off()
    AIN2.on()
    BIN1.on()
    BIN2.off()
    PWMA.value = val
    PWMB.value = val


# 左回転する関数
def func_left():
    print("左に回転します")
    AIN1.on()
    AIN2.off()
    BIN1.off()
    BIN2.on()
    PWMA.value = val
    PWMB.value = val


# ブレーキする関数
def func_brake():
    print("ブレーキをかけます")
    AIN1.on()
    AIN2.on()
    BIN1.on()
    BIN2.on()
    PWMA.value = 0
    PWMB.value = 0


# メインプログラム
try:
    func_forward()
    sleep(3.0)
    func_brake()
    sleep(3.0)

    func_right()
    sleep(1.5)
    func_brake()
    sleep(3.0)

    func_left()
    sleep(2.8)
    func_brake()
    sleep(3.0)

    func_right()
    sleep(1.5)
    func_brake()
    sleep(3.0)

    func_back()
    sleep(3.0)
    func_brake()
    sleep(3.0)

except KeyboardInterrupt:
    pass

finally:
    func_brake()
    print("End of program")
