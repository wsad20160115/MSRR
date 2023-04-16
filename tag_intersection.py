import cv2
import pupil_apriltags as apriltag
import math

intersection_img = cv2.imread('./image/snapshot.jpg')

def intersection(self, image):
    
    # image = cv2.flip(image, 1)
    self.gray = cv2.cvtColor(intersection_img, cv2.COLOR_BGR2GRAY)

    i = 0
    j = 0
    k = 1

    # 設置旗標 flag 用以除錯及檢測狀態
    flag = 0

    self.END_AD_POSITIONS = []
    self.END_BC_POSITIONS = []

    extend_factor = 1000

    if flag == 1:
        end_bc = (int(mid_bc_x-extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y+extend_factor*math.sin(mid_angle*math.pi/180)))
        end_ad = (int(mid_ad_x+extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_ad_y-extend_factor*math.sin(mid_angle*math.pi/180)))

    elif flag == 2:
        end_bc = (int(mid_bc_x+extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y+extend_factor*math.sin(mid_angle*math.pi/180)))
        end_ad = (int(mid_ad_x-extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_ad_y-extend_factor*math.sin(mid_angle*math.pi/180)))

    elif flag == 3:
        end_bc = (int(mid_bc_x+extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y-extend_factor*math.sin(mid_angle*math.pi/180)))
        end_ad = (int(mid_ad_x-extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_ad_y+extend_factor*math.sin(mid_angle*math.pi/180)))

    else :
        end_bc = (int(mid_bc_x-extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y-extend_factor*math.sin(mid_angle*math.pi/180)))
        end_ad = (int(mid_ad_x+extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_ad_y+extend_factor*math.sin(mid_angle*math.pi/180)))

    self.END_AD_POSITIONS.append(end_ad)
    self.END_BC_POSITIONS.append(end_bc)

    # ↓ 計算兩中心線段 X 、 Y 座標  ↓ #
    # print("\nFlag = ", flag)
    # print("Mid Angle = ", round(mid_angle,2))
    # print("Angle = ", angle)
    # i從1開始，但儲存兩個END Points的List之初使存儲位置為 0
    # print("i = ", i) 
    # print("END AD = ", END_AD_POSITIONS[i-1]) 
    # print("END BC = ", END_BC_POSITIONS[i-1])
    
    # cv2.putText(self.image, str(flag), (cen[0]-10, cen[1]-35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (130, 180, 0), 2)
    # cv2.putText(self.image, str(com_angle), (cen[0]-35, cen[1]-15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (130, 180, 0), 2)
    
    # 設定 MSRR 延伸線位置
    cv2.circle(self.intersection_img, (end_bc[0], end_bc[1]), 1, (250, 255, 0),10)  
    cv2.circle(self.intersection_img, (end_ad[0], end_ad[1]), 1, (250, 255, 0), 10)

    # cv2.putText(image, 'MID_BC', (mid_bc[0]-15, mid_bc[1]-15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    # cv2.putText(image, 'MID_AD', (mid_ad[0]-15, mid_ad[1]-15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # ↓ 繪製線段中點連線 ↓ #
    # cv2.line(self.image, mid_ad, mid_bc, (0, 220, 180), 2, lineType=cv2.LINE_8)
    
    # ↓ 繪製延伸線 ↓ #
    # cv2.line(self.image, end_ad, end_bc, (255, 255, 0), 2, lineType=cv2.LINE_8)

    # 標註中心點
    # cv2.circle(self.image, (cen[0], cen[1]), 1, (0, 0, 255),5 )

    # ↓ 標註線段中點 ↓ #
    # cv2.circle(self.image, (mid_bc[0], mid_bc[1]), 1, (250, 255, 0), 3)
    # cv2.circle(self.image, (mid_ad[0], mid_ad[1]), 1, (250, 255, 0), 3)
    
    # cv2.circle(image, (int(end_ad[0]), int(end_ad[1])), 1, (250, 255, 0), 10)

    if len(self.END_BC_POSITIONS) < i or len(self.END_AD_POSITIONS) < i :
        pass
    else :       
        for k in range (i):
            for j in range (k):
                
                x1, y1 = self.END_BC_POSITIONS[j]  # Line_1 start point
                x2, y2 = self.END_AD_POSITIONS[j]  # Line_1 end point

                x3, y3 = self.END_BC_POSITIONS[k]  # Line_2 start point
                x4, y4 = self.END_AD_POSITIONS[k]  # Line_2 end point

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

                cv2.circle(self.intersection_img, (int(intersection_x), int(intersection_y)), 1, (0, 200, 255), 10)
                cv2.putText(self.intersection_img, "CrossPoint", (int(intersection_x)-50, int(intersection_y)-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
