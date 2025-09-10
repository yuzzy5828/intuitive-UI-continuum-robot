import time
import numpy as np
import cv2
import serial
import csv

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
        self.phi = - phi * np.pi / 180.0
        self.theta = theta * np.pi / 180  # [rad]に変換
        if self.theta < 0.01:
            self.theta = 0.01

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
        """センサ用およびアクチュエータ用のシリアルポートを開く。"""
        # 入力側（センサArduino）用シリアル
        self.ser_in = serial.Serial(in_port, baudrate=baudrate, timeout=1)
        # 出力側（アクチュエータArduino）用シリアル
        self.ser_out = serial.Serial(out_port, baudrate=baudrate, timeout=1)

        self.ser_in.reset_input_buffer()

        # Arduinoリセット待ち
        time.sleep(5)

    def receive(self):
        """センサから文字列を1行受信して返す。"""
        #self.ser_in.reset_input_buffer()
        line = self.ser_in.readline().decode('utf-8').strip()
        return line

    def send(self, command):
        """アクチュエータArduinoへコマンドを送信。"""
        if isinstance(command, (list, np.ndarray)):
            command_str = ','.join([str(c) for c in command]) + '\n'
        else:
            command_str = str(command) + '\n'
        self.ser_out.write(command_str.encode('utf-8'))


def main():
    # シリアルブリッジ、モデル生成
    bridge = SerialBridge(in_port='COM3', out_port='COM5', baudrate=9600)
    model = Model()

    # カメラの準備
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to open video source")
        return

    # 画像表示用ウィンドウ設定
    cv2.namedWindow('camera view', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('camera view', 640, 480)

    # カメラ画像上で目標点の可視化に使うピクセル座標（例：画像中央）
    p_center = [320, 240]

    # CSVファイルを開く
    csv_path_70mm = "C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\20250306\\interface\\interface_70mm.csv"
    csv_path_95mm = "C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\20250606\\interface\\interface_100mm_3.csv"
    image_save_dir_70mm = "C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\20250306\\interface\\images_70mm\\"
    image_save_dir_95mm = "C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\20250606\\interface\\images_100mm_3\\"

    with open(csv_path_95mm, 'w', newline='') as f: #####
        writer = csv.writer(f)

        i = 0
        while True:
            # Arduino（センサ）から値を受信
            line = bridge.receive()
            if not line:
                # 受信できなければ少し待機して再受信
                time.sleep(0.04)
                continue

            # 受信データをパースして (phi_ref, theta_ref) に変換
            try:
                data = line.split(',')
                data0 = float(data[0])
                data1 = float(data[1])
                if (i == 0):
                    phi_ref = data0
                    theta_ref = data1
                elif (abs(data1) >= 50.0): #or (abs(phi_ref - data0) > 100.0):
                    pass                    
                else:
                    phi_ref = data0
                    theta_ref = data1
                
                if abs(theta_ref) < 1.0:
                    theta_ref == 1.0
                
                print(f"Received: theta_ref={theta_ref}, phi_ref={phi_ref}")

            except (IndexError, ValueError):
                print("Failed to parse:", line)
                continue

            # モデルからモータ回転角度(増分)を計算
            rotate_angle = model.cal_rotate_angle(theta_ref, phi_ref)

            # モータへ送信
            bridge.send(rotate_angle)

            # 少し待ってからカメラ画像を取得
            time.sleep(0.04)
            ret, img = cap.read()
            if not ret:
                print("Warning: Failed to read from camera.")
                continue

            # 画像上に目標点等を可視化 (必要に応じて)
            visualize_reference_trajectory(img, p_center)

            # 画像を表示
            cv2.imshow("camera view", img)

            # 画像を保存
            cv2.imwrite(f"{image_save_dir_95mm}interface_20250306_{i}.jpg", img)

            # CSVへ書き込み
            writer.writerow([i, theta_ref, phi_ref])

            i += 1

            # 'q'キーで終了するようにする場合（任意）
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
