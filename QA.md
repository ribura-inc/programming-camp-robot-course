# プログラミングキャンプ QAリスト

## Q. カメラ画像が読み込まれない

`cap.release()` していないことが原因の可能性が高いです。適切にカメラ権限を開放してプログラムを終了してください。
カメラのUSBを抜き差しすると暫定的にリセットできます。

## Q. 過去の接続情報が原因でSSHが出来ない

`ssh-keygen -R raspi-X.local` で過去の接続情報を削除してください。

## Q. 違うラズパイにSSHされてしまう

ネーム解決のキャッシュが原因ではないでしょうか？ 対応方法見つけてないです、、

## Q. ssh接続できない

```bash
PS C:\Users\ryout\OneDrive\デスクトップ\programing_camp> scp robot_work_sak.py  pi@raspi-2.local:/home/pi/
ssh: Could not resolve hostname raspi-2.local: \202\273\202\314\202\346\202\244\202\310\203z\203X\203g\202\315\225s\226\276\202\305\202\267\201B
C:\WINDOWS\System32\OpenSSH\scp.exe: Connection closed
```

- 同じWiFiに接続していますか？
- 先に `ping` してみるとうまくいくケースが？？（理由わかってない）
- `ipconfig /flushdns` でDNSキャッシュをクリアしてみる？

---

※ 過去質問（対策済み）

## Q. カメラ画像がプログラムの実行途中で急に読めなくなる

サーボの電源をラズパイから取っていることが原因です。適切に外部電源からサーボを駆動してください。
