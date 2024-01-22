import pyautogui
import sys
import random
import time as tm



# try:
set_range = 400000
full = 0
pyautogui.FAILSAFE = False
for x in range(0, set_range):
    # y = random.random(0,10)
    y = random.randint(10,30)
    # pyautogui.press('numlock') #available also with numlock for only 3.99$
    # print(y)
    # pyautogui.PAUSE = y
    pyautogui.press('scrolllock')
    # time = y*10
    time = y*2
    pyautogui.PAUSE = time
    full += time
    #tm.strftime('%H:%M:%S', tm.gmtime(time))
    print(x, time, full, tm.strftime('%H:%M:%S', tm.gmtime(full)))

    #


print("done")
# except KeyboardInterrupt:
#     sys.exit(0)
#     raise

