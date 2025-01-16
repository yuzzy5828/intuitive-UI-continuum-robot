import os
import cv2
import numpy as np
import math

image_1 = []
image_2 = []
points = [] # 白い部分の座標を保存

def add_two_image():
    global image_1, image_2, points
    img_path_1 = os.path.join("data", "before.png")
    img_path_2 = os.path.join("data", "after.png")
    image_1 = cv2.imread(img_path_1, cv2.IMREAD_GRAYSCALE)
    image_2 = cv2.imread(img_path_2, cv2.IMREAD_GRAYSCALE)

    if image_1 is None or image_2 is None:
        print("画像の読み込みに失敗しました。パスを確認してください。")
        return

    # 上下左右100pixelをカット(トリミング)
    # 画像サイズが h×w のとき、[100:h-100, 100:w-100]でトリミング
    h, w = image_1.shape
    if h <= 200 or w <= 200:
        print("画像サイズが小さすぎます。100pxトリミング後のサイズを確認してください。")
        return
    image_1 = image_1[100:h-100, 100:w-100]
    image_2 = image_2[100:h-100, 100:w-100]

    # グレースケールとして200より下の値は1/100にする処理
    image_1_float = image_1.astype(np.float32)
    image_2_float = image_2.astype(np.float32)

    image_1_float[image_1_float < 200] = image_1_float[image_1_float < 200] / 100.0
    image_2_float[image_2_float < 200] = image_2_float[image_2_float < 200] / 100.0

    # 浮動小数をuint8にクリップ＆変換（0～255範囲内に収める）
    image_1_proc = np.clip(image_1_float, 0, 255).astype(np.uint8)
    image_2_proc = np.clip(image_2_float, 0, 255).astype(np.uint8)

    # 二値化処理（閾値は適宜調整）
    _, bin1 = cv2.threshold(image_1_proc, 200, 255, cv2.THRESH_BINARY)
    _, bin2 = cv2.threshold(image_2_proc, 200, 255, cv2.THRESH_BINARY)

    # 足し合わせて平均
    avg_img = (bin1.astype(np.float32) + bin2.astype(np.float32)) / 2.0
    # avg_imgはfloat32型なので、uint8に変換
    avg_img_uint8 = avg_img.astype(np.uint8)
    cv2.imwrite("output.png", avg_img_uint8)

    h, w = avg_img.shape
    print("Cropped and processed image size:", h, w)
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

            window = avg_img[y1:y2, x1:x2]
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

    # 閾値処理して白い点と判定（ここでは0.5以上）
    threshold_value = 0.5
    for i, val in enumerate(norm_brightness):
        if val >= threshold_value:
            points.append(coords[i])

def cal_degree():
    global points
    if len(points) != 3:
        print(f"点が3つではありません: {len(points)}個の点")
        return None

    p1, p2, p3 = points[0], points[1], points[2]

    if image_1 is None:
        print("画像が読み込まれていません。")
        return None

    h, w = image_1.shape
    center = (w/2.0, h/2.0)

    def dist(a, b):
        return (a[0]-b[0])**2 + (a[1]-b[1])**2

    # 2点のみの場合、仮想的な3点目を追加
    # p1からx方向に1pixelだけずらした点を3点目とする
    sorted_points = sorted([p1, p2, p3], key=lambda p: dist(p, center))

    vertex = sorted_points[0]
    others = sorted_points[1:]
    A, B, C = others[0], vertex, others[1]

    BA = (A[0] - B[0], A[1] - B[1])
    BC = (C[0] - B[0], C[1] - B[1])

    norm_ba = math.sqrt(BA[0]**2 + BA[1]**2)
    norm_bc = math.sqrt(BC[0]**2 + BC[1]**2)

    if norm_ba == 0 or norm_bc == 0:
        print("角度が計算できません(2点以上が同一点)")
        return None

    dot = BA[0]*BC[0] + BA[1]*BC[1]
    cos_theta = dot / (norm_ba * norm_bc)
    cos_theta = max(min(cos_theta, 1.0), -1.0)

    theta_rad = math.acos(cos_theta)
    return theta_rad

def main():
    add_two_image()
    degree = cal_degree()
    if degree is not None:
        print("求めた角度(rad):", degree)

if __name__ == "__main__":
    main()
