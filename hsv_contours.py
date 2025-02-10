import cv2
import numpy as np

# 定数定義
CAMERA_INDEX = 0

def detect_objects() -> None:
    """画像から黄色い物体を検出し、結果画像を保存するスクリプト.
    
    Args:
      image_path: 処理対象の画像のパス.
    """
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("カメラを起動できません。")
        return

    ret, image = cap.read()
    cap.release()
    if not ret:
        print("画像のキャプチャに失敗しました。")
        return

    # 画像をHSV色空間に変換
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 緑の範囲を定義 (HSV)
    lower_green = np.array([15, 220, 120])
    upper_green = np.array([25, 255, 255])

    # 緑の部分のマスクを作成
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # マスクから輪郭を検出
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 輪郭を元画像に描画
    result = image.copy()
    cv2.drawContours(result, contours, -1, (0, 255, 0), 3)

    # 画像を保存
    cv2.imwrite("detected_objects.png", result)

if __name__ == "__main__":
    detect_objects()
