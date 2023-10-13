from pyautogui import *

import pyautogui
import time
import keyboard
import random  
import win32api, win32con
import random
from time import sleep
import sys
import datetime

fish_count = 0
start_time = time.time()
miss_count = 0

def resetTackle(fish_count):
    counter = 10
    
    while pyautogui.locateOnScreen('ready.png', confidence=0.6) == None:
        print('tackle is not ready')
        pyautogui.keyDown('shift')
        pyautogui.mouseDown()
        sleep(1)
        pyautogui.mouseUp()
        pyautogui.keyDown('shift')
        sleep(0.5)
        if counter == 0:
            # pyautogui.click()
            # sleep(0.1)
            # pyautogui.mouseDown()
            # sleep(3) # windows will handle the rest of the retrieval
            # pyautogui.mouseUp()
            return fish_count
        counter -= 1
    print('tackle is ready')
    return fish_count

def castTackle():
    sleep(1)
    pyautogui.keyDown('shift')
    pyautogui.mouseDown()
    sleep(1)
    pyautogui.keyUp('shift')
    pyautogui.mouseUp()
    sleep(6)
    pyautogui.mouseDown()
    sleep(3) # windows will handle the rest of the retrieval
    pyautogui.mouseUp()
    print('finish throwing')

def retrieveTackle(fish_count):
    retrieve_limit = 600
    print('start retrieving')
    while pyautogui.locateOnScreen('wheel.png', confidence=0.985) == None:
        # if pyautogui.locateOnScreen('snag.png', confidence=0.977):
        #     print('snagged')
        #     quit(is_session=True, is_full=False)
        if retrieve_limit < 0:
            return fish_count
        else:
            retrieve_limit -= 1
        sleep(1)
    print('finish retrieving')
    pyautogui.mouseDown()
    sleep(2)
    pyautogui.mouseUp()
    return fish_count

def quit(is_session=False, is_full=True):
    pyautogui.press('esc')
    if is_session:
        pyautogui.keyDown('shift')
    pyautogui.moveTo(pyautogui.locateOnScreen('quit.png', confidence=0.9), duration=0.2)
    pyautogui.click()
    pyautogui.moveTo(pyautogui.locateOnScreen('yes.png', confidence=0.9), duration=0.2)
    pyautogui.click()
    if is_session:
        pyautogui.keyUp('shift')
        sleep(2) # wait after quit
        login(is_full)
    else:
        print(f'execution time: {str(datetime.timedelta(seconds=time.time() - start_time))}')
        sys.exit()

def login(is_full=True):
    pyautogui.moveTo(pyautogui.locateOnScreen('login_16x9.png', confidence=0.9), duration=0.2)
    pyautogui.click()
    sleep(1)
    pyautogui.click()
    print('waiting the game to load...')
    sleep(60)

    if not is_full:
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(-1100), int(0), 0, 0)
        sleep(1)
        pyautogui.keyDown('up')
        sleep(6)
        pyautogui.keyUp('up')
        return
    
    pyautogui.keyDown('e')
    sleep(1)
    pyautogui.keyUp('e')
    sleep(0.5)

    pyautogui.moveTo(pyautogui.locateOnScreen('price.png', confidence=0.9), duration=0.2)
    pyautogui.click()
    sleep(0.5)
    pyautogui.moveTo(pyautogui.locateOnScreen('all.png', confidence=0.9), duration=0.2)
    pyautogui.click()

    sleep(0.1)
    pyautogui.click()

    while pyautogui.locateOnScreen('trophy.png', confidence=1) != None:
        pyautogui.moveTo(pyautogui.locateOnScreen('trophy.png', confidence=1), duration=0.2)
        pyautogui.moveRel(0, 30, duration=0.2)
        pyautogui.keyDown('ctrl')
        pyautogui.click()
        sleep(0.1)
        pyautogui.keyUp('ctrl')
    
    pyautogui.moveTo(pyautogui.locateOnScreen('sell.png', confidence=0.9), duration=0.2)
    pyautogui.click()
    sleep(1)
    
    pyautogui.press('e')
    sleep(1)

    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(-1100), int(0), 0, 0)
    sleep(1)
    pyautogui.keyDown('up')
    sleep(6)
    pyautogui.keyUp('up')


