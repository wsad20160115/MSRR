import threading
import time

def print_numbers():
    for i in range(1, 6):
        time.sleep(0.5)
        print(i)

def print_letters():
    for letter in ['a', 'b', 'c', 'd', 'e']:
        time.sleep(0.3)
        print(letter)

t1 = threading.Thread(target=print_numbers)
t2 = threading.Thread(target=print_letters)

t1.start()
t2.start()

t1.join()


print("Done!")