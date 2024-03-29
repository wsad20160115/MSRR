import socket
import tkinter as tk
import tkinter.messagebox
import cv2
import threading
import datetime
import time
from PIL import Image, ImageTk
import struct
import numpy as np

import sys
import pickle
import tag_detector # 引用 tag_detector 之函式庫用以檢測與取得AprilTag參數
import tag_intersection # 引用 tag_intersection 用以找出兩 MSRR 之交點 

sys.setrecursionlimit(100000) # 設定最大遞迴次數

#------------- ↓ 建立TCP客戶端 ↓ -------------
HOST = '0.0.0.0'
PORT = 9999
BUFFER_SIZE = 1024

# 設定視窗初始大小
win_width = 1750
win_height = 930

END_AD_POSITIONS = []
END_BC_POSITIONS = []

class App:

    global MIDOFMSRR, ANGLE_OF_MSRR, tagdetect, connect_function, ERROR_OF_ANGLE, stop_flag, option_ID
    global target_x, target_y

    region = False # 標示繪製交會點區塊之Boolean函數
    cal = False

    target_x = 0
    target_y = 0        

    now_date = datetime.date.today()

    # 設定AprilTag檢測器啟用與關閉
    tagintersection = False
    toggle_get_angle = False
    toggle_command_control = False
    put_intersection_point = False

    def __init__(self, master):  

        self.option_ID = 100

        self.tagdetect = False
        self.connect_function = False
        self.stop_flag = False

        self.master = master
        master.title("ACTL MSRR")
        master.iconbitmap('./ACTL72.ico')

        # 設定攝影機編號
        self.cam_id = 0
        
        # 設定攝影機視訊大小
        self.cam_width = 1920*0.7
        self.cam_height = 1080*0.7

        # 設定攝影機
        self.cam = cv2.VideoCapture(self.cam_id)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_width)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_height)

        # 設定畫面顯示區域
        self.video_area = tk.Label(master)
        self.video_area.place(x=450, y=0)

        # 開始更新畫面
        self.update_video()
               
        # 輸入框
        self.input_x_label = tk.Label(master, text="X Posttion:")
        self.input_x_label.place(x=5, y=5)
        self.input_x = tk.Entry(master)
        self.input_x.place(x=5, y=25)

        self.input_y_label = tk.Label(master, text="Y Posttion:")
        self.input_y_label.place(x=175, y=5)
        self.input_y = tk.Entry(master)
        self.input_y.place(x=175, y=25)
        
        # 按鈕設定
        button_width = 12
        button_height = 3

        # ----------- ROW
        # | column

        row1 = 22
        row2 = 182
        row3 = 332
        col1 = 420
        col2 = 490
        col3 = 560
        col4 = 630
        col5 = 700
        col6 = 770
        col7 = 840

        self.submit_button = tk.Button(master, width = 10, height = 2, text="Clear\n Message", command=self.clearBox)
        self.submit_button.place(x=220, y=356)
        self.submit_button = tk.Button(master, width = 10, height = 2, text="Calibration", command=self.calibrate)
        self.submit_button.place(x=320, y=356)
        # ----------------------------------------------------- 主要 Button 區設定 ----------------------------------------------------- #
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Connect", command=lambda: self.send_command("_Connect"))
        self.submit_button.place(x=row1, y=col1)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Forward", command=lambda: self.send_command("_Forward"))
        self.submit_button.place(x=row2, y=col1)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Disconnect", command=lambda: self.send_command("Dconnect"))
        self.submit_button.place(x=row3, y=col1)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Left", command=lambda: self.send_command("____Left"))
        self.submit_button.place(x=row1, y=col2)
        self.submit_button = tk.Button(master, width = button_width, height= button_height, text="Stop", command=lambda: self.send_command("____Stop"))
        self.submit_button.place(x=row2, y=col2)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Right", command=lambda: self.send_command("___Right"))
        self.submit_button.place(x=row3, y=col2)        
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="LiftUP", command=lambda: self.send_command("__LiftUP"))
        self.submit_button.place(x=row1, y=col3)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Backward", command=lambda: self.send_command("Backward"))
        self.submit_button.place(x=row2, y=col3)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="LayDown", command=lambda: self.send_command("_LayDown"))
        self.submit_button.place(x=row3, y=col3)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Snapshot", command=self.snapshot)
        self.submit_button.place(x=row1, y=col4)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Tag \n Detector", command=self.toggle_tag_detector)
        self.submit_button.place(x=row2, y=col4)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Intersection \n Point", command=self.intersection)
        self.submit_button.place(x=row3, y=col4)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Get \n intersection", command = self.get_intersection_point)
        self.submit_button.place(x=row1, y=col5)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Connect\n Function", command=self.connect_fcn)
        self.submit_button.place(x=row2, y=col5)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Get\n Angle", command = self.input_angle)
        self.submit_button.place(x=row3, y=col5)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="LED On", command=lambda: self.send_command("__LED ON"))
        self.submit_button.place(x=row1, y=col6)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="LED OFF", command=lambda: self.send_command("_LED OFF"))
        self.submit_button.place(x=row2, y=col6)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Get All\n ID", command= self.get_id)
        self.submit_button.place(x=row3, y=col6)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Forward \n control", command=lambda: self.command_with_control('_Forward'))
        self.submit_button.place(x=row1, y=col7)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Backward \n control", command=lambda: self.command_with_control('Backward'))
        self.submit_button.place(x=row2, y=col7)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Stop \n control", command=lambda: self.command_with_control('____Stop'))
        self.submit_button.place(x=row3, y=col7)        

        # 使用 "Multi Control" 功能時，選擇要控制哪些 MSRR
        self.ID_0_bool = tk.BooleanVar(value=False)
        self.ID_1_bool = tk.BooleanVar(value=False)
        self.ID_2_bool = tk.BooleanVar(value=False)
        self.ID_3_bool = tk.BooleanVar(value=False)
        self.ID_4_bool = tk.BooleanVar(value=False)
        self.multi = tk.BooleanVar(value=False)

        self.check_button_multi = tk.Checkbutton(master, text='Multi Control', variable=self.multi, onvalue=True, offvalue=False)
        self.check_button_multi.place(x=450, y=830)

        self.check_button_id = tk.Checkbutton(master, text='ID 0', variable=self.ID_0_bool, onvalue=True, offvalue=False)
        self.check_button_id.place(x=450, y=860)
        self.check_button_id = tk.Checkbutton(master, text='ID 1', variable=self.ID_1_bool, onvalue=True, offvalue=False)
        self.check_button_id.place(x=500, y=860)
        self.check_button_id = tk.Checkbutton(master, text='ID 2', variable=self.ID_2_bool, onvalue=True, offvalue=False)
        self.check_button_id.place(x=550, y=860)
        self.check_button_id = tk.Checkbutton(master, text='ID 3', variable=self.ID_3_bool, onvalue=True, offvalue=False)
        self.check_button_id.place(x=600, y=860)
        self.check_button_id = tk.Checkbutton(master, text='ID 4', variable=self.ID_4_bool, onvalue=True, offvalue=False)
        self.check_button_id.place(x=650, y=860)

        self.input_Kp_label = tk.Label(master, text="Kp:")
        self.input_Kp_label.place(x=800, y=830)
        self.input_Kp = tk.Entry(master)
        self.input_Kp.place(x=800, y=860)

        # 訊息框文字
        self.message_label = tk.Label(master, text="Response:", font=('Arial', '14'))
        self.message_label.place(x=18, y=55)
        
        # 訊息框說明
        self.message_response = tk.Text(master, width=58, height=20)        
        self.message_response.place(x=18, y=80)
        
        # 設定訊息框的滾動條
        response_scrollbar = tk.Scrollbar(master)
        response_scrollbar.place(x=430, y=80, height=265)
        self.message_response.config(yscrollcommand=response_scrollbar.set)
        response_scrollbar.config(command=self.message_response.yview)

        # 訊息框日期
        self.date_text = tk.Label(master, text=self.now_date, font=('Arial', '13'))
        self.date_text.place(x=340, y=55)

        # 其他資訊
        self.message_information = tk.Text(master, width=50, height=12)        
        self.message_information.place(x=1340, y=730)

        # 設定訊息框的滾動條
        information_scrollbar = tk.Scrollbar(master)
        information_scrollbar.place(x=1690, y=730, height=160)
        self.message_information.config(yscrollcommand=information_scrollbar.set)
        information_scrollbar.config(command=self.message_information.yview)

        options = [ #設定連結開發板之IP
            "Choose Master MSRR",
            "192.168.50.14, 0", 
            "192.168.50.125, 1",
            "192.168.50.60, 2",
            "192.168.50.122, 3",
            "192.168.50.208, 4",
            "192.168.50.127, 4"                     
        ]
        var = tk.StringVar(master)
        var.set(options[0]) #設定初始控制之開發板 IP 為 192.168.50.55
        self.option_menu = tk.OptionMenu(master, var, *options)
        self.option_menu.place(x=22, y=355)
        self.option_menu.config(width=20,height=2)
        
         # 拉桿設定   
        font = ('Courier New', 12, 'bold')
        self.scale_PWM = tk.Scale(
            label='PWM Pulse Width', font=font, orient=tk.HORIZONTAL, showvalue=True,
            bg='white', fg='gray', tickinterval=10000, length=800, width=10,
            troughcolor='gray', from_ = 0, to = 65535)
        self.scale_PWM.place(x=450, y=730)

        def show(*e):
            global HOST
            MSRR_information = var.get()
            MSRR_information = MSRR_information.split(', ')
            
            HOST = MSRR_information[0]
            self.option_ID = MSRR_information[1] # 選定控制的 MSRR AprilTag ID
            

        var.trace('w',show) # 當Option Menu(選擇控制的開發板IP) 被"改變"，則執行show函數，也就是將 HOST 設定為選單上的 IP
        

    #------------------ ↓ 顯示影像 ↓ ------------------#       
    def update_video(self):

        # 從攝影機捕捉一張畫面
        ret, self.frame = self.cam.read()

        if self.cal == True: #若按下影像校正鈕，則將畫面轉變為影像校正前之結果
            # 讀取影像校正檔案
            with open('calibration_parameter.pkl', 'rb') as calibrate:
                calib_params = pickle.load(calibrate)
            # 設定影像校正參數
            mtx = calib_params['mtx']
            dist = calib_params['dist']
            # rvecs = calib_params['rvecs']
            # tvecs = calib_params['tvecs']
            u = calib_params['u']
            v = calib_params['v']
            
            h1, w1 = self.frame.shape[:2]
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (u, v), 0, (u, v))
            # 校正影像畸變
           
            mapx,mapy=cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtx,(w1,h1),5)
            self.frame=cv2.remap(self.frame,mapx,mapy,cv2.INTER_LINEAR)

        if self.tagdetect:
            tag_detector.tag(self.frame)
            self.MIDOFMSRR = tag_detector.mid_ad
            self.ERROR_OF_ANGLE = tag_detector.error_of_angle # 使用外部tag.py檔案進行比對
            self.tag_id = tag_detector.tag_id
            self.update_angle = tag_detector.get_angle()       
                                 

        if self.put_intersection_point:
            
            cv2.circle(self.frame, (int(tag_intersection.intersection_x), int(tag_intersection.intersection_y)), 1, (0, 0, 255), 4)

        if self.region: 
            cv2.line(self.frame, (350, 80), (900, 80), (255, 50, 0), 2, lineType=cv2.LINE_8)    
            cv2.line(self.frame, (900, 80), (900, 630), (255, 50, 0), 2, lineType=cv2.LINE_8)    
            cv2.line(self.frame, (900, 630), (350, 630), (255, 50, 0), 2, lineType=cv2.LINE_8)    
            cv2.line(self.frame, (350, 630), (350, 80), (255, 50, 0), 2, lineType=cv2.LINE_8)


        # 將OpenCV圖像格式轉換為PIL圖像格式
        image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)      
 
        image = Image.fromarray(image)
                
        # 將PIL圖像格式轉換為Tkinter支援的圖像格式
        photo = ImageTk.PhotoImage(image)

        # 在視窗上顯示圖像
        self.video_area.configure(image=photo)
        self.video_area.image = photo

        # 每 33 毫秒更新一次畫面
        self.master.after(33, self.update_video) 

    def create_messagebox(self, messagebox_text, pop_text):
        tkinter.messagebox.showwarning(title = messagebox_text, # 視窗標題
                                    message = pop_text)
        
    def intersection(self):
        
        tag_intersection.intersection(self.frame)

        # if (tag_intersection.intersection_x < 0 or tag_intersection.intersection_x > 9000) or (tag_intersection.intersection_y > 6000 or tag_intersection.intersection_y < 0) :
        #         messagebox_text = '警告'
        #         pop_text = '畫面中的 AprilTag 交點已超出使用範圍'
        #         self.create_messagebox(messagebox_text, pop_text)
                
        # elif self.put_intersection_point != True:        
        self.message_information.insert(tk.END,'INTERSECTION_X = {:.2f}, INTERSECTION_Y = {:.2f}'.format(tag_intersection.intersection_x, tag_intersection.intersection_y)+ "\n")
        
        self.put_intersection_point = not self.put_intersection_point

    def get_id(self):
        self.list_of_tag_id = tag_detector.get_list_of_tag_id()
        print(self.list_of_tag_id)

    def calibrate(self):
        self.cal = not self.cal

    def test_function(self):
        pass
    
    def move_to_target(self):
        self.target_x = self.input_x.get()
        self.target_y = self.input_y.get()
        self.message_information.insert(tk.END, f'Target X : {self.target_x} Target Y : {self.target_y} \n')
        print(HOST)

    def toggle_tag_detector(self):
        
        self.tagdetect = not self. tagdetect
    
    def clearBox(self): # 清除 Response 訊息框中的所有訊息

        self.message_response.delete("1.0", "end")
        self.message_information.delete("1.0", "end")

    def input_angle(self): # 取得要移動之MSRR原先的AprilTag角度
        
        ANGLE_OF_MSRR = tag_detector.get_angle()
        try:
            self.OAM = ANGLE_OF_MSRR[int(self.option_ID)]  # 讀取要移動之MSRR原先的AprilTag角度 {Original Angle of MSRR}
            print('OAM: ', self.OAM)
        except Exception as exc:
            messagebox_text = 'Warning'
            pop_text = exc
            self.create_messagebox(messagebox_text, pop_text)

        self.message_information.insert(tk.END, f'Angle of MSRR : {ANGLE_OF_MSRR} \n')
        
    def snapshot(self):
        cv2.imwrite("./image/snapshot.jpg", self.frame)

    def send_command(self, command):

        # 將回應顯示在訊息框中
        now = datetime.datetime.now()
        nowhour = str(now.hour)
        nowmin = str(now.minute)
        nowsec = str(now.second)

        if self.multi.get():
            self.multi_control(command)
        else:
    # ----------------------- ↓ Socket 客戶端 ↓ ----------------------- #
            data='連結失敗!'.encode('utf-8')
            # 連接到TCP服務器
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            sock.settimeout(0.2)
            
            uR = self.scale_PWM.get()
            uL = self.scale_PWM.get() 

            # 防止計算出之數值溢位
            if uR > 65535:
                uR = 65535
            elif uR < 0:
                uR = 0
                
            if uL > 65535:
                uL = 65535
            elif uL < 0:
                uL = 0

            pack_data = struct.pack('ii8s', uR, uL, command.encode()) # 將右輪PWM、左輪PWM、移動方式包裝成 "struct" 一次發送給開發板
            print(command)
            while True:
                try:
                    sock.connect((HOST, PORT))
                    
                    # 傳送指令
                    sock.sendall(pack_data)

                    # 接收回應
                    data = sock.recv(BUFFER_SIZE)
                    break
                except socket.timeout:
                    self.message_information.insert(tk.END, f'連線超時，重新連線中... \n')
                    continue
                except ConnectionRefusedError:
                    self.message_information.insert(tk.END, f'連線被拒絕 \n')
                    break
                except Exception as e:
                    self.message_information.insert(tk.END, f'發生錯誤 \n')   
                    break
                finally:
                    sock.close()

            if command == '_Connect':
                self.message_response.insert(tk.END,'['+nowhour+':'+nowmin+':'+nowsec+']'+':'+ '連結' + "\n")

            elif command == 'Dconnect':
                self.message_response.insert(tk.END,'['+nowhour+':'+nowmin+':'+nowsec+']'+':'+ '解除連結' + "\n")

            else:
                
                self.message_response.insert(tk.END,'['+nowhour+':'+nowmin+':'+nowsec+']'+':'+ data.decode() + "\n")
                # 讓訊息框保持在能看到最後一則訊息
                self.message_response.see(tk.END)
                self.message_information.see(tk.END)           

    def command_with_control(self, command):
        print(self.option_ID)
        if int(self.option_ID) >= 0 and int(self.option_ID) <= 10:
            self.stop_flag = not self.stop_flag
        else:
            messagebox_text = 'Warning'
            pop_text = '請選擇欲控制之 MSRR '
            self.create_messagebox(messagebox_text, pop_text)

        def control():
            
            if self.stop_flag == True:

                data='連結失敗!'.encode('utf-8')
                # 連接到TCP服務器
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                uR = self.scale_PWM.get()
                uL = self.scale_PWM.get() 

                Kpo = self.input_Kp.get()
                print("Kpo: ", Kpo)
                self.OEM = self.update_angle[int(self.option_ID)] - self.OAM

                print(f'{self.update_angle[int(self.option_ID)]} - {self.OAM} = {self.OEM}')

                if command == '_Forward':
                    if self.OEM > 0:
                        uR = int(self.scale_PWM.get() + (self.OEM * Kpo))
                        uL = int(self.scale_PWM.get() - (self.OEM * Kpo))

                        if uR < 0:
                            uR = 0

                    elif self.OEM < 0:
                        uR = int(self.scale_PWM.get() + (self.OEM * Kpo))
                        uL = int(self.scale_PWM.get() - (self.OEM * Kpo))

                if command == 'Backward':
                    if self.OEM > 0:
                                uR = int(self.scale_PWM.get() + (self.OEM * Kpo))
                                uL = int(self.scale_PWM.get() - (self.OEM * Kpo))

                                if uR < 0:
                                    uR = 0

                    elif self.OEM < 0:
                        uR = int(self.scale_PWM.get() - (self.OEM * Kpo))
                        uL = int(self.scale_PWM.get() + (self.OEM * Kpo))

                if command == '____Stop':
                    self.stop_flag == False
                    uR = 65535
                    uL = 65535
                    

                # 防止計算出之數值溢位
                if uR > 65535:
                    uR = 65535
                elif uR < 0:
                    uR = 0
                    
                if uL > 65535:
                    uL = 65535
                elif uL < 0:
                    uL = 0
                
                pack_data = struct.pack('ii8s', uR, uL, command.encode()) # 將右輪、左輪、移動方式包裝成 "struct" 一次發送給開發板
                
                try:
                    sock.connect((HOST, PORT))               
                    sock.settimeout(0.3)
                    # 傳送指令
                    sock.sendall(pack_data)

                    # 接收回應
                    data = sock.recv(BUFFER_SIZE)
                except Exception as e:
                    self.message_information.insert(tk.END, f'{e} \n')
                
                sock.close()
                    
                # 將回應顯示在訊息框中
                now = datetime.datetime.now()
                nowhour = str(now.hour)
                nowmin = str(now.minute)
                nowsec = str(now.second)
                self.message_response.insert(tk.END,'['+nowhour+':'+nowmin+':'+nowsec+']'+':'+ data.decode() + "\n")
                # 讓訊息框保持在能看到最後一則訊息
                self.message_response.see(tk.END)
                self.message_information.see(tk.END) 
                time.sleep(0.05)
                if self.stop_flag == True:
                    control()

        def output_error_of_control():

            if self.stop_flag == True:
                try:
                    error_of_control = self.OEM
                    self.message_information.insert(tk.END, f'{str(error_of_control)} \n')
                except Exception as exc:
                    self.message_information.insert(tk.END, f'{exc} \n')

                time.sleep(0.05)
            if self.stop_flag == True:
                output_error_of_control()

        if self.stop_flag == True:
            thread_command_with_control = threading.Thread(target= control)
            thread_command_with_control.start()
            thread_output_error_of_control = threading.Thread(target= output_error_of_control)
            thread_output_error_of_control.start()

    def connect_fcn(self): # 啟動連結之功能
        
        self.OEM = 0 # Orientation Error of MSRR (移動前之角度 - 移動時之角度)
        self.step = 0
        self.position_error = 0
        self.position_error_mm = 0
        
        if HOST != '0.0.0.0':
            try:
                self.data='Connect fail!'.encode('utf-8')

                self.connect_function = not self.connect_function
                
            except ValueError as VE:
                
                self.message_information.insert(tk.END,f'Error : {VE} ' )
        else:
            messagebox_text = '警告'
            pop_text = '請選擇一個模組化自重組機器人'
            self.create_messagebox(messagebox_text, pop_text)

        def reading_error(): # 讀取主動之 MSRR 距離目標 Intersection Point 之位置差

            if self.connect_function == True:
                self.position_error = ((tag_intersection.intersection_x - self.MIDOFMSRR[0])**2 + (tag_intersection.intersection_y-self.MIDOFMSRR[1])**2)**0.5
                self.position_error_mm = self.position_error * 0.715 # 將位置誤差單位由 pixel 轉成 mm

                send_connect_command()
        	
        def send_connect_command(): # 將讀取之位置差之控制參數傳送給主動之 MSRR
            if self.connect_function == True:
                command = '__Fail__'
                inter_x = tag_intersection.intersection_x # 交會點 x 座標
                inter_y = tag_intersection.intersection_y # 交會點 y 座標

                step_bool = False                
                
                match self.step:
                    
                    case 0: # 若目前是尚未執行連結功能的狀態，則執行連結步驟 "1"
                        
                        if self.position_error_mm <= 1:
                            self.step = 1

                        # 交點在第一象限
                        if inter_x > self.MIDOFMSRR[0] and inter_y < self.MIDOFMSRR[1] and (180 < self.OAM < 270):
                            command = '_Forward'
                            print('狀況 1')
                        elif inter_x > self.MIDOFMSRR[0] and inter_y < self.MIDOFMSRR[1] and (0 < self.OAM < 90):
                            command = 'Backward'
                            print('狀況 2')

                        # 交點在第二象限
                        elif inter_x < self.MIDOFMSRR[0] and inter_y < self.MIDOFMSRR[1] and (270 < self.OAM < 360):
                            command = '_Forward'
                            print('狀況 3')
                        elif inter_x < self.MIDOFMSRR[0] and inter_y < self.MIDOFMSRR[1] and (90 < self.OAM < 180):
                            command ='Backward'
                            print('狀況 4')
                        
                        # 交點在第三象限     
                        elif inter_x < self.MIDOFMSRR[0] and inter_y > self.MIDOFMSRR[1] and (0 < self.OAM < 90):
                            command = '_Forward'
                            print('狀況 5')
                        elif inter_x < self.MIDOFMSRR[0] and inter_y > self.MIDOFMSRR[1] and (180 < self.OAM < 270):
                            command = 'Backward'
                            print('狀況 6')

                        # 交點在第四象限
                        elif inter_x > self.MIDOFMSRR[0] and inter_y > self.MIDOFMSRR[1] and (90 < self.OAM < 180):
                            command = '_Forward'
                            print('狀況 7')
                        elif inter_x > self.MIDOFMSRR[0] and inter_y > self.MIDOFMSRR[1] and (270 < self.OAM < 360):
                            command = 'Backward'
                            print('狀況 8')                            
                        
                        else:
                            if inter_x > self.MIDOFMSRR[0]:
                                print('X > M')
                            elif inter_x < self.MIDOFMSRR[0]:
                                print('X < M')

                            if inter_y > self.MIDOFMSRR[1]:
                                print('Y > M')
                            elif inter_y < self.MIDOFMSRR[1]:
                                print('Y < M')
                            
                            print('OAM = ', self.OAM)
                            print('例外狀況，請排除障礙')                        
                            
                    case 1: # 若已完成連結步驟 "1"，則執行步驟 "2"
                        print('Case 1')
                        if self.ERROR_OF_ANGLE <= 3:
                            step_bool = True
                            self.step = 2

                        if step_bool == False:
                            if self.ERROR_OF_ANGLE > 0:
                                command = '___Right'
                            elif self.ERROR_OF_ANGLE < 0:
                                command = '____Left'
                            
                    case 2: # 若已完成連結步驟 "2"，則執行步驟 "3"
                        print('Case 2')
                        self.step = 3     

                    case 3: # 若已完成連結步驟 "3"，則執行步驟 "4"
                        print('Case 3')
                        command = '_Connect'
                        uR = 65535    
                        uL = 65535

                    case 4: # 連結完成，跳出視窗提醒已完成
                        message_response = 'Hint'       
                        pop_text = 'Assemble finished'
                        self.step = 5
                        self.create_messagebox(message_response, pop_text)

                Kpo = 30 # 控制方向之 P-Control 參數 Kp_orientation

                Kp = 0.046 # P-Control 數值
      
                self.OEM = self.update_angle[0] - self.OAM
                
                u = 3000/(Kp * self.position_error)

                uR = 65535 # 右輪控制參數
                uL = 65535 # 左輪控制參數

                if command == '_Forward': # 設定移動模式若為"前進"之左右輪控制器
                    if self.OEM > 0:
                        uR = int(u + (self.OEM * Kpo))
                        uL = int(u - (self.OEM * Kpo))

                        if uR < 0:
                            uR = 0

                    elif self.OEM < 0:
                        uR = int(u + (self.OEM * Kpo))
                        uL = int(u - (self.OEM * Kpo))

                        if uL < 0:
                            uL = 0

                elif command == 'Backward': # 設定移動模式若為"後退"之左右輪控制器
                    if self.OEM > 0:
                        uR = int(u + (self.OEM * Kpo))
                        uL = int(u - (self.OEM * Kpo))

                        if uR < 0:
                            uR = 0

                    elif self.OEM < 0:
                        uR = int(u - (self.OEM * Kpo))
                        uL = int(u + (self.OEM * Kpo))

                        if uL < 0:
                            uL = 0

                if self.OEM == 0:
                    uR = int(u)
                    uL = int(u)               

                # 限制左輪與右輪輸出範圍
                if uR > 35000: 
                    uR = 65535
                elif uR < 0:
                    uR = 0

                if uL > 35000:
                    uL = 65535 
                elif uL < 0:
                    uL = 0

