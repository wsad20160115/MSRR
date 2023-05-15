import pupil_apriltags as apriltag
import cv2

import numpy as np
import glob

# 設定攝影機編號
cam_id = 0

# 設定攝影機視訊大小
cam_width = 1920*0.5
cam_height = 1080*0.5

global cam

# 設定攝影機
cam = cv2.VideoCapture(cam_id)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)
# 找棋盘格角点
# 设置寻找亚像素角点的参数，采用的停止准则是最大循环次数30和最大误差容限0.001
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001) # 阈值
#棋盘格模板规格
w = 9   # 10 - 1
h = 6   # 7  - 1
# 世界坐标系中的棋盘格点,例如(0,0,0), (1,0,0), (2,0,0) ....,(8,5,0)，去掉Z坐标，记为二维矩阵
objp = np.zeros((w*h,3), np.float32)
objp[:,:2] = np.mgrid[0:w,0:h].T.reshape(-1,2)
objp = objp*18.1  # 18.1 mm

# 储存棋盘格角点的世界坐标和图像坐标对
objpoints = [] # 在世界坐标系中的三维点
imgpoints = [] # 在图像平面的二维点
#加载pic文件夹下所有的jpg图像
images = glob.glob('./calibration/*.jpg')  #   拍摄的十几张棋盘图片所在目录

i=0

for fname in images:

    img = cv2.imread(fname)
    # 獲取影像中心點
    # 獲取影像的長寬
    h1, w1 = img.shape[0], img.shape[1]
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    u, v = img.shape[:2]
    # 找到棋盘格角点
    ret, corners = cv2.findChessboardCorners(gray, (w,h),None)
    # 如果找到足够点对，将其存储起来
    if ret == True:
        print("i:", i)
        i = i+1
        # 在原角点的基础上寻找亚像素角点
        cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        #追加进入世界三维点和平面二维点中
        objpoints.append(objp)
        imgpoints.append(corners)
        
# 校正
ret, mtx, dist, rvecs, tvecs = \
    cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (u, v), 0, (u, v))

# 設定攝影機編號
cam_id = 0

# 設定攝影機視訊大小
cam_width = 1920*0.7
cam_height = 1080*0.7

# 設定攝影機
cam = cv2.VideoCapture(cam_id)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)

ret,frame = cam.read()
h1, w1 = frame.shape[:2]
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (u, v), 0, (u, v))
# 校正畸變
dst1 = cv2.undistort(frame, mtx, dist, None, newcameramtx)
dst2 = cv2.undistort(frame, mtx, dist, None, newcameramtx)
mapx,mapy=cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtx,(w1,h1),5)
dst2=cv2.remap(frame,mapx,mapy,cv2.INTER_LINEAR)
frame = dst2
# 裁剪图像，输出纠正畸变以后的图片
x, y, w1, h1 = roi
dst1 = dst1[y:y + h1, x:x + w1]

# image = cv2.flip(image, 1)
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
dist_real = 71 # mm

# 計算像素與實際長度的換算關係
pixels_per_mm = dist_pixels / dist_real

print('Dist Pixels = ', dist_pixels, 'Dist real = ', dist_real)
print('像素與實際長度的換算關係為:', pixels_per_mm, 'pixels/mm')
print(f'Distance = {dist_pixels/0.71} mm ')