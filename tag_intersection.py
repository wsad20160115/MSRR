import cv2
import pupil_apriltags as apriltag
import math

image = cv2.imread('./image/snapshot.jpg')

def intersection():
    
    # image = cv2.flip(image, 1)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    i = 0
    j = 0
    k = 1

    # 設置旗標 flag 用以除錯及檢測狀態
    flag = 0

    END_AD_POSITIONS = []
    END_BC_POSITIONS = []

    # 創建一個AprilTag檢測器，接著檢測影像中的AprilTag
    options = apriltag.Detector(families='tag36h11')

    def intersection(self):
    
    
        results = self.options.detect(self.gray)
        # print(results)

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
            cv2.line(self.image, a, b, (255, 0, 255), 1, lineType=cv2.LINE_AA)
            cv2.line(self.image, b, c, (255, 0, 255), 1, lineType=cv2.LINE_AA)
            cv2.line(self.image, c, d, (255, 0, 255), 1, lineType=cv2.LINE_AA)
            cv2.line(self.image, d, a, (255, 0, 255), 1, lineType=cv2.LINE_AA)

            # 在影像上顯示AprilTag的Family
            # cv2.putText(image, tagFamily, (a[0], a[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(self.image, 'a', (a[0]-10, a[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.putText(self.image, 'b', (b[0]-10, b[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.putText(self.image, 'c', (c[0]-10, c[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0 , 255), 2)
            cv2.putText(self.image, 'd', (d[0]-10, d[1] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

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

            if b[0] < c[0] and b[1] < c[1]:
                flag = 1
                angle = math.degrees(math.atan(slope))
                angle = round(angle, 2)   
                com_angle = angle+270
                end_bc = (int(mid_bc_x-extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y+extend_factor*math.sin(mid_angle*math.pi/180)))
                end_ad = (int(mid_ad_x+extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_ad_y-extend_factor*math.sin(mid_angle*math.pi/180)))
            elif b[0] < c[0] and b[1] > c[1]:
                flag = 2
                angle = math.degrees(math.atan(slope))
                angle = round(angle, 2)
                com_angle = abs(angle)
                end_bc = (int(mid_bc_x+extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y+extend_factor*math.sin(mid_angle*math.pi/180)))
                end_ad = (int(mid_ad_x-extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_ad_y-extend_factor*math.sin(mid_angle*math.pi/180)))
            elif b[0] > c[0] and b[1] > c[1]:
                flag = 3
                angle = math.degrees(math.atan(slope))
                angle = round(angle, 2)             
                com_angle = angle+90
                end_bc = (int(mid_bc_x+extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y-extend_factor*math.sin(mid_angle*math.pi/180)))
                end_ad = (int(mid_ad_x-extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_ad_y+extend_factor*math.sin(mid_angle*math.pi/180)))
            else :
                flag = 4
                angle = math.degrees(math.atan(slope))
                angle = round(angle, 2)       
                com_angle = abs(angle)+180
                end_bc = (int(mid_bc_x-extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_bc_y-extend_factor*math.sin(mid_angle*math.pi/180)))
                end_ad = (int(mid_ad_x+extend_factor*math.cos(mid_angle*math.pi/180)), int(mid_ad_y+extend_factor*math.sin(mid_angle*math.pi/180)))

            self.END_AD_POSITIONS.append(end_ad)
            self.END_BC_POSITIONS.append(end_bc)

            # ↓ 計算兩中心線段 X 、 Y 座標  ↓ #
            print("\nFlag = ", flag)
            print("Mid Angle = ", round(mid_angle,2))
            print("Angle = ", angle)
            # i從1開始，但儲存兩個END Points的List之初使存儲位置為 0
            print("i = ", i) 
            # print("END AD = ", END_AD_POSITIONS[i-1]) 
            # print("END BC = ", END_BC_POSITIONS[i-1])
            
            cv2.putText(self.image, str(flag), (cen[0]-10, cen[1]-35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (130, 180, 0), 2)
            cv2.putText(self.image, str(com_angle), (cen[0]-35, cen[1]-15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (130, 180, 0), 2)
            
            # 設定 MSRR 延伸線位置
            cv2.circle(self.image, (end_bc[0], end_bc[1]), 1, (250, 255, 0),10)  
            cv2.circle(self.image, (end_ad[0], end_ad[1]), 1, (250, 255, 0), 10)

            # cv2.putText(image, 'MID_BC', (mid_bc[0]-15, mid_bc[1]-15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            # cv2.putText(image, 'MID_AD', (mid_ad[0]-15, mid_ad[1]-15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # ↓ 繪製線段中點連線 ↓ #
            cv2.line(self.image, mid_ad, mid_bc, (0, 220, 180), 2, lineType=cv2.LINE_8)
            
            # ↓ 繪製延伸線 ↓ #
            cv2.line(self.image, end_ad, end_bc, (255, 255, 0), 2, lineType=cv2.LINE_8)

            # 標註中心點
            cv2.circle(self.image, (cen[0], cen[1]), 1, (0, 0, 255),5 )

            # ↓ 標註線段中點 ↓ #
            cv2.circle(self.image, (mid_bc[0], mid_bc[1]), 1, (250, 255, 0), 3)
            cv2.circle(self.image, (mid_ad[0], mid_ad[1]), 1, (250, 255, 0), 3)
            
            # cv2.circle(image, (int(end_ad[0]), int(end_ad[1])), 1, (250, 255, 0), 10)

            if len(self.END_BC_POSITIONS) < i or len(self.END_AD_POSITIONS) < i :
                continue
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

                        cv2.circle(self.image, (int(intersection_x), int(intersection_y)), 1, (0, 200, 255), 10)
                        cv2.putText(self.image, "CrossPoint", (int(intersection_x)-50, int(intersection_y)-20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    intersection()
cv2.imshow('image', image)
cv2.waitKey(0)
 