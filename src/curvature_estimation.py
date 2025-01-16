import csv
import time
import serial

# Serial Bridge
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

with open('data/curvature_estimation_data.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['curvature', 'rho'])

    curvature = 0.0

    for i in range(100):
        # Arduinoから値を受信
        line = ser.readline().decode('utf-8').strip()

        if not line:
            # 受信できなければ待機
            time.sleep(0.1)
            continue

        data = line.split(',')
        rho = float(data[0])
        print(curvature, rho)
        
        # CSVファイルに書き込み
        writer.writerow([curvature, rho])

        time.sleep(0.1)
