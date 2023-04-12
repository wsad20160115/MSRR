import cv2
import math
<<<<<<< HEAD
=======

>>>>>>> 37d6f80e1906d50f44f9fb9d9f1124e5b7642dd0
import pupil_apriltags as apriltag


def run():
   
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
    
    i = 0
    j = 0
    k = 1
    END_AD_POSITIONS = []
    END_BC_POSITIONS = []

    while True:
    
        # 讀取攝影機畫面
        ret, image = cam.read()
        
        # 如果無法讀取畫面，跳出迴圈
        if not ret:
            break

        # 將彩色影像轉換為灰度影像
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 創建一個apriltag，接著檢測AprilTags
        options = apriltag.Detector(families='tag36h11')  # windows
        results = options.detect(gray)
        
        #印出 AprilTag Detector 檢測結果
        # print(results)
        r = results
    # --------------------------------------------- ↓ 找出所有AprilTag檢測的參數 ↓ --------------------------------------------- #    
        for r in results:
            # 取得 AprilTag 的中心座標
            cen = (int(r.center[0]), int(r.center[1]))
            # 獲取4个角點的座標
            b = (tuple(r.corners[0].astype(int))[0], tuple(r.corners[0].astype(int))[1])
            c = (tuple(r.corners[1].astype(int))[0], tuple(r.corners[1].astype(int))[1])
            d = (tuple(r.corners[2].astype(int))[0], tuple(r.corners[2].astype(int))[1])
            a = (tuple(r.corners[3].astype(int))[0], tuple(r.corners[3].astype(int))[1])

            # 繪製檢測到的AprilTag的框
            cv2.line(image, a, b, (255, 0, 255), 1, lineType=cv2.LINE_AA)
            cv2.line(image, b, c, (255, 0, 255), 1, lineType=cv2.LINE_AA)
            cv2.line(image, c, d, (255, 0, 255), 1, lineType=cv2.LINE_AA)
            cv2.line(image, d, a, (255, 0, 255), 1, lineType=cv2.LINE_AA)

            # 顯示 AprilTag 的中心座標
            (cX, cY) = (int(r.center[0]), int(r.center[1]))
            cv2.circle(image, (cX, cY), 3, (0, 0, 255), -1)

            # 顯示檢測到的AprilTag文字
            # tagFamily = r.tag_family.decode("utf-8")
            # cv2.putText(image, r.tag_Family, (a[0], a[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            # cv2.putText(image, 'a', (a[0]-10, a[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            # cv2.putText(image, 'b', (b[0]-10, b[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            # cv2.putText(image, 'c', (c[0]-10, c[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0 , 255), 2)
            # cv2.putText(image, 'd', (d[0]-10, d[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            if c[0]-b[0] == 0:
                slope = 90
            else:
                # 計算 AprilTag 的旋轉角度    
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
            
            if mid_ad[0]-mid_bc[0] == 0 :
                mid_angle = 90
            elif b[1] < c[1]:
                mid_angle = 270
            else:
                mid_slope = (mid_ad[1]-mid_bc[1])/(mid_ad[0]-mid_bc[0])
                mid_angle = abs(math.degrees(math.atan(mid_slope)))

            # ↓ 設定延伸線的長度係數 ↓ #
            extend_factor = 300

    # ------------------------------------------------ ↓ 設定4種情況下角度輸出 ↓ ------------------------------------------------ #
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

            elif b[0] > c[0] and b[1] < c[1]:
                flag = 4             
                com_angle = abs(angle)+180
                end_bc = (int(mid_bc_x-extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y-extend_factor*math.sin(mid_angle*math.pi/180)))
                end_ad = (int(mid_ad_x+extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_ad_y+extend_factor*math.sin(mid_angle*math.pi/180)))  

            END_AD_POSITIONS.append(end_ad)
            END_BC_POSITIONS.append(end_bc)

            # ↓ 標註線段中點 ↓ #
            cv2.circle(image, (mid_bc[0], mid_bc[1]), 1, (250, 255, 0), 3)
            cv2.circle(image, (mid_ad[0], mid_ad[1]), 1, (250, 255, 0), 3)

            # ↓ 繪製延伸線段中點連線 ↓ #
            cv2.line(image, end_ad, end_bc, (255, 255, 0), 2, lineType=cv2.LINE_8)

            # ↓ 標註物件之旋轉角度 ↓ #
            cv2.putText(image, str(round(com_angle,2)), (cen[0]-35, cen[1]-15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (130, 180, 0), 2)

            # if len(END_BC_POSITIONS) < i or len(END_AD_POSITIONS) < i :
            #     continue
            # else :       
            for k in range (i):
                for j in range (k):
                    
                    x1, y1 = END_BC_POSITIONS[j]  # Line_1 start point
                    x2, y2 = END_AD_POSITIONS[j]  # Line_1 end point

                    x3, y3 = END_BC_POSITIONS[k]  # Line_2 start point
                    x4, y4 = END_AD_POSITIONS[k]  # Line_2 end point

                    denom = (y4-y3)*(x2-x1)-(x4-x3)*(y2-y1)
                    intersection_x = 0
                    intersection_y = 0
                    if denom != 0:
                        ua = ((x4-x3)*(y1-y3)-(y4-y3)*(x1-x3))/denom
                        ub = ((x2-x1)*(y1-y3)-(y2-y1)*(x1-x3))/denom
                        intersection_x = x1 + ua*(x2-x1)
                        intersection_y = y1 + ua*(y2-y1)
                        print(f"Intersection point: ({intersection_x:.2f}, {intersection_y:.2f})")
                    else:
                        print("Lines are parallel")

                    cv2.circle(image, (int(intersection_x), int(intersection_y)), 1, (0, 200, 255), 10)

            
        cv2.imshow('AprilTag', image)
            
        if cv2.waitKey(1) & 0xFF == 27:
            break
    
    run()
    # 釋放資源
    cam.release()
    cv2.destroyAllWindows()

# if __name__ == "__main__":
#     while(True):
#         try:
#             run()
#             if cv2.waitKey(1) & 0xFF == 27:
#                 break
#         except:
#             print("bug")
        