import os
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def cal_current_degree(image, image_init):
    """
    与えられた画像から先端部の位置を推定し、h (距離) と phi (角度) を計算します。

    Args:
        image (np.ndarray): 現在のロボットの画像。
        image_init (np.ndarray): ロボットが初期姿勢にある時の画像。

    Returns:
        tuple: (h_current, phi_current) - ロボットの先端までの距離[ピクセル]と角度[ラジアン]。
    """
    # グレースケール変換と輝度調整
    # 200以下の値を1/100にすることで、暗い部分のノイズを抑える
    image_float = image.astype(np.float32)
    image_init_float = image_init.astype(np.float32)
    image_float[image_float < 200] = image_float[image_float < 200] / 100.0
    image_init_float[image_init_float < 200] = image_init_float[image_init_float < 200] / 100.0

    # 浮動小数をuint8にクリップ＆変換
    image_proc = np.clip(image_float, 0, 255).astype(np.uint8)
    image_init_proc = np.clip(image_init_float, 0, 255).astype(np.uint8)

    # 画像の差分を取る
    diff_img = cv2.absdiff(image_proc, image_init_proc)
    
    # 差分画像から輝度が高い部分（＝動いた部分）を抽出
    _, bin_img = cv2.threshold(diff_img, 50, 255, cv2.THRESH_BINARY)
    
    # 輪郭を見つける
    contours, _ = cv2.findContours(bin_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    points = []
    if contours:
        # 面積の大きい順にソートして、上位3つの輪郭の中心を求める
        contours.sort(key=cv2.contourArea, reverse=True)
        for i in range(min(3, len(contours))):
            M = cv2.moments(contours[i])
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                points.append((cx, cy))
    
    if len(points) < 3:
        # 必要な点が検出できない場合はエラーメッセージを返す
        print("Warning: Could not detect 3 points for calculation.")
        return 0, 0
    
    # 画像の中心に近い点をp1（根元）、それ以外の2点をp2, p3と見なす
    h, w = bin_img.shape
    center = (w//2, h//2)
    
    def dist(p1, p2):
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    # 中心から一番近い点を根元(p1)とする
    sorted_points = sorted(points, key=lambda p: dist(p, center))
    p1 = sorted_points[0]
    p2, p3 = sorted_points[1], sorted_points[2]

    # p1, p2, p3を使って角度と距離を計算
    vec_p1p2 = np.array(p2) - np.array(p1)
    vec_p1p3 = np.array(p3) - np.array(p1)

    dot_product = np.dot(vec_p1p2, vec_p1p3)
    norm_p1p2 = np.linalg.norm(vec_p1p2)
    norm_p1p3 = np.linalg.norm(vec_p1p3)

    if norm_p1p2 == 0 or norm_p1p3 == 0:
        return 0, 0

    cos_phi = dot_product / (norm_p1p2 * norm_p1p3)
    cos_phi = np.clip(cos_phi, -1.0, 1.0) # 値域を[-1, 1]にクリップ

    phi_current = np.arccos(cos_phi)
    h_current = dist(p1, p2)
    
    return h_current, phi_current # h_current: p1とp2の距離, phi_current: p1とp2,p3が作る角度[ラジアン]

def visualize_reference_trajectory(img, p_center):

    cv2.circle(img, (p_center[0], p_center[1]), 100, (255, 0, 0), thickness=3)

def plot_data_from_csv(csv_path, title, x_label, y_label, save_path=None):
    """
    CSVファイルからデータを読み込み、プロットして表示・保存します。

    Args:
        csv_path (str): CSVファイルのパス。
        title (str): グラフのタイトル。
        x_label (str): x軸のラベル。
        y_label (str): y軸のラベル。
        save_path (str, optional): グラフを保存するパス。指定しない場合は保存しない。
    """
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_path}")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(df[x_label], df[y_label], marker='o', linestyle='-')
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True)

    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"Plot saved to {save_path}")
    
    plt.show()