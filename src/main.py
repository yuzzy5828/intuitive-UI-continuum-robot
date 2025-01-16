import time
import numpy as np
import matplotlib.pyplot as plt
import serial

import torch as t
import torch.nn as nn
import torch.optim as optim

class Model:
    def __init__(self, rho, phi):
        self.L = 60  # 長さ
        self.d = 35  # tendonが通る部分の半径
        self.phi = phi  # 根本の回転角
        self.rho = rho  # 曲率
        self.n = 5      # ディスクの数
        self.delta_l = np.zeros(4)

    def cal_delta_l(self):
        for i in range(len(self.delta_l)):
            # 下記の式はオリジナルコードを踏襲していますが、実際の計算式は要検証
            self.delta_l[i] = (self.L + self.d * np.cos(self.phi + 2 * np.pi * (i - 1) / self.n)) \
                               * self.n * np.cos((self.L / self.rho) / self.n)
        return self.delta_l

# 学習したモデルを基に制御を行う
class ErrorEstimation(nn.Module):
    def __init__(self, rho_ref, h, phi_ref, phi, hyperparameters):
        super(ErrorEstimation, self).__init__()
        self.L = 60
        self.rho_ref = rho_ref
        self.h = h
        self.rho_now = 0
        self.phi_ref = phi_ref
        self.phi_now = phi
    
    def cal_current_rho(self):
        self.rho_now = self.L / (2 * np.arcsin(self.h / self.L))

    def predict(self, data):
        model = t.load('model.pth', map_location=cpu)
        pred = model(data) # dataはrhoとphiの２つ
        return pred # predは4つのdelta_lと同じ配列         
                                                                          
class SerialBridge:
    def __init__(self, in_port='/dev/ttyACM0', out_port='/dev/ttyACM1', baudrate=9600):
        # 入力側（センサArduino）用シリアル
        self.ser_in = serial.Serial(in_port, baudrate=baudrate, timeout=1)
        # 出力側（アクチュエータArduino）用シリアル
        # self.ser_out = serial.Serial(out_port, baudrate=baudrate, timeout=1)
        time.sleep(2)  # Arduinoのリセット待ち(必要に応じて調整)

    def receive(self):
        # 改行まで読み込み
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
    bridge = SerialBridge(in_port='/dev/ttyACM0', out_port='/dev/ttyACM1', baudrate=9600)

    while True:
        # Arduino（センサ）から値を受信
        line = bridge.receive()
        if not line:
            # 受信できなければ待機
            time.sleep(0.1)
            continue
        
        try:
            data = line.split(',')
            rho_ref = float(data[0])
            phi_ref = float(data[1])
            print(rho_ref, phi_ref)
        except (IndexError, ValueError):
            # パース失敗したらスキップ
            print("受信データのパース失敗:", line)
            continue
        
        # モデルにより近似値計算
        model = Model(rho=rho_ref, phi=phi_ref)
        delta_l = model.cal_delta_l()

        data = t.Tensor([h, phi])

        # エラー推定
        error_nn = ErrorEstimation(rho_ref=rho_ref, h=h, phi_ref=phi_ref, phi=phi)
        error_nn.cal_current_rho()
        error = error_nn.predict(data=data)

        # 修正後のコマンド
        command = delta_l + error

        # コマンドをアクチュエータArduinoへ送信
        bridge.send(command)

        time.sleep(0.1)

if __name__ == '__main__':
    main()
