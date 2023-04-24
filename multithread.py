import threading

class MyThread(threading.Thread):
    def __init__(self, num):
        threading.Thread.__init__(self)
        self.num = num

    def run(self):
        print("Thread", self.num, "starts")
        # do something
        print("Thread", self.num, "ends")

if __name__ == "__main__":
    thread1 = MyThread(1)
    thread2 = MyThread(2)
    thread3 = MyThread(3)
    
    thread1.start()
    thread2.start()
    thread3.start()

    thread1.join()
    thread2.join()
    thread3.join()

    print("All threads finished")