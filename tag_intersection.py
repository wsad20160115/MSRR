import cv2
import pupil_apriltags as apriltag
import math

def intersection(frame):
    global intersection_x, intersection_y
    
    intersection_x = 0
    intersection_y = 0

    image = frame

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 設置旗標 flag 用以除錯及檢測狀態
    flag = 0

    END_AD_POSITIONS = []
    END_BC_POSITIONS = []

    # 創建一個AprilTag檢測器，接著檢測影像中的AprilTag
    options = apriltag.Detector(families='tag36h11')

    results = options.detect(gray)

    i = 0
    j = 0
    k = 1

    distance = 0

    for r in results:
        
        i = i + 1
        # 獲取4个角點的座標
        b = (tuple(r.corners[0].astype(int))[0], tuple(r.corners[0].astype(int))[1])
        c = (tuple(r.corners[1].astype(int))[0], tuple(r.corners[1].astype(int))[1])
        d = (tuple(r.corners[2].astype(int))[0], tuple(r.corners[2].astype(int))[1])
        a = (tuple(r.corners[3].astype(int))[0], tuple(r.corners[3].astype(int))[1])
        
        # 取得 AprilTag 的中心座標
        cen = (int(r.center[0]), int(r.center[1]))
        
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

        if b[0] < c[0] and b[1] < c[1]:
            end_bc = (int(mid_bc_x-extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y+extend_factor*math.sin(mid_angle*math.pi/180)))
            end_ad = (int(mid_ad_x+extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_ad_y-extend_factor*math.sin(mid_angle*math.pi/180)))
        elif b[0] < c[0] and b[1] > c[1]:
            end_bc = (int(mid_bc_x+extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y+extend_factor*math.sin(mid_angle*math.pi/180)))
            end_ad = (int(mid_ad_x-extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_ad_y-extend_factor*math.sin(mid_angle*math.pi/180)))
        elif b[0] > c[0] and b[1] > c[1]:
            end_bc = (int(mid_bc_x+extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y-extend_factor*math.sin(mid_angle*math.pi/180)))
            end_ad = (int(mid_ad_x-extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_ad_y+extend_factor*math.sin(mid_angle*math.pi/180)))
        else :
            end_bc = (int(mid_bc_x-extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y-extend_factor*math.sin(mid_angle*math.pi/180)))
            end_ad = (int(mid_ad_x+extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_ad_y+extend_factor*math.sin(mid_angle*math.pi/180)))

        END_AD_POSITIONS.append(end_ad)
        END_BC_POSITIONS.append(end_bc)

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
                        # print("j = ", j , "k = ", k)
                        # print(f"Intersection point: ({globals.intersection_x:.2f}, {globals.intersection_y:.2f})")
                    else:
                        print("Lines are parallel")
    cv2.imshow('image', image)