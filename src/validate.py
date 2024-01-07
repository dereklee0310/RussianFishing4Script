"""
Check if the spool is fully loaded and in the right position.

Usage: validate.py
"""
from time import sleep
from script import activate_game_window
from monitor import is_spool_icon_detected

if __name__ == '__main__':
    activate_game_window()
    sleep(0.25)
    if not is_spool_icon_detected():
        print('Test failed.')
        print('Please make sure your reel is at full capacity or adjust the game resolution and try again.')
    else:
        print('Test pass.')