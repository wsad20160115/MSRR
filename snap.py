import cv2

cam_id = 0
cam_width = 1920*0.5
cam_height = 1080*0.5

# 設定攝影機
cam = cv2.VideoCapture(cam_id)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)

cam = cv2.VideoCapture(cam_id)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)

# 讀取攝影機畫面
ret, image = cam.read()

# 如果無法讀取畫面，跳出迴圈
if not ret:
    print("No frame")

cv2.imshow("Snap", image)
cv2.imwrite("./image/snapshot.jpg", image )
cv2.waitKey(0)