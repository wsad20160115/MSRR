import socket
import tkinter as tk
import tkinter.messagebox
import cv2
import threading
import datetime
import time
from PIL import Image, ImageTk
import struct
import tag_detector # 引用 tag_detector 之函式庫用以檢測與取得AprilTag參數
import tag_intersection # 引用 tag_intersection 用以找出兩 MSRR 之交點 
import sys

sys.setrecursionlimit(100000)

#------------- ↓ 建立TCP客戶端 ↓ -------------
HOST = '0.0.0.0'
PORT = 9999
BUFFER_SIZE = 1024

# 設定視窗初始大小
win_width = 1750
win_height = 850

END_AD_POSITIONS = []
END_BC_POSITIONS = []

class App:

    global classTag, MIDOFMSRR, ANGLEOFMSRR, tagdetect, connect_function, ERROR_OF_ANGLE
    # MIDOFMSRR = (0.0, 0.0)
    # ANGLEOFMSRR = 0.0
    classTag = tag_detector.Tag()

    now_date = datetime.date.today()

    # 設定AprilTag檢測器啟用與關閉
    
    tagintersection = False
    putintersection = False

    def __init__(self, master):

        self.tagdetect = False
        self.connect_function = False
        
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
        self.input_label = tk.Label(master, text="Command:")
        self.input_label.grid(row=0, column=0)
        self.input_entry = tk.Entry(master)
        self.input_entry.grid(row=0, column=1)
        
        # 按鈕設定
        button_width = 12
        button_height = 3

        # ----------- ROW
        # | column

        row1 = 22
        row2 = 182
        row3 = 332
        col1 = 400
        col2 = 470
        col3 = 540
        col4 = 610
        col5 = 680 

        self.submit_button = tk.Button(master, width = button_width, height = 2, text="Clear Message", command=self.clearBox)
        self.submit_button.place(x=250, y=335)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="LED On", command=lambda: self.send_command("__LED ON"))
        self.submit_button.place(x=row1, y=750)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="LED OFF", command=lambda: self.send_command("_LED OFF"))
        self.submit_button.place(x=row2, y=750)
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
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Put\n Intersection", command = self.put_intersection)
        self.submit_button.place(x=row1, y=col5)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Connect\n Function", command=self.connect_fcn)
        self.submit_button.place(x=row2, y=col5)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Shutdown", command =lambda: self.send_command("Shundown"))
        self.submit_button.place(x=row3, y=col5)

        # 創建 Scrollbar 控件
        scrollbar = tk.Scrollbar(root)
        
        # 訊息框
        self.message_label = tk.Label(master, text="Response:", font=('Arial', '14'))
        self.message_label.place(x=18, y=35)
        self.message_text = tk.Text(master, width=58, height=20)        
        self.message_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config()
        self.message_text.place(x=18, y=60)

        self.date_text = tk.Label(master, text=self.now_date, font=('Arial', '13'))
        self.date_text.place(x=340, y=35)

        options = [ #設定連結開發板之IP
            "Choose Master MSRR",
            "192.168.50.14",
            "192.168.50.55",
            "192.168.50.60",
            "192.168.50.142",
            "192.168.50.156", 
            "192.168.50.176",
            "192.168.50.208",           
            "192.168.50.220",
            "192.168.50.234",       
            "192.168.50.239",
            "192.168.0.101"
        ]
        var = tk.StringVar(master)
        var.set(options[0])
        self.option_menu = tk.OptionMenu(master, var, *options)
        self.option_menu.place(x=22, y=335)
        self.option_menu.config(width=20,height=2)
        
         # 拉桿設定
        font = ('Courier New', 16, 'bold')
        self.scale = tk.Scale(
            label='PWM Pulse Width', font=font, orient=tk.HORIZONTAL, showvalue=True,
            bg='white', fg='gray', tickinterval=10000, length=1280, width=20,
            troughcolor='gray', from_ = 0, to = 65535)
        self.scale.place(x=450, y=730)

        def show(*e):
            global HOST
            HOST = var.get()
            print(HOST)
        var.trace('w',show)

    def create_messagebox(self, messagebox_text, pop_text):
        tkinter.messagebox.showwarning(title = messagebox_text, # 視窗標題
                                    message = pop_text)
    
    def test_function(self):
        pass

    def toggle_tag_detector(self):
        
        self. tagdetect = not self. tagdetect

    def put_intersection(self):
        self.putintersection = not self.putintersection

    # -------------- ↓ 計算 MSRR 延伸線之交點 ↓ -------------- #
    def intersection(self):
        tag_intersection.intersection(self)

        if (tag_intersection.intersection_x < 350 or tag_intersection.intersection_x > 900) or (tag_intersection.intersection_y > 600 or tag_intersection.intersection_y < 80) :
           messagebox_text = 'Warning'
           pop_text = 'Intersection Point is out of range ！ '
           self.create_messagebox(messagebox_text, pop_text)
        else:
            self.putintersection = not self.putintersection

        print('INTERSECTION_X = {:.2f}, INTERSECTION_Y = {:.2f}'.format(tag_intersection.intersection_x, tag_intersection.intersection_y))

    def clearBox(self): # 清除 Response 訊息框中的所有訊息
        self.message_text.delete("1.0", "end")
    
    #------------------ ↓ 顯示影像 ↓ ------------------#       
    def update_video(self):
        # 從攝影機捕捉一張畫面
        ret, frame = self.cam.read()
    
        if self.tagdetect:
            self.MIDOFMSRR, self.ANGLEOFMSRR, self.ERROR_OF_ANGLE = classTag.tag(frame) # 使用外部tag.py檔案進行比對

        if self.putintersection:
           cv2.circle(frame, (int(tag_intersection.intersection_x), int(tag_intersection.intersection_y)), 1, (0, 0, 255), 4)

        # 將OpenCV圖像格式轉換為PIL圖像格式
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)      
 
        image = Image.fromarray(image)
                
        # 將PIL圖像格式轉換為Tkinter支援的圖像格式
        photo = ImageTk.PhotoImage(image)

        # 在視窗上顯示圖像
        self.video_area.configure(image=photo)
        self.video_area.image = photo

        # 每 33 毫秒更新一次畫面
        self.master.after(33, self.update_video) 
        
        # -------------- ↓ Apriltag 檢測器 ↓ -------------- # 

    def snapshot(self):

        ret, frame = self.cam.read()

        if ret:
            cv2.imwrite("./image/snapshot.jpg", frame)

    def send_command(self,command):
