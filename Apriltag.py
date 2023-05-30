import cv2
import pupil_apriltags as apriltag
import math
import numpy as np
import pickle

image = cv2.imread('./image/snapshot.jpg')
# image = cv2.flip(image, 1)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

with open('calibration_parameter.pkl', 'rb') as calibrate:
    calib_params = pickle.load(calibrate)

mtx = calib_params['mtx']
dist = calib_params['dist']
rvecs = calib_params['rvecs']
tvecs = calib_params['tvecs']

i = 0
j = 0
k = 1

# 設置旗標 flag 用以除錯及檢測狀態
flag = 0

END_AD_POSITIONS = []
END_BC_POSITIONS = []

# 創建一個AprilTag檢測器，接著檢測影像中的AprilTag
options = apriltag.Detector(families='tag36h11')

results = options.detect(gray)

print(results)

r_cen = (0, 0)

intersection_x = 0
intersection_y = 0

for r in results:
    
    i = i + 1
    # 獲取4个角點的座標
    b = (tuple(r.corners[0].astype(int))[0], tuple(r.corners[0].astype(int))[1])
    c = (tuple(r.corners[1].astype(int))[0], tuple(r.corners[1].astype(int))[1])
    d = (tuple(r.corners[2].astype(int))[0], tuple(r.corners[2].astype(int))[1])
    a = (tuple(r.corners[3].astype(int))[0], tuple(r.corners[3].astype(int))[1])
    
    # 取得 AprilTag 的中心座標
    cen = (int(r.center[0]), int(r.center[1]))

    # 繪製檢測到的AprilTag的框
    cv2.line(image, a, b, (255, 0, 255), 1, lineType=cv2.LINE_AA)
    cv2.line(image, b, c, (255, 0, 255), 1, lineType=cv2.LINE_AA)
    cv2.line(image, c, d, (255, 0, 255), 1, lineType=cv2.LINE_AA)
    cv2.line(image, d, a, (255, 0, 255), 1, lineType=cv2.LINE_AA)

    # 在影像上顯示AprilTag的Family
    # cv2.putText(image, tagFamily, (a[0], a[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    # cv2.putText(image, 'a', (a[0]-10, a[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    cv2.putText(image, 'b', (b[0]-10, b[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    cv2.putText(image, 'c', (c[0]-10, c[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0 , 255), 2)
    # cv2.putText(image, 'd', (d[0]-10, d[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    #計算 AprilTag 的旋轉角度       
    slope = (c[1]-b[1])/(c[0]-b[0])
    angle = math.degrees(math.atan(slope))
    angle = round(angle, 2)
    # print('Slope =', slope)

    # ↓ 找出線段中點 ↓ #
    mid_bc_x = int((c[0]+b[0])/2)
    mid_bc_y = int((c[1]+b[1])/2)
    mid_ad_x = int((a[0]+d[0])/2)
    mid_ad_y = int((a[1]+d[1])/2)

    mid_ad = (mid_ad_x, mid_ad_y)
    mid_bc = (mid_bc_x, mid_bc_y)
    
    mid_slope = (mid_ad[1]-mid_bc[1])/(mid_ad[0]-mid_bc[0])
    mid_angle = abs(math.degrees(math.atan(mid_slope)))

    extend_factor = 1000
    cen_factor = 100

    if b[0] < c[0] and b[1] < c[1]:
        flag = 1        
        com_angle = angle+270
        end_bc = (int(mid_bc_x-extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y+extend_factor*math.sin(mid_angle*math.pi/180)))
        end_ad = (int(mid_ad_x+extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_ad_y-extend_factor*math.sin(mid_angle*math.pi/180)))

    elif b[0] < c[0] and b[1] > c[1]:
        flag = 2
        com_angle = abs(angle)
        end_bc = (int(mid_bc_x+extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y+extend_factor*math.sin(mid_angle*math.pi/180)))
        end_ad = (int(mid_ad_x-extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_ad_y-extend_factor*math.sin(mid_angle*math.pi/180)))
     
    elif b[0] > c[0] and b[1] > c[1]:
        flag = 3                     
        com_angle = angle+90
        end_bc = (int(mid_bc_x+extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y-extend_factor*math.sin(mid_angle*math.pi/180)))
        end_ad = (int(mid_ad_x-extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_ad_y+extend_factor*math.sin(mid_angle*math.pi/180)))

    else :
        flag = 4   
        com_angle = abs(angle)+180
        end_bc = (int(mid_bc_x-extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y-extend_factor*math.sin(mid_angle*math.pi/180)))
        end_ad = (int(mid_ad_x+extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_ad_y+extend_factor*math.sin(mid_angle*math.pi/180)))

    END_AD_POSITIONS.append(end_ad)
    END_BC_POSITIONS.append(end_bc)

    # pixel_length = np.sqrt((c[0] - b[0]) ** 2 + (c[1] - b[1]) ** 2)
    # ↓ 計算兩中心線段 X 、 Y 座標  ↓ #
    
    print("\nFlag = ", flag)
    # print('length = ', pixel_length)
    print("Mid Angle = ", round(mid_angle,2))
    print("Angle = ", angle)
    # i從1開始，但儲存兩個END Points的List之初使存儲位置為 0
    # print("i = ", i) 
    # print("END AD = ", END_AD_POSITIONS[i-1]) 
    # print("END BC = ", END_BC_POSITIONS[i-1])
    
    # cv2.putText(image, str(flag), (cen[0]-10, cen[1]-35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (130, 180, 0), 2)
    cv2.putText(image, str(com_angle), (cen[0]-35, cen[1]-15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (130, 180, 0), 2)
    
    # 設定 MSRR 延伸線位置
    cv2.circle(image, (end_bc[0], end_bc[1]), 1, (250, 255, 0),10)  
    cv2.circle(image, (end_ad[0], end_ad[1]), 1, (250, 255, 0), 10)
   

    # cv2.putText(image, 'MID_BC', (mid_bc[0]-15, mid_bc[1]-15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    # cv2.putText(image, 'MID_AD', (mid_ad[0]-15, mid_ad[1]-15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # ↓ 繪製線段中點連線 ↓ #
    # cv2.line(image, mid_ad, mid_bc, (0, 220, 180), 2, lineType=cv2.LINE_8)
    
    # ↓ 繪製延伸線 ↓ #
    cv2.line(image, end_ad, end_bc, (255, 255, 0), 1, lineType=cv2.LINE_8)

    # 標註中心點
    cv2.circle(image, (cen[0], cen[1]), 1, (0, 0, 255),5 )

    # ↓ 標註線段中點 ↓ #
    cv2.circle(image, (mid_bc[0], mid_bc[1]), 1, (250, 255, 0), 3)
    cv2.circle(image, (mid_ad[0], mid_ad[1]), 1, (250, 255, 0), 3)
    
    # cv2.circle(image, (int(end_ad[0]), int(end_ad[1])), 1, (250, 255, 0), 10)
    
    cv2.putText(image, str(flag), cen, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 0, 255), 2)

    if len(END_BC_POSITIONS) < i or len(END_AD_POSITIONS) < i :
        continue
    else :       
        for k in range (i):
            for j in range (k):
                
                x1, y1 = END_BC_POSITIONS[j]  # Line_1 start point
                x2, y2 = END_AD_POSITIONS[j]  # Line_1 end point

                x3, y3 = END_BC_POSITIONS[k]  # Line_2 start point
                x4, y4 = END_AD_POSITIONS[k]  # Line_2 end point

                denom = (y4-y3)*(x2-x1)-(x4-x3)*(y2-y1)
                
                if denom != 0 :
                    ua = ((x4-x3)*(y1-y3)-(y4-y3)*(x1-x3))/denom
                    ub = ((x2-x1)*(y1-y3)-(y2-y1)*(x1-x3))/denom
                    intersection_x = x1 + ua*(x2-x1)
                    intersection_y = y1 + ua*(y2-y1)
                    print("j = ", j , "k = ", k)
                    print(f"Intersection point: ({intersection_x:.2f}, {intersection_y:.2f})")
                    
                else:
                    print("Lines are parallel")

                text  = str(f"({intersection_x:.2f}, {intersection_y:.2f})")
                cv2.circle(image, (int(intersection_x), int(intersection_y)), 1, (0, 200, 255), 10)
                cv2.putText(image, "Intersection", (int(intersection_x)-60, int(intersection_y)+30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
                # cv2.putText(image, text, (int(intersection_x)-80, int(intersection_y)-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            distance = ((mid_ad[0] - intersection_x)**2 + (mid_ad[1] - intersection_y)**2)**0.5
           # print('Distance (mm) = ', distance/0.559025768)  
            
                          
cv2.imshow('image', image)

cv2.waitKey(0)
