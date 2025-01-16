import time
import numpy as np
import matplotlib.pyplot as plt
import cv2
import serial

from utils import visualize_reference_point
from utils import visualize_reference_trajectory

class Model:
    def __init__(self):
        self.L = 120.0  # 長さ mm
        self.d = 25.0  # tendonが通る部分の半径 mm
        self.r_pulley = 10.0 # pulleyの半径 mm
        self.n = 4      # セグメントの数
        self.delta_l = np.zeros(4)
        self.rotate_angle_absolute = np.zeros(4) # 曲率や回転角から計算される絶対角度
        self.rotate_angle_previous = np.zeros(4) # 前の角度
        self.rotate_angle = np.zeros(4)

    def cal_rotate_angle(self, rho, phi):
        self.phi = -phi  # 根本の回転角(符号に注意)
        self.rho = rho  # 曲率

        for i in range(len(self.delta_l)):
            # 幾何学モデルからdelta_lを計算 mm
            self.delta_l[i] = 2 * self.n * (self.rho - self.d * np.cos(self.phi + (i - 1) * 2 * np.pi / len(self.delta_l))) * np.sin(self.L / (2 * self.rho * self.n)) - self.L
            
            # たるみを無視した絶対回転角度を計算（deg）
            self.rotate_angle_absolute[i] = (self.delta_l[i] / (2 * np.pi * self.r_pulley)) * 360 

            # 前回の回転角との差を計算
            self.rotate_angle[i] = self.rotate_angle_absolute[i] - self.rotate_angle_previous[i]

            # 前回のabsolute角を更新
            self.rotate_angle_previous[i] = self.rotate_angle_absolute[i]

        # 回転角度を返す    
        return self.rotate_angle

class SerialBridge:
    def __init__(self, in_port='/dev/ttyUSB0', out_port='/dev/ttyACM0', baudrate=9600):
        # 入力側（センサArduino）用シリアル
        self.ser_in = serial.Serial(in_port, baudrate=baudrate, timeout=1)
        # 出力側（アクチュエータArduino）用シリアル
        self.ser_out = serial.Serial(out_port, baudrate=baudrate, timeout=1)
        time.sleep(5)  # Arduinoのリセット待ち(必要に応じて調整)

    def receive(self):
        # 改行まで読み込み
        self.ser_in.reset_input_buffer()
        line = self.ser_in.readline().decode('utf-8').strip()
        return line

    def send(self, command):
        # コマンドは文字列で送信し、最後に改行を付ける
        if isinstance(command, (list, np.ndarray)):
            # 配列ならCSV形式などにフォーマットして送信
            command_str = ','.join([str(c) for c in command]) + '\n'
        else:
            # 文字列ならそのまま送信
            command_str = str(command) + '\n'
        self.ser_out.write(command_str.encode('utf-8'))

def main():
    # シリアルブリッジ作成
    bridge = SerialBridge(in_port='/dev/ttyUSB0', out_port='/dev/ttyACM0', baudrate=9600)
    model = Model()

    cap = cv2.VideoCapture(0)

    p_center = 0 # 中心のピクセルの値（）2次元

    i = 0

    while True:
        
        # Arduino（センサ）から値を受信
        line = bridge.receive()
        if not line:
            # 受信できなければ待機
            time.sleep(0.1)
            continue
        
        try:
            data = line.split(',')
            phi_ref = float(data[0])
            rho_ref = float(data[1])
            print(rho_ref, phi_ref)
        except (IndexError, ValueError):
            # パース失敗したらスキップ
            print("受信データのパース失敗:", line)
            continue
        
        # モデルにより近似値計算
        rotate_angle = model.cal_rotate_angle(rho_ref, i * np.pi / 10)

        # コマンドをアクチュエータArduinoへ送信
        bridge.send(rotate_angle)

        time.sleep(0.2)
        
        # モデルによる目標の点を表示
        _, img = cap.read()
        visualize_reference_point(img, p_center, rho_ref, phi_ref)
        cv2.imshow(0, img)
        
        cap.release()
        cv2.destroyAllWindows()

        i += 1

if __name__ == '__main__':
    main()
