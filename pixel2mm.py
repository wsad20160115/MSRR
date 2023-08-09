import pupil_apriltags as apriltag
import cv2

import numpy as np


# # 設定攝影機編號
# cam_id = 0

# # 設定攝影機視訊大小
# cam_width = 1920*0.7
# cam_height = 1080*0.7

# # 設定攝影機
# cam = cv2.VideoCapture(cam_id)
# cam.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)
# cam.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)
# # 設定攝影機
# cam = cv2.VideoCapture(cam_id)
# cam.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)
# cam.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)

# ret,frame = cam.read()

# image = cv2.flip(image, 1)

frame = cv2.imread("./image/after_calibration.jpg")

gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# 創建一個AprilTag檢測器，接著檢測影像中的AprilTag
options = apriltag.Detector(families='tag36h11')

results = options.detect(gray)

for r in results:
    
    # 獲取4个角點的座標
    b = (tuple(r.corners[0].astype(int))[0], tuple(r.corners[0].astype(int))[1])
    c = (tuple(r.corners[1].astype(int))[0], tuple(r.corners[1].astype(int))[1])
    d = (tuple(r.corners[2].astype(int))[0], tuple(r.corners[2].astype(int))[1])
    a = (tuple(r.corners[3].astype(int))[0], tuple(r.corners[3].astype(int))[1])
    
    # 取得 AprilTag 的中心座標
    cen = (int(r.center[0]), int(r.center[1]))

# 計算兩點距離
dist_pixels = ((b[0] - c[0])**2 + (b[1] - c[1])**2)**0.5

# 已知的實際距離
dist_real = 62 # mm

# 計算像素與實際長度的換算關係
pixels_per_mm = dist_pixels / dist_real

print('Dist Pixels = ', dist_pixels, 'Dist real = ', dist_real)
print('像素與實際長度的換算關係為:', pixels_per_mm, 'pixels/mm')
print(f'Distance = {dist_pixels/pixels_per_mm} mm ')