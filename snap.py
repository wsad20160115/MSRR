import cv2

# 設定攝影機編號
cam_id = 0

# 設定攝影機視訊大小
cam_width = 1344
cam_height = 756

global cam, error_of_angle

# 設定攝影機
cam = cv2.VideoCapture(cam_id)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)

width = cam.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)

ret, frame = cam.read()

cv2.imwrite("./image/snap.jpg", frame)