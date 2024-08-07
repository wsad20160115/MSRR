import cv2
import pupil_apriltags as apriltag
import math


# 設定 END_BC 與 END_AD 的 list
END_BC_POSITIONS = []
END_AD_POSITIONS = []


# 設定 j、k 來進行迴圈的設定
j, k = 0,0

# 創建一個apriltag，接著檢測AprilTags
options = apriltag.Detector(families='tag36h11')  # windows
angle_of_msrr = []
list_of_tag_id = []

    # -------------- ↓ Apriltag 檢測器 ↓ -------------- # 
def tag(image):
    
    global mid_ad, com_angle, angle_of_msrr, error_of_angle, tag_id, list_of_tag_id
    tag_id = 1000
    quadrant = 0
    com_angle = 0
    slope = 0
    error_of_angle = 0

    mid_ad = []
    

    special_factor = False # 判斷 MSRR 是否為特殊角度如:90°、270°
    bool_angle = False

    #image = cv2.flip(image, 1)
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
        
        # 取得 AprilTag 之 ID
        tag_id = r.tag_id

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
        # cv2.putText(image, r.tag_Family, (a[0], a[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        # cv2.putText(image, 'a', (a[0]-10, a[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        # cv2.putText(image, 'b', (b[0]-10, b[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        # cv2.putText(image, 'c', (c[0]-10, c[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0 , 255), 2)
        #cv2.putText(image, 'd', (d[0]-10, d[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # 計算 AprilTag 的旋轉角度，並考慮角度為90°或270°而產生斜率為 ∞ 之情形

        if b[0] - a[0] == 0 and b[1] < a[1]:
            angle = 90
            special_factor = True

        elif a[1] < b[1] and b[0] - a[0] == 0:
            angle = 270
            special_factor = True

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
        extend_factor = 200

        if special_factor == False:
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
                com_angle = (90-abs(angle))+270
                # 當線段 AB 為第 IV 象限情況時，BC線段會在第 I 象限  
                end_bc = (int(mid_bc_x+extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y+extend_factor*math.sin(mid_angle*math.pi/180)))
                end_ad = (int( mid_ad_x-extend_factor*math.cos(mid_angle*math.pi/180)), int( mid_ad_y-extend_factor*math.sin(mid_angle*math.pi/180))) 

        END_AD_POSITIONS.append(end_ad)
        END_BC_POSITIONS.append(end_bc)
        
        # 存取影像中的 AprilTag 角度        
        if len(angle_of_msrr) < 2 :
            angle_of_msrr.append(com_angle)

        elif len(angle_of_msrr) == 2:

            if tag_id == 0:
                angle_of_msrr[0] = com_angle
                angle_of_msrr[1] = angle_of_msrr[1]

            if tag_id == 1:
                angle_of_msrr[0] = angle_of_msrr[0]
                angle_of_msrr[1] = com_angle
        
        if tag_id not in list_of_tag_id:
            list_of_tag_id.append(tag_id)
        
        # ↓ 繪製延伸線段中點連線 ↓ #

        cv2.line(image, mid_bc, end_bc, (255, 50, 0), 2, lineType=cv2.LINE_8)

        # ↓ 標註線段中點與中心點 ↓ #
        cv2.circle(image, (mid_bc[0], mid_bc[1]), 1, (130, 180, 255), 4)
        
        com_angle_format = '{:.2f}'.format(com_angle)
        # ↓ 標註物件之旋轉角度 ↓ #
        cv2.putText(image, str(tag_id), (cen[0], cen[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (25, 30, 200), 2)
        cv2.putText(image, com_angle_format, (cen[0]-35, cen[1]-15), cv2.FONT_HERSHEY_COMPLEX, 0.8, (180, 255, 0), 2)
        #cv2.putText(image, "Center", (mid_ad[0]-10, mid_ad[1]-10), cv2.FONT_ITALIC, 0.7, (150, 150, 255), 2)
                
def get_angle():
    return angle_of_msrr

def get_list_of_tag_id():
    return list_of_tag_id
    # def get_MID(self):
    #     return self.mid_ad    
