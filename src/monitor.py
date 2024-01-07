"""
Module for wrappers of pyautogui.locateOnScreen.

Todo:
    Validate language option
    Implement is_tackle_snagged()
"""
from pyautogui import locateOnScreen
import configparser

config = configparser.ConfigParser()
config.read('../config.ini')
dir = fr"../static/{config['game']['language']}"

def is_fish_hooked():
    return locateOnScreen(fr'{dir}/get.png', confidence=0.8)

def is_tackle_broked():
    return locateOnScreen(fr'{dir}/broke.png', confidence=0.6)

def is_fish_captured():
    return locateOnScreen(fr'{dir}/keep.png', confidence=0.9)

def is_retrieve_finished():
    return locateOnScreen(fr'{dir}/wheel.png', confidence=0.985)
is_spool_icon_detected = is_retrieve_finished

def is_tackle_ready():
    return locateOnScreen(fr'{dir}/ready.png', confidence=0.6)

def is_fish_marked():
    return locateOnScreen(fr'{dir}/mark.png', confidence=0.7)

def is_moving_in_bottom_layer():
    return locateOnScreen(fr'{dir}/movement.png', confidence=0.7)

def get_quit_position():
    return locateOnScreen(fr'{dir}/quit.png', confidence=0.8)

def get_yes_position():
    return locateOnScreen(fr'{dir}/yes.png', confidence=0.8)

def get_make_position():
    return locateOnScreen(fr'{dir}/make.png', confidence=0.8)

def is_operation_failed():
    return locateOnScreen(fr'{dir}/warning.png', confidence=0.8)

def get_ok_position():
    return locateOnScreen(fr'{dir}/ok.png', confidence=0.8)