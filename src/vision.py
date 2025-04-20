import cv2
import os
import re

def natural_sort_key(s):
    """
    ファイル名を自然順にソートするためのキーを返す関数
    例: 'img10.jpg' -> ['img', 10, '.jpg']
    """
    return [int(text) if text.isdigit() else text for text in re.split(r'(\d+)', s)]

# 画像が入ったディレクトリを指定
image_dir = "C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\20250306\\interface\\images_70mm\\"

# 動画のパラメータ
output_path = "C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\20250306\\interface\\images_70mm\\output.mp4"  # 出力ファイル名
fps = 10  # フレームレート (1秒あたり何コマ表示するか)

# ディレクトリ内の画像ファイルを取得し、自然順にソート
files = [f for f in os.listdir(image_dir) 
         if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
files = sorted(files, key=natural_sort_key)

# 最初の画像を読み込み、動画のサイズを取得
first_image_path = os.path.join(image_dir, files[0])
frame = cv2.imread(first_image_path)
height, width, channels = frame.shape

# VideoWriter の設定
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 'DIVX', 'XVID', 'mp4v' など
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# 画像を順番に書き出す
for file in files:
    img_path = os.path.join(image_dir, file)
    img = cv2.imread(img_path)
    out.write(img)

out.release()
print("動画の書き出しが完了しました:", output_path)
