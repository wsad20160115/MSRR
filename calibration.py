import cv2
import numpy as np
import glob

def init_calibration():
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
        # 获取画面中心点
        #获取图像的长宽
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


    ret, mtx, dist, rvecs, tvecs = \
        cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    return mtx, dist, rvecs, tvecs, u, v

def show_calibration(self, frame):
    counter = 1
    if counter == 1:
        mtx, dist, rvecs, tvecs, u, v = init_calibration()
        counter = 2
    elif counter == 2:
        mtx = mtx
        dist = dist
        rvecs = rvecs
        tvecs = tvecs
        u = u
        v = v
    
    # print('rvecs : ', rvecs)
    # print('tvecs : ', tvecs)

    # 設定攝影機編號
    cam_id = 0

    # 設定攝影機視訊大小
    cam_width = 1920*0.7
    cam_height = 1080*0.7

    # 設定攝影機
    cam = cv2.VideoCapture(cam_id)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)

    # while True:
    ret, frame=cam.read()
    h1, w1 = frame.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (u, v), 0, (u, v))
    # 纠正畸变

    frame = cv2.undistort(frame, mtx, dist, None, newcameramtx)
    mapx,mapy=cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtx,(w1,h1),5)
    frame = cv2.remap(frame,mapx,mapy,cv2.INTER_LINEAR)
    # 裁剪图像，输出纠正畸变以后的图片
    x, y, w1, h1 = roi

    return frame

    #     cv2.imshow('Calibration Image', frame)
        
    #     if cv2.waitKey(1) & 0xFF == 27:
    #         break
        
    # cam.release()      

# if __name__ == '__main__':
    
#     show_calibration()
    
# cv2.destroyAllWindows()