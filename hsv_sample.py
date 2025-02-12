import cv2
import matplotlib.pyplot as plt


def capture_and_visualize() -> None:
    """カメラから1枚画像を取得し、HSV各チャネルの分布をヒストグラムで可視化し、画像として保存する.

    カメラから画像をキャプチャし、BGR画像をHSVに変換後、
    Hue, Saturation, Valueの各チャネルのヒストグラムを保存する.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("カメラを起動できません。")
        return

    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("画像のキャプチャに失敗しました。")
        return

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h_channel = hsv[:, :, 0]
    s_channel = hsv[:, :, 1]
    v_channel = hsv[:, :, 2]

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes = axes.flatten()

    axes[0].imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    axes[0].set_title("Captured Image")
    axes[0].axis("off")

    axes[1].hist(h_channel.ravel(), bins=180, range=(0, 180), color="red")
    axes[1].set_title("Hue Histogram")
    axes[1].set_xlabel("Hue")
    axes[1].set_ylabel("Frequency")

    axes[2].hist(s_channel.ravel(), bins=256, range=(0, 256), color="green")
    axes[2].set_title("Saturation Histogram")
    axes[2].set_xlabel("Saturation")
    axes[2].set_ylabel("Frequency")

    axes[3].hist(v_channel.ravel(), bins=256, range=(0, 256), color="blue")
    axes[3].set_title("Value Histogram")
    axes[3].set_xlabel("Value")
    axes[3].set_ylabel("Frequency")

    plt.tight_layout()
    plt.savefig("hsv_histograms.png")
    plt.close()


if __name__ == "__main__":
    capture_and_visualize()
