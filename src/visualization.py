import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

jpg_file = "C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\20250308\\interface\\result_2.jpg"

# CSVファイルの読み込み
df_95mm = pd.read_csv(
    "C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\20250306\\interface\\interface_95mm_complete.csv"
)

# データ範囲を指定して抽出
df_95mm = df_95mm.iloc[257:371]

# 平均を計算
mean = df_95mm['theta'].mean()
print(mean)

# # グラフ描画の準備
# plt.figure(figsize=(8, 5))

# # サンプルとして、計測の順番（インデックス）を色として与える
# num_points = len(df_95mm)
# scatter = plt.scatter(
#     360 - df_95mm["phi"],
#     df_95mm["theta"],
#     c=range(num_points),   # インデックスを色付けの基準にする
#     cmap='viridis',        # お好みでカラーマップを変更
#     marker='o'
# )

# # y軸を 0 から始める
# plt.ylim(bottom=0)

# # カラーバーを表示し、ラベルをつける
# cb = plt.colorbar(scatter)
# cb.set_label('Measurement Index')

# # タイトルや軸ラベルなどの設定
# plt.title('the values of φ and θ')
# plt.xlabel('Rotate Angle φ [deg]')
# plt.ylabel('θ [deg]')

# plt.axhline(y=27.26, color='r', linestyle='--', label='theoretical value')

# # グラフをJPG形式で保存
# plt.savefig(jpg_file, dpi=300, format='jpg')

# # グラフを表示
# plt.show()
# plt.close()
