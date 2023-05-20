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
    # 校正影像畸變
    dst2 = cv2.undistort(frame, mtx, dist, None, newcameramtx)
    mapx,mapy=cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtx,(w1,h1),5)
    dst2=cv2.remap(frame,mapx,mapy,cv2.INTER_LINEAR)
    
    return dst2