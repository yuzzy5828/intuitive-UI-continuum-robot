import time
import numpy as np
import cv2
import csv

from model import Model, SerialBridge
from utils import visualize_reference_trajectory

def main():
    # シリアル通信用と計算用のインスタンス
    bridge = SerialBridge(in_port='COM5', out_port='COM3', baudrate=9600)
    model = Model()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to open video source")
        bridge.close()
        return

    cv2.namedWindow('camera view', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('camera view', 640, 480)

    p_center = [320, 240]

    # CSVログと画像保存用のパス
    csv_filename = "C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\20250306\\histeresis\\histeresis_95mm_315deg.csv"
    out_img_dir = "C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\20250306\\histeresis\\images_95mm_315deg\\"
    
    i = 1
    j = 1

    toggle_state = False
    visualize_circle = False

    with open(csv_filename, 'w', newline='') as f:
        writer = csv.writer(f)

        while True:
            ret, img = cap.read()
            if not ret:
                print("Warning: Failed to read from camera.")
                continue

            time.sleep(0.25)

            if visualize_circle:
                visualize_reference_trajectory(img, p_center)

            cv2.imshow("camera view", img)

            key = cv2.waitKey(10) & 0xFF

            if key == ord('q'):
                break

            if key == 13: # Enterに対応
                toggle_state = not toggle_state
                if toggle_state:
                    theta_ref = 90.0
                    phi_ref = 315.0
                else:
                    theta_ref = 1e-5 # 0除算回避
                    phi_ref = 0.0

                rotate_angle = model.cal_rotate_angle(theta_ref, phi_ref)
                bridge.send(rotate_angle)

                writer.writerow([i, theta_ref, phi_ref])
                cv2.imwrite(f"{out_img_dir}histeresis_20250307_{i}.jpg", img)

                i += 1
            
            if key == ord('s'):
                cv2.imwrite(f"{out_img_dir}histeresis_20250307_start_{j}.jpg", img)
                j += 1
                
            if key == ord('c'):
                visualize_circle = not visualize_circle 

    cap.release()
    cv2.destroyAllWindows()
    bridge.close()


if __name__ == '__main__':
    main()