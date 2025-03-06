import cv2

# 画像の読み込み
img = cv2.imread("C:\\Users\\user\\venv\\soft_robot\\intuitive-UI-continuum-robot\\data\\95mm_traj\\95mm_traj_419.jpg",  cv2.IMREAD_COLOR)
# 閾値の設定
threshold = 250

# 二値化(閾値100を超えた画素を255にする。)
ret, img_thresh = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)

# 二値化画像の表示
cv2.imshow("img_raw", img)
cv2.imshow("img_th", img_thresh)
cv2.waitKey()
cv2.destroyAllWindows()