# ----------------------- ↓ Socket 客戶端 ↓ ----------------------- #
        data='Connect fail!'.encode('utf-8')
        # 連接到TCP服務器
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
        uR = self.scale.get()
        uL = self.scale.get()-100
        
        if uR > 65535:
            uR = 65535
        elif uR < 0:
            uR = 0
            
        if uL > 65535:
            uL = 65535
        elif uL < 0:
            uL = 0
        movecommand = command
        pack_data = struct.pack('ii8s', uR, uL, movecommand.encode())
        
        try:
            sock.connect((HOST, PORT))

            # 傳送指令
            sock.sendall(pack_data)

            # 接收回應
            data = sock.recv(BUFFER_SIZE)
        except Exception as e:
            print('Exception', e)
        finally:
            sock.close()
            
        # 將回應顯示在訊息框中
        now = datetime.datetime.now()
        nowhour = str(now.hour)
        nowmin = str(now.minute)
        nowsec = str(now.second)
        self.message_text.insert(tk.END,'['+nowhour+':'+nowmin+':'+nowsec+']'+':'+ data.decode() + "\n")
        

    def connect_fcn(self): # 啟動連結之功能
        self.data='Connect fail!'.encode('utf-8')
        global position_error, step
        self.step = 0
        self.connect_function = not self.connect_function

        def reading_error(): # 讀取主動之 MSRR 距離目標 Intersection Point 之位置差

            if self.connect_function == True:
                self.position_error = ((tag_intersection.intersection_x - self.MIDOFMSRR[0])**2 + (tag_intersection.intersection_y-self.MIDOFMSRR[1])**2)**0.5
                print('Reading Error．．．')
                
            
                send_connect_command()
        	
        def send_connect_command(): # 將讀取之位置差之控制參數傳送給主動之 MSRR
            if self.connect_function == True:

                inter_x = tag_intersection.intersection_x # 交會點 x 座標
                inter_y = tag_intersection.intersection_y # 交會點 y 座標

                command = '__Fail__' # 移動之命令
                
                OEM = 0 # Orientation Error of MSRR (移動前之角度 - 移動時之角度)
                Kpo = 5 # 控制方向之 P-Control 參數 Kp_orientation

                u = 3000/(kp * self.position_error)
                uR = 65535 # 右輪控制參數
                uL = 65535 # 左輪控制參數
                kp = 3 # P-Control 數值

                uR = u - (OEM * Kpo)
                uL = u - (OEM * Kpo)

                # 避免控制訊號大於65535後產生溢位導致 MSRR 不停止
                if control_signal > 65535: 
                    control_signal = 65535 
                
                match step:
                    case 0: # 若目前是尚未執行連結功能的狀態，則執行連結步驟 "1"
                        if inter_x > self.MIDOFMSRR[0] and inter_y > self.MIDOFMSRR[1] and (270 < self.ANGLEOFMSRR[0] < 360):
                            command = '_Forward'
                        elif inter_x > self.MIDOFMSRR[0] and inter_y > self.MIDOFMSRR[1] and (90 < self.ANGLEOFMSRR[0] < 180):
                            command = 'Backward'
                        elif inter_x < self.MIDOFMSRR[0] and inter_y > self.MIDOFMSRR[1] and (180 < self.ANGLEOFMSRR[0] < 270):
                            command = '_Forward'
                        elif inter_x < self.MIDOFMSRR[0] and inter_y > self.MIDOFMSRR[1] and (0 < self.ANGLEOFMSRR[0] < 90):
                            command = 'Backward'
                        elif inter_x < self.MIDOFMSRR[0] and inter_y < self.MIDOFMSRR[1] and (90 < self.ANGLEOFMSRR[0] < 180):
                            command ='_Forward'
                        elif inter_x < self.MIDOFMSRR[0] and inter_y < self.MIDOFMSRR[1] and (270 < self.ANGLEOFMSRR[0] < 360):
                            command = 'Backward'
                        elif inter_x > self.MIDOFMSRR[0] and inter_y < self.MIDOFMSRR[1] and (0 < self.ANGLEOFMSRR[0] < 90):
                            command = '_Forward'
                        elif inter_x > self.MIDOFMSRR[0] and inter_y < self.MIDOFMSRR[1] and (180 < self.ANGLEOFMSRR[0] < 270):
                            command = 'Backward'

                    case 1: # 若已完成連結步驟 "1"，則執行步驟 "2"
                        if self.ERROR_OF_ANGLE <= 3:
                            step_bool = True
                            step = 2

                        if step_bool == False:
                            if self.ERROR_OF_ANGLE > 0:
                                command = '___Right'
                            elif self.ERROR_OF_ANGLE < 0:
                                command = '____Left'
                            
                    case 2: # 若已完成連結步驟 "2"，則執行步驟 "3"
                    
                        step = 3     

                    case 3: # 若已完成連結步驟 "3"，則執行步驟 "4"
                        command = '_Connect'
                        control_signal = 65535    

                    case 4: # 連結完成，跳出視窗提醒已完成
                        message_text = 'Hint'       
                        pop_text = 'Assemble finished'
                        self.create_messagebox(message_text, pop_text)

