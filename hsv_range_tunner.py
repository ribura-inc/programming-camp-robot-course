import cv2
import numpy as np


def nothing(x: int) -> None:
    """何もしないコールバック."""
    pass


def main() -> None:
    """リアルタイムでHSVの範囲を調整するUIを表示する."""
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

        lower_h = cv2.getTrackbarPos("Lower H", "Trackbars")
        lower_s = cv2.getTrackbarPos("Lower S", "Trackbars")
        lower_v = cv2.getTrackbarPos("Lower V", "Trackbars")
        upper_h = cv2.getTrackbarPos("Upper H", "Trackbars")
        upper_s = cv2.getTrackbarPos("Upper S", "Trackbars")
        upper_v = cv2.getTrackbarPos("Upper V", "Trackbars")

        lower_bound = np.array([lower_h, lower_s, lower_v])
        upper_bound = np.array([upper_h, upper_s, upper_v])

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        result = cv2.bitwise_and(frame, frame, mask=mask)

        # 最大輪郭と重心の描画（resultに）
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            cv2.drawContours(result, [largest_contour], -1, (0, 255, 0), 2)
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.circle(result, (cx, cy), 5, (0, 0, 255), -1)

        combined = np.hstack((frame, result))
        cv2.imshow("Original & Result", combined)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
