from monitor import is_spool_icon_dected
from pyautogui import getWindowsWithTitle
from time import sleep


window = getWindowsWithTitle("Russian Fishing 4")[0]
window.activate()
sleep(1)
if not is_spool_icon_dected():
    print('Failed to identify the spool icon.')
    print('Please make sure your reel is at full capacity or change the game resolution and try again.')
else:
    print('Test pass.')