# ----------------------------------------------------------- 發送移動命令與控制訊號 ----------------------------------------------------------- #
                data='Connect fail!'.encode('utf-8')
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 連接到TCP服務器

                pack_data = struct.pack('ii8s', uR, uL, command.encode())
                
                try:
                    sock.settimeout(0.3)
                    sock.connect((HOST, PORT))

                    # 傳送指令
                    sock.sendall(pack_data)

                    # 接收回應
                    data = sock.recv(BUFFER_SIZE)
                except Exception as e:
                    print('Exception', e)
                

                # 將回應顯示在訊息框中
                now = datetime.datetime.now()
                nowhour = str(now.hour)
                nowmin = str(now.minute)
                nowsec = str(now.second)
                self.message_text.insert(tk.END,'['+nowhour+':'+nowmin+':'+nowsec+']'+':'+ data.decode() + "\n")

                thread_reading_error.join() # 等待

                reading_error()

        # ---------------------------- 執行緒之設定與啟動 ---------------------------- #
        thread_reading_error = threading.Thread(target = reading_error) #設定 reading_error 為 Thread
        thread_send_connect_command = threading.Thread(target = send_connect_command) #設定 send_connect_command 為 Thread

        thread_reading_error.start() # 啟動 reading_error 之 Thread
        thread_send_connect_command.start() # 啟動 send_connect_command 之 Thread

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