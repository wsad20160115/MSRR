import socket
import tkinter as tk
import cv2
import datetime
from PIL import Image, ImageTk
import math

#--------------------------------------- ↓ 設定在D槽中import AprilTag 函式庫 ↓ ---------------------------------------#
import sys

sys.path.append("D:\\")

import pupil_apriltags as apriltag

# import tag

#------------- ↓ 建立TCP客戶端 ↓ -------------
HOST = '0.0.0.0'
PORT = 9999
BUFFER_SIZE = 1024

# 設定視窗初始大小
win_width = 1300
win_height = 750

i = 0
j = 0
k = 1
END_AD_POSITIONS = []
END_BC_POSITIONS = []

class App:

    # 設定AprilTag檢測器啟用與關閉
    tagcontrol = False

    # 創建一個apriltag，接著檢測AprilTags
    options = apriltag.Detector(families='tag36h11')

    def __init__(self, master):
        self.master = master
        master.title("ACTL MSRR")
        master.iconbitmap('./ACTL72.ico')

        # 設定攝影機編號
        self.cam_id = 0
        
        # 設定攝影機視訊大小
        self.cam_width = 1920*0.5
        self.cam_height = 1080*0.5

        # 設定攝影機
        self.cam = cv2.VideoCapture(self.cam_id)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_width)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_height)

        # 設定畫面顯示區域
        self.video_area = tk.Label(master)
        self.video_area.place(x=270, y=0)

        # 開始更新畫面
        self.update_video()
               
        # 輸入框
        self.input_label = tk.Label(master, text="Command:")
        self.input_label.grid(row=0, column=0)
        self.input_entry = tk.Entry(master)
        self.input_entry.grid(row=0, column=1)

        # 按鈕
        self.submit_button = tk.Button(master, text="Clear Message", command=self.clearBox)
        self.submit_button.place(x=80, y=40)
        self.submit_button = tk.Button(master, text="Test", command=lambda: self.send_command("Test"))
        self.submit_button.place(x=10, y=40)
        self.submit_button = tk.Button(master, width=7, height=3, text="連結", command=lambda: self.send_command("連結"))
        self.submit_button.place(x=20, y=380)
        self.submit_button = tk.Button(master, width=7, height=3, text="前進", command=lambda: self.send_command("前進"))
        self.submit_button.place(x=100, y=380)
        self.submit_button = tk.Button(master, width=7, height=3, text="斷開", command=lambda: self.send_command("斷開"))
        self.submit_button.place(x=180, y=380)
        self.submit_button = tk.Button(master, width=7, height=3, text="左轉", command=lambda: self.send_command("左轉"))
        self.submit_button.place(x=20, y=450)
        self.submit_button = tk.Button(master, width=7, height=3, text="停止", command=lambda: self.send_command("停止"))
        self.submit_button.place(x=100, y=450)
        self.submit_button = tk.Button(master, width=7, height=3, text="右轉", command=lambda: self.send_command("右轉"))
        self.submit_button.place(x=180, y=450)        
        self.submit_button = tk.Button(master, width=7, height=3, text="抬升", command=lambda: self.send_command("抬升"))
        self.submit_button.place(x=20, y=520)
        self.submit_button = tk.Button(master, width=7, height=3, text="後退", command=lambda: self.send_command("後退"))
        self.submit_button.place(x=100, y=520)
        self.submit_button = tk.Button(master, width=7, height=3, text="下降", command=lambda: self.send_command("下降"))
        self.submit_button.place(x=180, y=520)
        self.submit_button = tk.Button(master, width=7, height=3, text="擷取", command=self.snapshot)
        self.submit_button.place(x=20, y=590)
        self.submit_button = tk.Button(master, width=7, height=3, text="AprilTag", command=self.toggle)
        self.submit_button.place(x=100, y=590)
        self.submit_button = tk.Button(master, width=7, height=3, text="計算", command=self.calculate)
        self.submit_button.place(x=180, y=590)
        self.submit_button = tk.Button(master, width=7, height=3, text="HI", command=self.calculate)
        self.submit_button.place(x=180, y=660)
        
        # 創建 Scrollbar 控件
        scrollbar = tk.Scrollbar(root)
        
        # 訊息框
        self.message_label = tk.Label(master, text="Response:", font=('Arial', '14'))
        self.message_label.place(x=10, y=80)
        self.message_text = tk.Text(master, width=35, height=12)        
        self.message_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config()
        self.message_text.place(x=10, y=110)
        
        options1 = [ #設定連結開發板之IP
            "Choose First MSRR",
            "192.168.50.14",
            "192.168.50.55",
            "192.168.50.60",
            "192.168.50.142",
            "192.168.50.156", 
            "192.168.50.176",
            "192.168.50.208",           
            "192.168.50.220",
            "192.168.50.234",       
            "192.168.50.239"
        ]

        options2 = [ #設定被連結開發板之IP
            "Choose Second MSRR",
            "192.168.50.14",
            "192.168.50.55",
            "192.168.50.60",
            "192.168.50.142",
            "192.168.50.156", 
            "192.168.50.176",
            "192.168.50.208",           
            "192.168.50.220",
            "192.168.50.234",       
            "192.168.50.239"
        ]
        
        var = tk.StringVar(master)
        var.set(options1[0])
        self.option_menu = tk.OptionMenu(master, var, *options1)
        self.option_menu.place(x=40, y=280)
        self.option_menu.config(width=20,height=1)

        var = tk.StringVar(master)
        var.set(options2[0])
        self.option_menu = tk.OptionMenu(master, var, *options2)
        self.option_menu.place(x=40, y=325)
        self.option_menu.config(width=20,height=1)
        
        def show(*e):
            global HOST
            HOST = var.get()
            print(HOST)
        var.trace('w',show)

    def toggle(self):
        
        self.tagcontrol = not self.tagcontrol    

    def clearBox(self):
        self.message_text.delete("1.0", "end")

    #------------------ ↓ 顯示影像 ↓ ------------------#       
    def update_video(self):
        # 從攝影機捕捉一張畫面
        ret, frame = self.cam.read()

        # print("type = ", type(frame))
        try:
            if self.tagcontrol:
                # tag.tag(self, frame) 使用外部tag.py檔案進行比對
                self.tag(frame)
        except BaseException as e:
            print(e)

        # 將OpenCV圖像格式轉換為PIL圖像格式
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)      
        # image = cv2.flip(image, 1) #將攝影機畫面左右翻轉  
        image = Image.fromarray(image)
                
        # 將PIL圖像格式轉換為Tkinter支援的圖像格式
        photo = ImageTk.PhotoImage(image)

        # 在視窗上顯示圖像
        self.video_area.configure(image=photo)
        self.video_area.image = photo

        # 每 33 毫秒更新一次畫面
        self.master.after(33, self.update_video) 
    
        # -------------- ↓ Apriltag 檢測器 ↓ -------------- # 
    def tag(self, image):

        # print("type = ", type(image))
        # 將彩色影像轉換為灰度影像
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        results = self.options.detect(gray)

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
        return image
        # cv2.imshow('AprilTag', image)

    def snapshot(self):
        ret, frame = self.cam.read()
        frame_flip = cv2.flip(frame, 1)
        if ret:
            cv2.imwrite("./image/snapshot.jpg", frame_flip)
    
    # -------------- ↓ 計算MSRR姿態 ↓ -------------- #
    def calculate(self):
        pass

    def send_command(self,value):
        # 取得使用者輸入的指令
        #command = self.input_entry.get()
        command = value
           
# ----------------------- ↓ Socket 客戶端 ↓ ----------------------- #
        data='Connect fail!'.encode('utf-8')
        # 連接到TCP服務器
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                print(HOST)
                sock.settimeout(0.2)
                sock.connect((HOST, PORT))

                # 傳送指令
                sock.sendall(command.encode())

                # 接收回應
                data = sock.recv(BUFFER_SIZE)
            except Exception as e:
                print(e)
        # 將回應顯示在訊息框中
        now = datetime.datetime.now()
        nowhour = str(now.hour)
        nowmin = str(now.minute)
        nowsec = str(now.second)
        self.message_text.insert(tk.END,'['+nowhour+':'+nowmin+':'+nowsec+']'+':'+ data.decode() + "\n")

        

# 建立主視窗
root = tk.Tk()
#設定程式啟動時的視窗大小
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width - win_width) / 2) 
y = int((screen_height - win_height) / 2)
root.geometry(f"{win_width}x{win_height}+{x}+{y}") #設定視窗初始位置

app = App(root)
root.mainloop()

