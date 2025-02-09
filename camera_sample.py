import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("カメラが見つかりません。")
    exit()

ret, frame = cap.read()
if ret:
    cv2.imwrite("capture.jpg", frame)  # 画像を保存
    print("画像を保存しました: capture.jpg")

cap.release()
