import time
import numpy as np
import serial

class Model:
    def __init__(self, L=90.0, d=25.0, r_pulley=10.0, n=4):
        '''
        L       : 1セグメントの長さ [mm]。
        d       : 腱が通る円の半径 [mm]。
        r_pulley: モータプーリーの半径 [mm]。
        n       : セグメントの数
        '''
        self.L = L
        self.d = d
        self.r_pulley = r_pulley
        self.n = n

        self.delta_l = np.zeros(4)
        self.rotate_angle_absolute = np.zeros(4)
        self.rotate_angle_previous = np.zeros(4)
        self.rotate_angle = np.zeros(4)

    def cal_rotate_angle(self, theta, phi):
        
        # 度からラジアンへ変換し、phiの符号を反転
        phi_rad = -phi * np.pi / 180.0
        theta_rad = theta * np.pi / 180.0

        if theta_rad < 0.01:
            # 分母がゼロになるのを防ぐ
            theta_rad = 0.01

        for i in range(len(self.delta_l)):
            # 幾何学モデルからテンドン長の差分 (delta_l) を計算 [mm]
            self.delta_l[i] = (
                2 * self.n
                * (
                    (self.L / theta_rad)
                    - self.d * np.cos(phi_rad + (i - 1) * 2.0 * np.pi / len(self.delta_l))
                )
                * np.sin(theta_rad / (2.0 * self.n))
                - self.L
            )

            # テンドン長の差分を絶対モータ回転角度に変換 [度]
            self.rotate_angle_absolute[i] = (self.delta_l[i] / (2.0 * np.pi * self.r_pulley)) * 360.0

            # 前回の回転角との差分を計算（増分）
            self.rotate_angle[i] = self.rotate_angle_absolute[i] - self.rotate_angle_previous[i]

            # 次回計算のために絶対角度を更新
            self.rotate_angle_previous[i] = self.rotate_angle_absolute[i]

        return self.rotate_angle


class SerialBridge:
    def __init__(self, in_port='/dev/ttyUSB0', out_port='/dev/ttyACM0', baudrate=9600):
        self.ser_in = None
        self.ser_out = None
        
        try:
            self.ser_in = serial.Serial(in_port, baudrate=baudrate, timeout=1)
            print(f"Serial port for sensor opened at {in_port}")
        except serial.SerialException as e:
            print(f"Error opening sensor port {in_port}: {e}")

        try:
            self.ser_out = serial.Serial(out_port, baudrate=baudrate, timeout=1)
            print(f"Serial port for actuator opened at {out_port}")
        except serial.SerialException as e:
            print(f"Error opening actuator port {out_port}: {e}")

        if self.ser_in:
            self.ser_in.reset_input_buffer()
        if self.ser_out:
            self.ser_out.reset_input_buffer()

        time.sleep(5)  # Arduinoのリセット待ち

    def receive(self):
        # strでの指令値受信用
        if self.ser_in and self.ser_in.is_open:
            try:
                line = self.ser_in.readline().decode('utf-8').strip()
                return line
            except serial.SerialException as e:
                print(f"Error receiving data: {e}")
                return ""
        return ""

    def send(self, command):
        # strでの回転量送信用
        if self.ser_out and self.ser_out.is_open:
            try:
                if isinstance(command, (list, np.ndarray)):
                    command_str = ','.join([str(c) for c in command]) + '\n'
                else:
                    command_str = str(command) + '\n'
                self.ser_out.write(command_str.encode('utf-8'))
            except serial.SerialException as e:
                print(f"Error sending data: {e}")

    def close(self):
        if self.ser_in and self.ser_in.is_open:
            self.ser_in.close()
            print("Sensor serial port closed.")
        if self.ser_out and self.ser_out.is_open:
            self.ser_out.close()
            print("Actuator serial port closed.")