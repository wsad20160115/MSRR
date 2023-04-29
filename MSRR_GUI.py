import socket
import tkinter as tk
import cv2
import threading
import datetime
from PIL import Image, ImageTk
import struct
import tag_detector # 引用 tag_detector 之函式庫用以檢測與取得AprilTag參數
import tag_intersection # 引用 tag_intersection 用以找出兩 MSRR 之交點 
import test
import globals
#------------- ↓ 建立TCP客戶端 ↓ -------------
HOST = '0.0.0.0'
PORT = 9999
BUFFER_SIZE = 1024

# 設定視窗初始大小
win_width = 1600
win_height = 900

END_AD_POSITIONS = []
END_BC_POSITIONS = []

class App:

    # 設定AprilTag檢測器啟用與關閉
    tagcontrol = False
    tagintersection = False
    putintersection = False

    def __init__(self, master):
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
        self.video_area.place(x=300, y=0)

        # 開始更新畫面
        self.update_video()
               
        # 輸入框
        self.input_label = tk.Label(master, text="Command:")
        self.input_label.grid(row=0, column=0)
        self.input_entry = tk.Entry(master)
        self.input_entry.grid(row=0, column=1)
        
        # 按鈕設定
        button_width = 9
        button_height = 3

        self.submit_button = tk.Button(master, text="Clear Message", command=self.clearBox)
        self.submit_button.place(x=180, y=40)
        self.submit_button = tk.Button(master, text="LED On", command=lambda: self.send_command("LED ON"))
        self.submit_button.place(x=10, y=40)
        self.submit_button = tk.Button(master, text="LED OFF", command=lambda: self.send_command("LED OFF"))
        self.submit_button.place(x=80, y=40)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Connect", command=lambda: self.send_command("Connect"))
        self.submit_button.place(x=20, y=380)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Forward", command=lambda: self.send_command("Forward"))
        self.submit_button.place(x=100, y=380)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Disconnect", command=lambda: self.send_command("Disconnect"))
        self.submit_button.place(x=180, y=380)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Left", command=lambda: self.send_command("Left"))
        self.submit_button.place(x=20, y=450)
        self.submit_button = tk.Button(master, width = button_width, height= button_height, text="Stop", command=lambda: self.send_command("Stop"))
        self.submit_button.place(x=100, y=450)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Right", command=lambda: self.send_command("Right"))
        self.submit_button.place(x=180, y=450)        
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="LiftUP", command=lambda: self.send_command("LiftUP"))
        self.submit_button.place(x=20, y=520)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Backward", command=lambda: self.send_command("Backward"))
        self.submit_button.place(x=100, y=520)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="LayDown", command=lambda: self.send_command("LayDown"))
        self.submit_button.place(x=180, y=520)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Snapshot", command=self.snapshot)
        self.submit_button.place(x=20, y=590)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Tag \n Detector", command=self.toggle_tag_detector)
        self.submit_button.place(x=100, y=590)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Intersection \n Point", command=self.intersection)
        self.submit_button.place(x=180, y=590)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Put\n Intersection", command = self.put_intersection)
        self.submit_button.place(x=20, y=660)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="HI_test", command=self.test_function)
        self.submit_button.place(x=100, y=660)
        self.submit_button = tk.Button(master, width = button_width, height = button_height, text="Shutdown", command=lambda: self.send_command("Shutdown"))
        self.submit_button.place(x=180, y=660)

        # 拉桿設定
        font = ('Courier New', 20, 'bold')
        self.scale = tk.Scale(
            label='PWM Pulse Width', font=font, orient=tk.HORIZONTAL, showvalue=True,
            bg='white', fg='blue', tickinterval=10000, length=1000, width=30,
            troughcolor='blue', from_ = 0, to = 65535)
        self.scale.place(x=0, y=750)
        
        # 創建 Scrollbar 控件
        scrollbar = tk.Scrollbar(root)
        
        # 訊息框
        self.message_label = tk.Label(master, text="Response:", font=('Arial', '14'))
        self.message_label.place(x=10, y=80)
        self.message_text = tk.Text(master, width=40, height=12)        
        self.message_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config()
        self.message_text.place(x=10, y=110)
        
        options1 = [ #設定被連結開發板之IP
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

        options2 = [ #設定連結開發板之IP
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
            "192.168.50.239",
            "192.168.0.101"
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
    
    def test_function(self):
        pass

    def toggle_tag_detector(self):
        
        self.tagcontrol = not self.tagcontrol

    def put_intersection(self):
        self.putintersection = not self.putintersection
        
    # -------------- ↓ 計算 MSRR 延伸線之交點 ↓ -------------- #
    def intersection(self):
        globals.initialize()
        tag_intersection.intersection(self)

        print('INTERSECTION_X = {:.2f}, INTERSECTION_Y = {:.2f}'.format(globals.intersection_x, globals.intersection_y))

    def clearBox(self): # 清除 Response 訊息框中的所有訊息
        self.message_text.delete("1.0", "end")
    
    #------------------ ↓ 顯示影像 ↓ ------------------#       
    def update_video(self):
        # 從攝影機捕捉一張畫面
        ret, frame = self.cam.read()
        center = (0, 0)
        # print("type = ", type(frame))
        # try:
        #     if self.tagcontrol:
        #         tag.tag(self, frame) # 使用外部tag.py檔案進行比對
        #         # self.tag(frame)
        # except BaseException as e:
        #     print(e)
        

        if self.tagcontrol:
            tag_detector.Tag.tag(self, frame) # 使用外部tag.py檔案進行比對
            # print('MID_AD = ', (globals.intersection_x, globals.intersection_y))
            # self.tag(frame)
            print('MID_AD_X = ', globals.mid_ad_x, 'MID_AD_Y = ', globals.mid_ad_y)

        if self.putintersection:
           cv2.circle(frame, (int(globals.intersection_x), int(globals.intersection_y)), 1, (0, 0, 255), 4)

        # 將OpenCV圖像格式轉換為PIL圖像格式
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)      
        # image = cv2.flip(image, 1) #將攝影機畫面左右翻轉  
        image = Image.fromarray(image)
                
        # 將PIL圖像格式轉換為Tkinter支援的圖像格式
        photo = ImageTk.PhotoImage(image)

        # 在視窗上顯示圖像
        self.video_area.configure(image=photo)
        self.video_area.image = photo

        # 每 15 毫秒更新一次畫面
        self.master.after(15, self.update_video) 
        
        # -------------- ↓ Apriltag 檢測器 ↓ -------------- # 

    def snapshot(self):
        ret, frame = self.cam.read()
        # frame_flip = cv2.flip(frame, 1)
        if ret:
            cv2.imwrite("./image/snapshot.jpg", frame)

    def send_command(self,value):
        # 取得使用者輸入的指令
        # command = self.input_entry.get()
        command = value
        # package = pack
# ----------------------- ↓ Socket 客戶端 ↓ ----------------------- #
        data='Connect fail!'.encode('utf-8')
        # 連接到TCP服務器
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                print(HOST)
                sock.settimeout(0.5)
                sock.connect((HOST, PORT))

                # 傳送指令
                sock.sendall(command.encode())
                # sock.sendall(command)
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

    def connect(self):

        def reading_error():
            pass

        def send_connect_command():
            pass

        thread_reading_error = threading.Thread(target=reading_error)
        thread_send_connect_command = threading.Thread(target=send_connect_command)

        thread_reading_error.start()
        thread_send_connect_command.start()

        thread_reading_error.join()
        thread_send_connect_command.join()

# 建立主視窗
root = tk.Tk()
#設定程式啟動時的視窗大小
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width - win_width) / 2) 
y = int((screen_height - win_height) / 2)
root.geometry(f"{win_width}x{win_height}+{x}+{y-30}") #設定視窗初始位置

app = App(root)
root.mainloop()