import time
import numpy as np
import matplotlib.pyplot as plt
import cv2
import serial
import csv

from utils import visualize_reference_point
from utils import visualize_reference_trajectory

class Model:
    def __init__(self):
        self.L = 90.0  # 長さ mm
        self.d = 25.0  # tendonが通る部分の半径 mm
        self.r_pulley = 10.0  # pulleyの半径 mm
        self.n = 4     # セグメントの数

        self.delta_l = np.zeros(4)
        self.rotate_angle_absolute = np.zeros(4)  # 曲率や回転角から計算される絶対角度
        self.rotate_angle_previous = np.zeros(4)  # 前の角度
        self.rotate_angle = np.zeros(4)

    def cal_rotate_angle(self, theta, phi):
        """
        theta, phi [deg]を入力し、
        モデルからモータ回転角(増分)のリストを返す。
        """
        # 内部でphiのみ符号反転＆ラジアン変換
        self.phi = -phi * np.pi / 180.0
        self.theta = theta * np.pi / 180  # [rad]に変換

        for i in range(len(self.delta_l)):
            # 幾何学モデルからdelta_lを計算 mm
            self.delta_l[i] = (
                2 * self.n
                * (
                    (self.L / self.theta)
                    - self.d * np.cos(self.phi + (i - 1) * 2.0 * np.pi / len(self.delta_l))
                )
                * np.sin(self.theta / (2.0 * self.n))
                - self.L
            )

            # たるみを無視した絶対回転角度[deg]
            self.rotate_angle_absolute[i] = (self.delta_l[i] / (2.0 * np.pi * self.r_pulley)) * 360.0

            # 前回の回転角との差を計算(増分)
            self.rotate_angle[i] = self.rotate_angle_absolute[i] - self.rotate_angle_previous[i]

            # 次回のため、絶対角度を更新
            self.rotate_angle_previous[i] = self.rotate_angle_absolute[i]

        return self.rotate_angle


class SerialBridge:
    def __init__(self, in_port='/dev/ttyUSB0', out_port='/dev/ttyACM0', baudrate=9600):
        # 入力側（センサArduino）用シリアル (不要なら削除してもOK)
        # self.ser_in = serial.Serial(in_port, baudrate=baudrate, timeout=1)
        # 出力側（アクチュエータArduino）用シリアル
        self.ser_out = serial.Serial(out_port, baudrate=baudrate, timeout=1)

        time.sleep(5)  # Arduinoのリセット待ち(必要に応じて調整)

    def send(self, command):
        # コマンドは文字列で送信し、最後に改行を付ける
        if isinstance(command, (list, np.ndarray)):
            command_str = ','.join([str(c) for c in command]) + '\n'
        else:
            command_str = str(command) + '\n'
        self.ser_out.write(command_str.encode('utf-8'))


def main():
    # シリアルブリッジ作成
    bridge = SerialBridge(in_port='COM3', out_port='COM5', baudrate=9600)
    model = Model()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to open video source")
        return

    # ウィンドウを作成
    cv2.namedWindow('camera view', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('camera view', 640, 480)

    p_center = [320, 240]  # 画面中心などを可視化したい場合

    # CSVログ用
    csv_filename_70mm = "C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\20250306\\histeresis\\histeresis_70mm.csv"
    csv_filename_95mm = "C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\20250306\\histeresis\\histeresis_95mm.csv"
    out_img_dir_70mm = "C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\20250306\\histeresis\\images_70mm\\"
    out_img_dir_95mm = "C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\20250306\\histeresis\\images_95mm\\"
    i = 1
    j = 1

    # (theta_ref, phi_ref) をトグルするためのフラグ
    toggle_state = False  # False: (0,0), True: (90,0)

    visualize_circle = False

    # CSVファイルを開いておき、逐次書き込み
    with open(csv_filename_95mm, 'w', newline='') as f:  # 必要に応じて 'a' (append) に変更
        writer = csv.writer(f)

        while True:
            # カメラ映像を取得
            ret, img = cap.read()
            if not ret:
                print("Warning: Failed to read from camera.")
                continue

            time.sleep(0.25)

            # 目標点等の可視化（必要に応じて）
            if visualize_circle == True:
                visualize_reference_trajectory(img, p_center)

            cv2.imshow("camera view", img)

            # キー入力を取得 (1ms待ち)
            key = cv2.waitKey(10) & 0xFF

            # 'q' で終了
            if key == ord('q'):
                break

            # Enterキー (ASCIIコード13) で (theta_ref, phi_ref) 切り替え
            if key == 13:
                toggle_state = not toggle_state
                if toggle_state:
                    # (theta_ref, phi_ref) = (45, 0)
                    theta_ref = 90.0
                    phi_ref = -135.0
                else:
                    # (theta_ref, phi_ref) = (0, 0)
                    theta_ref = 0.000001
                    phi_ref = 0.0

                # モデルで回転角(増分)を計算
                rotate_angle = model.cal_rotate_angle(theta_ref, phi_ref)
                # モータに送信
                bridge.send(rotate_angle)

                # CSVログに書き込み
                writer.writerow([i, theta_ref, phi_ref])
                # 画像保存
                cv2.imwrite(f"{out_img_dir_95mm}histeresis_20250306_{i}.jpg", img)

                i += 1
            
            if key == ord('s'):
                # 画像保存
                cv2.imwrite(f"{out_img_dir_95mm}histeresis_20250306_start_{j}.jpg", img)
                j += 1
                
            if key == ord('c'):
                visualize_circle = not visualize_circle 

            #print(i)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
