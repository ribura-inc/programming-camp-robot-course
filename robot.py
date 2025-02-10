import cv2
import numpy as np
import time
import random
from gpiozero import PWMOutputDevice, DigitalOutputDevice, AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory

# 定数定義
CAMERA_INDEX = 0

# サーボ設定
SERVO_PIN = 12
SERVO_MIN_ANGLE = 85
SERVO_MAX_ANGLE = 0
SERVO_MIN_PULSE = 0.5 / 1000
SERVO_MAX_PULSE = 2.4 / 1000
SERVO_FRAME_WIDTH = 1 / 50

# モーターピン設定
AIN1_PIN = 14
AIN2_PIN = 15
PWMA_PIN = 18
BIN1_PIN = 8
BIN2_PIN = 25
PWMB_PIN = 7

# 動作パラメータ
MOVE_SPEED = 0.8            # 前進時の基本速度
ROTATE_SPEED = 0.7          # 旋回時の速度
CORRECTION_FACTOR = 0.1     # 画面中心からのずれ補正係数

# 物体検出パラメータ
COLOR_THRESHOLD = 0.0005              # 色検出の最小面積比率
CLOSE_DISTANCE_THRESHOLD = 0.0020      # タイヤ出力を変える
LAUNCH_DETECTION_DURATION = 1.5     # 発射前に連続検出する必要がある秒数
CAN_LAUNCH_DISTANCE_THRESHOLD = 0.03 # 発射可能と判断する面積比率

# 探索行動パラメータ
SEARCH_ROTATE_DURATION = 1.0  # 旋回モードの継続時間
SEARCH_FORWARD_DURATION = 1.0 # 前進モードの継続時間
SLEEP_INTERVAL = 0.01         # ループ間の待機時間

# 色検出用HSVレンジ
LOWER_HSV = np.array([15, 220, 120])   # オレンジ色の下限
UPPER_HSV = np.array([25, 255, 255])  # オレンジ色の上限