# ----------------------------------------------------------- 發送移動命令與控制訊號 ----------------------------------------------------------- #
                data='連結失敗!'.encode('utf-8')
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 連接到TCP服務器

                pack_data = struct.pack('ii8s', uR, uL, command.encode())
                while True:
                    try:                    
                        sock.connect((HOST, PORT))
                        sock.settimeout(0.01)
                        # 傳送指令
                        sock.sendall(pack_data)

                        # 接收回應
                        data = sock.recv(BUFFER_SIZE)
                    except sock.timeout:
                        self.message_information.insert(tk.END, f'連線超時，重新連線中... \n')
                        continue
                    except ConnectionRefusedError:
                        self.message_information.insert(tk.END, f'連線被拒絕 \n')
                        break
                    except Exception as e:
                        self.message_information.insert(tk.END, f'發生錯誤 \n')
                        break
                    finally:
                        sock.close()   
                

                # 將回應顯示在訊息框中
                now = datetime.datetime.now()
                nowhour = str(now.hour)
                nowmin = str(now.minute)
                nowsec = str(now.second)
                self.message_response.insert(tk.END,'['+nowhour+':'+nowmin+':'+nowsec+']'+':'+ data.decode() + "\n")
                self.message_response.see(tk.END)
                self.message_information.see(tk.END)
                #thread_reading_error.join() # 等待

                reading_error()

        # ---------------------------- 執行緒之設定與啟動 ---------------------------- #
        thread_reading_error = threading.Thread(target = reading_error) #設定 reading_error 為 Thread
        thread_send_connect_command = threading.Thread(target = send_connect_command) #設定 send_connect_command 為 Thread

        thread_reading_error.start() # 啟動 reading_error 之 Thread
        thread_send_connect_command.start() # 啟動 send_connect_command 之 Thread
    
    def multi_control(self, command):
        control_ip = [] # 設定
        
        if self.ID_0_bool.get():
            control_ip.append('192.168.50.14')
            
        if self.ID_1_bool.get():
            control_ip.append('192.168.50.125')

        if self.ID_2_bool.get():
            control_ip.append('192.168.50.60')
        
        if self.ID_3_bool.get():
            control_ip.append('192.168.50.122')

        if self.ID_4_bool.get():
            control_ip.append('192.168.50.208')


        for HOST in control_ip:
            data='連結失敗!'.encode('utf-8')
            print(control_ip)
            print(HOST)
            # 連接到TCP服務器
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)            
            sock.settimeout(0.3)

            uR = self.scale_PWM.get()
            uL = self.scale_PWM.get() 

            # 防止計算出之數值溢位
            if uR > 65535:
                uR = 65535
            elif uR < 0:
                uR = 0
                
            if uL > 65535:
                uL = 65535
            elif uL < 0:
                uL = 0
            
            pack_data = struct.pack('ii8s', uR, uL, command.encode()) # 將右輪PWM、左輪PWM、移動方式包裝成 "struct" 一次發送給開發板
            
            try:
                sock.connect((HOST, PORT))
                
                # 傳送指令
                sock.sendall(pack_data)

                # 接收回應
                data = sock.recv(BUFFER_SIZE)
                
            except socket.timeout:
                self.message_information.insert(tk.END, f'連線超時，重新連線中... \n')
                
            except ConnectionRefusedError:
                self.message_information.insert(tk.END, f'連線被拒絕 \n')
                
            except Exception as e:
                self.message_information.insert(tk.END, f'發生錯誤 \n')
                
            finally:
                sock.close()
        
        # 將回應顯示在訊息框中
        now = datetime.datetime.now()
        nowhour = str(now.hour)
        nowmin = str(now.minute)
        nowsec = str(now.second)
        self.message_response.insert(tk.END,'['+nowhour+':'+nowmin+':'+nowsec+']'+':'+ data.decode() + "\n")
        # 讓訊息框保持在能看到最後一則訊息
        self.message_response.see(tk.END)
        self.message_information.see(tk.END)                   

        thread_multi_control = threading.Thread(target = self.multi_control)
        thread_multi_control.start()

    def get_intersection_point(self):
        import get_intersection
        get_intersection.tag_with_intersection()
# 建立主視窗
root = tk.Tk()
#設定程式啟動時的視窗大小
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width - win_width) / 2) 
y = int((screen_height - win_height) / 2)
root.geometry(f"{win_width}x{win_height}+{x}+{y-30}") #設定視窗初始位置

app = App(root)
#root.configure(bg='gray')
root.mainloop()