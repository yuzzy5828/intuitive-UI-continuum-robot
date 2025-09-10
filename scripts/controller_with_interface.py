import time
import numpy as np
import cv2
import csv

from model import Model, SerialBridge
from utils import visualize_reference_trajectory

def main():
    # シリアルブリッジ、モデル生成
    bridge = SerialBridge(in_port='COM3', out_port='COM5', baudrate=9600)
    model = Model()

    # カメラの準備
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to open video source")
        bridge.close()
        return

    cv2.namedWindow('camera view', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('camera view', 640, 480)

    p_center = [320, 240]

    csv_path = "C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\20250606\\interface\\interface_100mm_3.csv"
    image_save_dir = "C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\20250606\\interface\\images_100mm_3\\"

    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        i = 0
        while True:
            line = bridge.receive()
            if not line:
                time.sleep(0.04)
                continue

            try:
                data = line.split(',')
                data0 = float(data[0])
                data1 = float(data[1])
                
                if (i == 0):
                    phi_ref = data0
                    theta_ref = data1
                elif (abs(data1) >= 50.0):
                    pass
                else:
                    phi_ref = data0
                    theta_ref = data1
                
                if abs(theta_ref) < 1.0:
                    theta_ref = 1.0
                
                print(f"Received: theta_ref={theta_ref}, phi_ref={phi_ref}")

            except (IndexError, ValueError):
                print("Failed to parse:", line)
                continue

            rotate_angle = model.cal_rotate_angle(theta_ref, phi_ref)
            bridge.send(rotate_angle)

            time.sleep(0.04)
            ret, img = cap.read()
            if not ret:
                print("Warning: Failed to read from camera.")
                continue

            visualize_reference_trajectory(img, p_center)
            cv2.imshow("camera view", img)
            cv2.imwrite(f"{image_save_dir}interface_20250306_{i}.jpg", img)
            writer.writerow([i, theta_ref, phi_ref])

            i += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    bridge.close()

if __name__ == '__main__':
    main()