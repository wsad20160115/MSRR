import cv2
import numpy as np

# 定義兩條直線的起點和終點座標 
line1_start = (100, 100)
line1_end = (400, 400)

line2_start = (100, 400)
line2_end = (400, 100)

# 繪製兩條直線
img = np.zeros((512, 512, 3), np.uint8)
cv2.line(img, line1_start, line1_end, (0, 0, 255), 3)
cv2.line(img, line2_start, line2_end, (0, 255, 0), 3)

# 計算兩條直線的交點
x1, y1 = line1_start
x2, y2 = line1_end
x3, y3 = line2_start
x4, y4 = line2_end
denom = (y4-y3)*(x2-x1)-(x4-x3)*(y2-y1)
if denom != 0:
    ua = ((x4-x3)*(y1-y3)-(y4-y3)*(x1-x3))/denom
    ub = ((x2-x1)*(y1-y3)-(y2-y1)*(x1-x3))/denom
    intersection_x = x1 + ua*(x2-x1)
    intersection_y = y1 + ua*(y2-y1)
    print(f"Intersection point: ({intersection_x:.2f}, {intersection_y:.2f})")
else:
    print("Lines are parallel")

cv2.circle(img, (int(intersection_x), int(intersection_y)), 1, (0, 255, 255), 10)

# 顯示圖片
cv2.imshow("Image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
