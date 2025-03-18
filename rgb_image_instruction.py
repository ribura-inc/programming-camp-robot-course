"""画像はRGBの3チャンネルの重ね合わせで実現されていることを理解するためのスクリプト（実際のカメラ画像を3チャンネルに分解することで理解を手助け）"""

import cv2
import matplotlib.pyplot as plt
import numpy as np


def capture_and_display() -> None:
    """カメラ画像を取得し、RGB各チャンネルと合成画像を表示する.

    480P（640×480）の画像を取得し、
    ・上段：左から順に赤、緑、青チャンネルを各カラーマップ（Reds, Greens, Blues）で表示。各画像には0～255の値がカラーバーで示される。
    ・下段：3チャンネルを重ね合わせた元の画像を表示。
    """
    # カメラ設定：480P（640×480）
    cap: cv2.VideoCapture = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    ret, frame = cap.read()
    if not ret:
        print("カメラから画像を取得できませんでした")
        cap.release()
        return

    # OpenCVはBGRのため、RGBに変換
    frame_rgb: np.ndarray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 各チャンネル抽出
    r_channel: np.ndarray = frame_rgb[:, :, 0]
    g_channel: np.ndarray = frame_rgb[:, :, 1]
    b_channel: np.ndarray = frame_rgb[:, :, 2]

    # グリッドレイアウト設定（上段：各チャンネル、下段：合成画像）
    fig = plt.figure(figsize=(12, 8))
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1])

    # 赤チャンネル
    ax_r = fig.add_subplot(gs[0, 0])
    im_r = ax_r.imshow(r_channel, cmap="Reds", vmin=0, vmax=255)
    ax_r.set_title("Red Channel")
    ax_r.axis("off")
    plt.colorbar(im_r, ax=ax_r)

    # 緑チャンネル
    ax_g = fig.add_subplot(gs[0, 1])
    im_g = ax_g.imshow(g_channel, cmap="Greens", vmin=0, vmax=255)
    ax_g.set_title("Green Channel")
    ax_g.axis("off")
    plt.colorbar(im_g, ax=ax_g)

    # 青チャンネル
    ax_b = fig.add_subplot(gs[0, 2])
    im_b = ax_b.imshow(b_channel, cmap="Blues", vmin=0, vmax=255)
    ax_b.set_title("Blue Channel")
    ax_b.axis("off")
    plt.colorbar(im_b, ax=ax_b)

    # 合成画像（重ね合わせた結果）
    ax_merged = fig.add_subplot(gs[1, :])
    ax_merged.imshow(frame_rgb)
    ax_merged.set_title("Merged Image (Original)")
    ax_merged.axis("off")

    plt.tight_layout()
    plt.show()

    cap.release()


if __name__ == "__main__":
    capture_and_display()
