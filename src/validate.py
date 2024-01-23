"""
Check if the spool is fully loaded and is in the right position.

Usage: validate.py
"""
from windowcontroller import WindowController
from monitor import is_spool_icon_valid

if __name__ == '__main__':
    controller = WindowController()
    controller.activate_game_window()
    
    if not is_spool_icon_valid():
        print('TEST FAILED')
        print('Please make sure your reel is at full capacity or adjust the game resolution and try again')
    else:
        print('TEST PASSED')