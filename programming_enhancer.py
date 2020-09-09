import pyautogui
import sys
import random

#use gloves for stronger effect

try:
    set_range = 1000
    for x in range(0, set_range):
        y = random.random()
        # pyautogui.press('numlock') #available also with numlock for only 3.99$
        # print(y)
        # pyautogui.PAUSE = y
        pyautogui.press('capslock')
        pyautogui.PAUSE = y
        print(y*2)

        #


    print("done")
except KeyboardInterrupt:
    sys.exit(0)
    raise

