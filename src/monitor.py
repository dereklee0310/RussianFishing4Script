"""
Module for pyautogui.locateOnScreen wrappers.

Todo:
    Validate language option
    Implement snage detection
"""
from pyautogui import locateOnScreen, locateCenterOnScreen

from script import get_image_dir_path

parent_dir = get_image_dir_path()

def is_fish_hooked():
    return locateOnScreen(fr'{parent_dir}get.png', confidence=0.8)

def is_tackle_broke():
    return locateOnScreen(fr'{parent_dir}broke.png', confidence=0.6)

def is_disconnected():
    return locateOnScreen(fr'{parent_dir}disconnected.png', confidence=0.9)

def is_fish_captured():
    return locateOnScreen(fr'{parent_dir}keep.png', confidence=0.9)

def is_retrieve_finished():
    return locateOnScreen(fr'{parent_dir}wheel.png', confidence=0.985)
is_spool_icon_valid = is_retrieve_finished # for validate.py

def is_tackle_ready():
    return locateOnScreen(fr'{parent_dir}ready.png', confidence=0.6)

def is_fish_marked():
    return locateOnScreen(fr'{parent_dir}mark.png', confidence=0.7)

def is_moving_in_bottom_layer():
    return locateOnScreen(fr'{parent_dir}movement.png', confidence=0.7)

# quit through ese menu
def get_quit_position():
    return locateOnScreen(fr'{parent_dir}quit.png', confidence=0.8)

def get_yes_position():
    return locateOnScreen(fr'{parent_dir}yes.png', confidence=0.8)

def get_make_position():
    return locateOnScreen(fr'{parent_dir}make.png', confidence=0.8)

def is_operation_failed():
    return locateOnScreen(fr'{parent_dir}warning.png', confidence=0.8)

def get_ok_position():
    return locateOnScreen(fr'{parent_dir}ok.png', confidence=0.8)

# quit through main menu
def get_exit_icon_position():
    return locateOnScreen(fr'{parent_dir}exit.png', confidence=0.8)

def get_confirm_exit_icon_position():
    return locateOnScreen(fr'{parent_dir}confirm_exit.png', confidence=0.8)

def is_harvest_success():
    return locateOnScreen(fr'{parent_dir}harvest_confirm.png', confidence=0.8)

def get_energy_icon_position():
    return locateCenterOnScreen(fr'{parent_dir}energy.png', confidence=0.8)

def get_food_icon_position():
    return locateCenterOnScreen(fr'{parent_dir}food.png', confidence=0.8)

def get_comfort_icon_position():
    return locateCenterOnScreen(fr'{parent_dir}comfort.png', confidence=0.8)

def get_carrot_icon_position():
    return locateOnScreen(fr'{parent_dir}carrot.png', confidence=0.8)

def get_tea_icon_position():
    return locateOnScreen(fr'{parent_dir}tea.png', confidence=0.9)

def get_coffee_icon_position():
    return locateOnScreen(fr'{parent_dir}coffee.png', confidence=0.9)