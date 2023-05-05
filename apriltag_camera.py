import cv2
import math
import pupil_apriltags as apriltag
import time
# 設定攝影機編號
cam_id = 0

# 設定攝影機視訊大小
cam_width = 1920
cam_height = 1080

global cam, error_of_angle

# 設定攝影機
cam = cv2.VideoCapture(cam_id)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, cam_width)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_height)

width = cam.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)

bool_angle = False

slope = 0
i = 0
j = 0
k = 1

END_AD_POSITIONS = []
END_BC_POSITIONS = []
angle_of_msrr = []

# 創建一個apriltag，接著檢測AprilTags
options = apriltag.Detector(families='tag36h11')  # windows

while True:
    
    # 讀取攝影機畫面
    ret, image = cam.read()
    
    # 如果無法讀取畫面，跳出迴圈
    if not ret:
        break

    # 將彩色影像轉換為灰度影像
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
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

        # 顯示檢測到的AprilTag文字
        # tagFamily = r.tag_family.decode("utf-8")

        # 計算 AprilTag 的旋轉角度，並考慮角度為90°或270°而產生斜率為 ∞ 之情形
        slope = 0
        special_factor = 0

        if b[0] - a[0] == 0 and b[1] < a[1]:
            angle = 90
            special_factor = 1
        elif a[1] < b[1] and b[0] - a[0] == 0:
            angle = 270
            special_factor = 1
        else:
            slope = (b[1]-a[1])/(b[0]-a[0])

        angle = math.degrees(math.atan(slope))
        angle = round(angle, 2)        
        # print('Slope =', slope)

        # ↓ 找出線段中點 ↓ #
        mid_bc_x = int((c[0]+b[0])/2)
        mid_bc_y = int((c[1]+b[1])/2)
        mid_ad_x = int((a[0]+d[0])/2)
        mid_ad_y = int((a[1]+d[1])/2)

        global mid_ad
        mid_ad = (mid_ad_x, mid_ad_y)
        mid_bc = (mid_bc_x, mid_bc_y)
        end_ad = (0, 0)
        end_bc = (0, 0)

        if mid_ad[0]-mid_bc[0] == 0 :
            mid_angle = 90
        elif b[1] < c[1] and mid_ad[0]-mid_bc[0] == 0:
            mid_angle = 270
        else:
            mid_slope = (mid_ad[1]-mid_bc[1])/(mid_ad[0]-mid_bc[0])
            mid_angle = abs(math.degrees(math.atan(mid_slope)))

        # ↓ 設定延伸線的長度係數 ↓ #
        extend_factor = 130
        com_angle = 0

        if special_factor == 0:
# ------------------------------------------------ ↓ 設定4種情況下角度輸出 ↓ ------------------------------------------------ #

            if a[0] < b[0] and a[1] > b[1]: # 當線段 AB 在 第 I 象限之情況
                quadrant = 1
                com_angle = abs(angle)
                # 當線段 AB 為第 I 象限情況時，BC線段會在第 II 象限
                end_bc = (int(mid_bc_x+extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y-extend_factor*math.sin(mid_angle*math.pi/180)))
                end_ad = (int(mid_ad_x-extend_factor*math.cos(mid_angle*math.pi/180)), int( mid_ad_y+extend_factor*math.sin(mid_angle*math.pi/180)))

            elif a[0] > b[0] and a[1] > b[1]: # 當線段 AB 在 第 II 象限之情況
                quadrant = 2         
                com_angle = (90-angle)+90
                # 當線段 AB 為第 II 象限情況時，BC線段會在第 III 象限
                end_bc = (int(mid_bc_x-extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y-extend_factor*math.sin(mid_angle*math.pi/180)))
                end_ad = (int( mid_ad_x+extend_factor*math.cos(mid_angle*math.pi/180)), int( mid_ad_y+extend_factor*math.sin(mid_angle*math.pi/180)))

            elif a[0] > b[0] and a[1] < b[1] : # 當線段 AB 在 第 III 象限之情況
                quadrant = 3     
                com_angle = abs(angle)+180
                # 當線段 AB 為第 III 象限情況時，BC線段會在第 IV 象限
                end_bc = (int(mid_bc_x-extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y+extend_factor*math.sin(mid_angle*math.pi/180)))
                end_ad = (int( mid_ad_x+extend_factor*math.cos(mid_angle*math.pi/180)), int( mid_ad_y-extend_factor*math.sin(mid_angle*math.pi/180)))

            elif a[0] < b[0] and a[1] < b[1]: # 當線段 AB 在 第 IV 象限之情況
                quadrant = 4
                com_angle = (90-angle)+270
                # 當線段 AB 為第 IV 象限情況時，BC線段會在第 I 象限  
                end_bc = (int(mid_bc_x+extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y+extend_factor*math.sin(mid_angle*math.pi/180)))
                end_ad = (int( mid_ad_x-extend_factor*math.cos(mid_angle*math.pi/180)), int( mid_ad_y-extend_factor*math.sin(mid_angle*math.pi/180)))

        END_AD_POSITIONS.append(end_ad)
        END_BC_POSITIONS.append(end_bc)

        angle_of_msrr.append(com_angle)
        
        if len(angle_of_msrr) > 2:
            error_of_angle = abs(angle_of_msrr[0]-angle_of_msrr[1])
            cv2.putText(image, str(error_of_angle), (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (130, 180, 0), 2)

        if len(angle_of_msrr) == 3:
            # 由於每次迴圈執行時需要取代掉的 list 位置不同，僅考慮有兩個的情況下，使用一 boolean 函數判斷新進數值需要取代掉哪一個原本的 list 數值
            bool_angle = not bool_angle
            if bool_angle :
                angle_of_msrr[0] = angle_of_msrr[2]
            else:
                angle_of_msrr[1] = angle_of_msrr[2]

            del angle_of_msrr[2]

        
        print("Angle of MSRR : ", angle_of_msrr)

        # ↓ 繪製延伸線段中點連線 ↓ #
        cv2.line(image, end_ad, end_bc, (255, 255, 0), 2, lineType=cv2.LINE_8)

        # ↓ 標註線段中點 ↓ #
        cv2.circle(image, (mid_bc[0], mid_bc[1]), 1, (0, 0, 255), 5)
        cv2.circle(image, (mid_ad[0], mid_ad[1]), 1, (0, 0, 255), 5)

        # ↓ 標註物件之旋轉角度 ↓ #
        cv2.putText(image, str(round(com_angle,2)), (cen[0]-35, cen[1]-15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (130, 180, 0), 2)
        # cv2.putText(image, 'a', (a[0], a[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 180, 255), 2) 
        # cv2.putText(image, 'b', (b[0], b[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 180, 255), 2)        
        # cv2.putText(image, 'c', (c[0], c[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 180, 255), 2)
        # cv2.putText(image, 'd', (d[0], d[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 180, 255), 2)
        cv2.putText(image, str(quadrant), (cen[0]-35, cen[1]+5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)  
        cv2.putText(image, str(mid_ad), (mid_ad_x, mid_ad_y), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1 )

    cv2.imshow('AprilTag', image)
        
    if cv2.waitKey(1) & 0xFF == 27:
        break
    
# 釋放資源
cam.release()
cv2.destroyAllWindows()