def pullTheFish(fish_count):
    print('retrieve the rest of the line')
    pyautogui.click() # reset the click lock 
    pyautogui.keyDown('shift')
    for i in range(2):
        print(f'drag {i}')
        pyautogui.mouseDown()
        sleep(1.5)
        pyautogui.mouseUp()
        sleep(0.001)
    pyautogui.keyUp('shift')


    if pyautogui.locateOnScreen('get.png', confidence=0.8) != None:
        print('start pulling fish')
        
        # offset = 0
        get_counter = 10
        pyautogui.mouseDown(button="right")
        while pyautogui.locateOnScreen('keep.png', confidence=0.9) == None:
            get_counter -= 1
            if get_counter < 0:
                pyautogui.mouseDown()
                sleep(0.5)
                pyautogui.mouseUp()
                pyautogui.mouseUp(button="right")
                return fish_count
            print('getting fish')
            # win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(0), int(-10), 0, 0)
            # offset += 10
            # pyautogui.moveRel(0, -200, duration=1)
            pyautogui.mouseDown()
            sleep(1)
            pyautogui.mouseUp()
            sleep(0.1)
        
        pyautogui.mouseUp(button="right")
        sleep(0.5)
        # pyautogui.rightClick()
        # sleep(0.5)
        print('finish pulling')
        pyautogui.press('space')
        sleep(0.5)
        # win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(0), int(offset), 0, 0)
        # pyautogui.moveRel(0, offset)
        fish_count += 1
        print(f'got a fish!, this is the {fish_count}st fish!')
        if fish_count == capacity:
            print('fish net is full')
            # quit(is_session=True)
            quit(is_session=False, is_full=False)
            fish_count = 0
    else:
        print('no fish!, trying to cast the tackle again...')
    sleep(0.5)
    return fish_count


# adjust
# print('start the program in: ', end='')
# print(pyautogui.FAILSAFE)

# windows = pyautogui.getAllWindows()
# for window in windows:
#     print(window)

capacity = 100 - int(input('enter current fish number: '))
print(capacity)
for i in range(3, 0, -1):
    sleep(1)
    print('start the program in:', i, end='\r')
print('')

window = pyautogui.getWindowsWithTitle("Russian Fishing 4")[0]
window.activate()

pre_fish_count = 0
fail_count = 5

miss_count = 0
hit_count = 0

check_delay = 5

try:
    i = 0
    while True:
        i = 1 if i == 3 else i + 1
        pyautogui.press(f'{i}')
        sleep(1)
        print(f'checking if rod {i} got a fish...')
        if pyautogui.locateOnScreen('get.png', confidence=0.8) != None:
            print('got a fish!')
            pyautogui.mouseDown()
            sleep(3)
            pyautogui.mouseUp()
            fish_count = retrieveTackle(fish_count)
            fish_count = pullTheFish(fish_count)

            if hit_count == 3:
                hit_count = 0
                check_delay -= 1
                print(f'current check delay: {check_delay} seconds')
            hit_count += 1
        else:
            print(f'no fish on rod {i}')
            if miss_count == 3:
                miss_count = 0
                check_delay += 1
                print(f'current check delay: {check_delay} seconds')
            miss_count += 1
            sleep(5)
            continue
        fish_count = resetTackle(fish_count)
        sleep(1)
        pyautogui.keyDown('shift')
        pyautogui.mouseDown()
        sleep(1)
        pyautogui.keyUp('shift')
        pyautogui.mouseUp()
        pyautogui.click()
        sleep(1)
        pyautogui.click()
        pyautogui.press('0')
        sleep(5)

        # pre_fish_count = fish_count
        # if pyautogui.locateOnScreen('broke.png', confidence=0.6):
        #     print('broked')
        #     quit(is_session=False, is_full=False)
        # fish_count = resetTackle(fish_count)
        # castTackle()
        # fish_count = retrieveTackle(fish_count)
        # fish_count = pullTheFish(fish_count)

        # if fish_count == pre_fish_count:
        #     fail_count -= 1
        # else:
        #     fail_count = 5

        # if fail_count == 0:
        #     fail_count = 5
        #     pyautogui.click()
        #     direction = random.choice(['left', 'right'])
        #     print(f'move {direction}!')
        #     pyautogui.keyDown(direction)
        #     sleep(random.uniform(0, 0.5))
        #     pyautogui.keyUp(direction)
except KeyboardInterrupt:
    sys.exit()
        
    
sleep(5)
pyautogui.mouseDown()
# sleep(time)
sleep(3)
pyautogui.mouseUp()
    
    
# else:
#     print("No")