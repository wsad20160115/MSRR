import cv2
import pickle

with open('calibration_parameter.pkl', 'rb') as calibrate:
    calib_params = pickle.load(calibrate)

mtx = calib_params['mtx']
dist = calib_params['dist']
rvecs = calib_params['rvecs']
tvecs = calib_params['tvecs']
u = calib_params['u']
v = calib_params['v']

def calibration(frame):
    
    h1, w1 = frame.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (u, v), 0, (u, v))
    # 纠正畸变
    dst1 = cv2.undistort(frame, mtx, dist, None, newcameramtx)
    dst2 = cv2.undistort(frame, mtx, dist, None, newcameramtx)
    mapx,mapy=cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtx,(w1,h1),5)
    dst2=cv2.remap(frame,mapx,mapy,cv2.INTER_LINEAR)
    # 裁剪图像，输出纠正畸变以后的图片
    x, y, w1, h1 = roi
    dst1 = dst1[y:y + h1, x:x + w1]

    return dst2