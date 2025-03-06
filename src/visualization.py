import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

csv_file = "C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\20250306\\interface\\result.csv"

# CSVファイルの読み込み
df_70mm = pd.read_csv("C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\20250306\\interface\\interface_70mm.csv")
df_95mm = pd.read_csv("C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\20250306\\interface\\interface_70mm.csv")

# 400番目から80個のデータを取り出し（範囲内であるか確認）70mm
if df_70mm.shape[0] >= 79 + 80:
    df_70mm = df_70mm.iloc[79:79 + 80]
else:
    print("データが不足しています。行数:", df_70mm.shape[0])
    df_70mm = df_70mm.iloc[79:]  # 存在する分だけ取り出す

    # 400番目から80個のデータを取り出し（範囲内であるか確認）95mm
if df_95mm.shape[0] >= 79 + 80:
    df_95mm = df_70mm.iloc[79:79 + 80]
else:
    print("データが不足しています。行数:", df_95mm.shape[0])
    df_95mm = df_95mm.iloc[79:]  # 存在する分だけ取り出す

# グラフの描画
plt.figure(figsize=(8, 5))

# メインデータのプロット
plt.plot(df_70mm["phi"], df_70mm["theta"], linestyle=':', marker='o', color='blue', label='70mm')
plt.plot(df_95mm["phi"], df_95mm["theta"], linestyle=':', marker='o', color='red',  label='95mm')

# タイトルやラベルの設定
plt.title('回転角φと曲率に対応する値θの関係')
plt.xlabel('Rotate Angle [deg]')
plt.ylabel('θ [deg]')
plt.legend()  # 凡例の表示

# グラフの表示
#plt.show()

plt.savefig(csv_file, dpi=300)  # 高解像度で保存
plt.close()
