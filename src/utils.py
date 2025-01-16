import os
import cv2
import numpy as np

points = [] # 白い部分の座標を保存

def cal_current_degree(image, image_init):
    # 一枚の画像から以下の処理をする
    
    # グレースケール変換をして，200より下の値は1/100にする処理
    # 二値化処理（閾値は適宜調整）
    # 窓を動かして平均輝度を計算
    # 平均輝度が閾値以上の点を白い点として取得
    # 点の個数が2点だった場合，中心に近い方をp1とし，もう一つの点をp2とする．p1のy座標が同じ点のうちで，x座標が正の点をp3とする．
    # p1, p2, p3の座標からp1に対する角度（phi_current）・p1とp2の距離（h_current）を計算する
    # phi_currentとh_currentを返す

    # グレースケール変換をして，200より下の値は1/100にする処理
    image_float = image.astype(np.float32)
    image_init_float = image_init.astype(np.float32)
    image_float[image_float < 200] = image_float[image_float < 200] / 100.0
    image_init_float[image_init_float < 200] = image_init_float[image_init_float < 200] / 100.0

    # 浮動小数をuint8にクリップ＆変換（0～255範囲内に収める）
    image_proc = np.clip(image_float, 0, 255).astype(np.uint8)
    image_init_proc = np.clip(image_init_float, 0, 255).astype(np.uint8)

    # 二値化処理（閾値は適宜調整）
    _, bin_img = cv2.threshold(image_proc, 200, 255, cv2.THRESH_BINARY)
    _, bin_init_img = cv2.threshold(image_init_proc, 200, 255, cv2.THRESH_BINARY)

    # 足し合わせて平均
    avg_img = (bin_img.astype(np.float32) + bin_init_img.astype(np.float32)) / 2.0

    h, w = avg_img.shape
    window_w = max(1, w // 50)
    window_h = max(1, h // 50)

    brightness_values = []
    coords = []

    # ウィンドウごとの平均輝度計算
    for cy in range(window_h//2, h - window_h//2, window_h):
        for cx in range(window_w//2, w - window_w//2, window_w):
            y1 = cy - window_h//2
            y2 = cy + window_h//2
            x1 = cx - window_w//2
            x2 = cx + window_w//2

            window = bin_img[y1:y2, x1:x2]
            mean_val = np.mean(window)
            brightness_values.append(mean_val)
            coords.append((cx, cy))

    brightness_values = np.array(brightness_values)
    min_val = np.min(brightness_values)
    max_val = np.max(brightness_values)

    if max_val != min_val:
        norm_brightness = (brightness_values - min_val) / (max_val - min_val)
    else:
        norm_brightness = np.zeros_like(brightness_values)

    # 閾値処理して白い点と判定（ここでは0.7としているがすでに実質的にバイナリになっている）
    threshold_value = 0.7
    for i, val in enumerate(norm_brightness):
        if val >= threshold_value:
            points.append(coords[i])

    # 点の個数が２点だった場合，中心に近い方をp1とし，もう一つの点をp2とする．p1のy座標が同じ点のうちで，x座標が正の点をp3とする．
    p1, p2, p3 = points[0], points[1], points[2]
    center = (w//2, h//2)

    def dist(a, b):
        return (a[0]-b[0])**2 + (a[1]-b[1])**2
    
    sorted_points = sorted([p1, p2, p3], key=lambda p: dist(p, center))

    vertex = sorted_points[0]
    others = sorted_points[1:]
    A, B, C = others[0], vertex, others[1]

    BA = (A[0] - B[0], A[1] - B[1])
    BC = (C[0] - B[0], C[1] - B[1])

    norm_ba = np.sqrt(BA[0]**2 + BA[1]**2)
    norm_bc = np.sqrt(BC[0]**2 + BC[1]**2)

    dot = BA[0]*BC[0] + BA[1]*BC[1]
    cos_phi = dot / (norm_ba * norm_bc)
    cos_phi = max(min(cos_phi, 1.0), -1.0)

    phi_current = np.arccos(cos_phi)
    
    h_current = np.sqrt((B[0] - A[0])**2 + (B[1] - A[1])**2)
    
    return h_current, phi_current # h_current: p1とp2の距離, phi_current: p1に対する角度[rad]


def visualize_reference_point(p_center, rho, phi):
    # 画像に本来の位置を表示
    # いずれこの誤差をNNか強化学習でほかしていく

    h = 0
    h_pixel = 
    # pixelとの対応
    px, py = p_center + h * np.cos(phi), p_center + h * np.sin(phi)

def visualize_reference_trajectory():
    # 画像に目標軌道を表示
    # 目標軌道に思い通りに追従できるか？
    pass

def analyze_trajectory():
    # 先端の動きを一枚の画像に表示させるための関数
    pass