class ColorObjectTracker:
    """カメラ画像から色物体を追尾し、接近時に射出するクラス.

    物体検出により追尾動作と探索動作（旋回＋前進）を非ブロッキングで実施し、
    一定期間連続検出された場合に射出動作を行う.
    """

    def __init__(self) -> None:
        """各種ハードウェアの初期化と状態変数の設定を行う."""
        # カメラ初期化
        self.cap = cv2.VideoCapture(CAMERA_INDEX)

        # モータードライバのピン設定
        self.AIN1 = DigitalOutputDevice(AIN1_PIN)
        self.AIN2 = DigitalOutputDevice(AIN2_PIN)
        self.PWMA = PWMOutputDevice(PWMA_PIN)
        self.BIN1 = DigitalOutputDevice(BIN1_PIN)
        self.BIN2 = DigitalOutputDevice(BIN2_PIN)
        self.PWMB = PWMOutputDevice(PWMB_PIN)

        # サーボモーターの設定（射出用）
        factory = PiGPIOFactory()
        self.servo = AngularServo(
            SERVO_PIN,
            min_angle=SERVO_MIN_ANGLE,
            max_angle=SERVO_MAX_ANGLE,
            initial_angle=SERVO_MAX_ANGLE,
            min_pulse_width=SERVO_MIN_PULSE,
            max_pulse_width=SERVO_MAX_PULSE,
            frame_width=SERVO_FRAME_WIDTH,
            pin_factory=factory,
        )
        self.servo.angle = SERVO_MAX_ANGLE

        # 基本速度設定
        self.base_speed = MOVE_SPEED
        self.rotate_speed = ROTATE_SPEED

        # 状態管理用変数
        self.state: str = ""  # "tracking", "search_rotate", "search_forward"
        self.state_start_time: float = time.time()
        self.rotation_direction: int = random.choice([1, -1])

    def launch(self) -> None:
        """射出動作を実施する."""
        print("launch")
        self.servo.angle = SERVO_MIN_ANGLE
        time.sleep(0.2)
        print("reset")
        self.servo.angle = SERVO_MAX_ANGLE
        time.sleep(0.1)

    def set_motor_speed(self, left_speed: float, right_speed: float) -> None:
        """左右モーターの速度を設定する.
        
        Args:
            left_speed: 左モーターの速度（0～1）
            right_speed: 右モーターの速度（0～1）
        """
        self.AIN1.off()
        self.AIN2.on()
        self.BIN1.off()
        self.BIN2.on()
        left_speed = max(0, min(1, left_speed))
        right_speed = max(0, min(1, right_speed))
        self.PWMA.value = left_speed
        self.PWMB.value = right_speed

    def stop(self) -> None:
        """モーターを停止する."""
        self.AIN1.on()
        self.AIN2.on()
        self.BIN1.on()
        self.BIN2.on()
        self.PWMA.value = 0
        self.PWMB.value = 0

    def detect_object(self) -> tuple[bool, tuple[int, int] | None, float, np.ndarray]:
        """カメラ画像から物体を検出する.
        
        HSV変換後、指定色のマスク作成と輪郭抽出により最大領域の面積比率と重心を算出する.
        
        Returns:
            detected: 物体が検出されたか否か.
            centroid: 物体の重心 (x, y) または None.
            area_ratio: 物体領域の画面全体に対する面積比率.
            frame: キャプチャしたフレーム.
        """
        ret, frame = self.cap.read()
        if not ret:
            print("フレームの取得に失敗しました。")
            return False, None, 0.0, np.array([])

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, LOWER_HSV, UPPER_HSV)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            print("物体が検出されませんでした。")
            return False, None, 0.0, frame

        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        frame_area = frame.shape[0] * frame.shape[1]
        area_ratio = area / frame_area

        if area_ratio < COLOR_THRESHOLD:
            print(f"検出された物体の面積比率が閾値を下回りました: {area_ratio:.4f}")
            return False, None, area_ratio, frame

        M = cv2.moments(largest_contour)
        if M["m00"] == 0:
            print("重心の計算に失敗しました。")
            return False, None, area_ratio, frame
        centroid_x = int(M["m10"] / M["m00"])
        centroid_y = int(M["m01"] / M["m00"])
        print(f"物体が検出されました。重心: ({centroid_x}, {centroid_y}), 面積比率: {area_ratio:.2f}")
        return True, (centroid_x, centroid_y), area_ratio, frame


    def run(self) -> None:
        """メインループを実行する."""
        try:
            while True:
                current_time = time.time()
                detected, centroid, area_ratio, frame = self.detect_object()

                if detected and centroid is not None:
                    # 物体検出中 → トラッキング状態に移行
                    if self.state != "tracking":
                        self.state = "tracking"
                        self.state_start_time = current_time

                    # 左右のタイヤ出力に係数をかけるか
                    if area_ratio > CLOSE_DISTANCE_THRESHOLD:
                        #  画面中心からのずれを計算し、左右の出力を補正
                        frame_center_x = frame.shape[1] / 2
                        error = (centroid[0] - frame_center_x) / frame_center_x  # -1～1の範囲
                        left_speed = self.base_speed * (1 + CORRECTION_FACTOR * error)
                        right_speed = self.base_speed * (1 - CORRECTION_FACTOR * error)
                    else:
                        left_speed = self.base_speed
                        right_speed = self.base_speed 
                    self.set_motor_speed(left_speed, right_speed)

                    # 連続検出時間が規定を超えたら射出
                    if area_ratio > CAN_LAUNCH_DISTANCE_THRESHOLD and (current_time - self.state_start_time >= LAUNCH_DETECTION_DURATION):
                        print("物体に接近。発射します。")
                        self.stop()
                        self.launch()
                        break
                else:
                    # 物体未検出 → 探索行動（旋回＋前進）へ
                    if self.state not in ["search_rotate", "search_forward"]:
                        self.state = "search_rotate"
                        self.state_start_time = current_time
                        self.rotation_direction = random.choice([1, -1])
                    if self.state == "search_rotate":
                        # 非ブロッキングで旋回しながら検出を継続
                        if self.rotation_direction == 1:
                            # 左旋回
                            self.AIN1.on()
                            self.AIN2.off()
                            self.BIN1.off()
                            self.BIN2.on()
                        else:
                            # 右旋回
                            self.AIN1.off()
                            self.AIN2.on()
                            self.BIN1.on()
                            self.BIN2.off()
                        self.PWMA.value = self.rotate_speed
                        self.PWMB.value = self.rotate_speed
                        if current_time - self.state_start_time >= SEARCH_ROTATE_DURATION:
                            self.state = "search_forward"
                            self.state_start_time = current_time
                    elif self.state == "search_forward":
                        # 前進しながら探索
                        self.set_motor_speed(self.base_speed, self.base_speed)
                        if current_time - self.state_start_time >= SEARCH_FORWARD_DURATION:
                            self.state = "search_rotate"
                            self.state_start_time = current_time
                            self.rotation_direction = random.choice([1, -1])
                time.sleep(SLEEP_INTERVAL)
        except KeyboardInterrupt:
            print("プログラムを終了します")
        finally:
            self.stop()
            self.cap.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    tracker = ColorObjectTracker()
    tracker.run()
