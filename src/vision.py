import cv2
import os

# 画像が入ったディレクトリを指定
image_dir = "C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\70mm_traj"

# 動画のパラメータ
output_path = "C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\70mm_traj\\output.mp4"  # 出力ファイル名
fps = 10                    # フレームレート (1秒あたり何コマ表示するか)

# ディレクトリ内の画像ファイルをソートして取得
files = sorted([f for f in os.listdir(image_dir) 
                if f.lower().endswith(('.jpg', '.png', '.jpeg'))])

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