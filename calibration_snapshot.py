import cv2
 # 設定攝影機編號
cam_id = 0

# 設定攝影機視訊大小
cam_width = 1920*0.7
cam_height = 1080*0.7

# 設定攝影機
cam = cv2.VideoCapture(cam_id)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)

i = 0
while 1:
    (grabbed, img) = cam.read()
    cv2.imshow('img',img)
    if cv2.waitKey(1) & 0xFF == ord('j'):  # 按j保存一张图片
        i += 1
        u = str(i)
        firename=str('./calibration/calibration_img'+u+'.jpg')
        cv2.imwrite(firename, img)
        print('寫入：',firename)
    if cv2.waitKey(1) & 0xFF == 27:
        break

