import cv2
import numpy as np


def nothing(x: int) -> None:
    """何もしないコールバック."""
    pass


def main() -> None:
    """リアルタイムでHSVの範囲を調整するUIを表示する."""
    # DirectShowを指定してカメラを初期化（Windows環境の場合）
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("カメラが開けません")
        return

    cv2.namedWindow("Trackbars", cv2.WINDOW_NORMAL)
    cv2.moveWindow("Trackbars", 10, 10)
    cv2.namedWindow("Original & Result", cv2.WINDOW_NORMAL)
    cv2.moveWindow("Original & Result", 300, 10)

    # LOWER用トラックバー作成
    cv2.createTrackbar("Lower H", "Trackbars", 65, 179, nothing)
    cv2.createTrackbar("Lower S", "Trackbars", 110, 255, nothing)
    cv2.createTrackbar("Lower V", "Trackbars", 105, 255, nothing)

    # UPPER用トラックバー作成
    cv2.createTrackbar("Upper H", "Trackbars", 105, 179, nothing)
    cv2.createTrackbar("Upper S", "Trackbars", 200, 255, nothing)
    cv2.createTrackbar("Upper V", "Trackbars", 230, 255, nothing)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("フレームの取得に失敗")
            break

        # トラックバーから現在のHSV閾値を取得
        lower_h = cv2.getTrackbarPos("Lower H", "Trackbars")
        lower_s = cv2.getTrackbarPos("Lower S", "Trackbars")
        lower_v = cv2.getTrackbarPos("Lower V", "Trackbars")
        upper_h = cv2.getTrackbarPos("Upper H", "Trackbars")
        upper_s = cv2.getTrackbarPos("Upper S", "Trackbars")
        upper_v = cv2.getTrackbarPos("Upper V", "Trackbars")

        lower_bound = np.array([lower_h, lower_s, lower_v])
        upper_bound = np.array([upper_h, upper_s, upper_v])

        # 画像をHSV空間に変換してマスク作成
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        result = cv2.bitwise_and(frame, frame, mask=mask)

        # original と result を横に結合
        combined = np.hstack((frame, result))

        # 結果を表示
        cv2.imshow("Original & Result", combined)

        # ESCキーで終了
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
