"""
Module for pyautogui.locateOnScreen wrappers.

Todo:
    Validate language option
    Implement snag detection
"""
from configparser import ConfigParser

from pyautogui import locateOnScreen, locateCenterOnScreen, pixel

config = ConfigParser()
config.read('../config.ini')
parent_dir = fr"../static/{config['game']['language']}/"
spool_icon_confidence = config['game'].getfloat('spool_icon_confidence', fallback=0.985)

# ---------------------------------------------------------------------------- #
#                           icon and text recognition                          #
# ---------------------------------------------------------------------------- #
def is_fish_hooked():
    return locateOnScreen(fr'{parent_dir}get.png', confidence=0.8)

def is_tackle_broke():
    return locateOnScreen(fr'{parent_dir}broke.png', confidence=0.6)

def is_disconnected():
    return locateOnScreen(fr'{parent_dir}disconnected.png', confidence=0.9)

def is_fish_captured():
    return locateOnScreen(fr'{parent_dir}keep.png', confidence=0.9)

def is_retrieve_finished():
    return locateOnScreen(fr'{parent_dir}wheel.png', confidence=spool_icon_confidence) # original: 0.985
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
    return locateOnScreen(fr'{parent_dir}make.png', confidence=0.9)

def is_operation_failed():
    return locateOnScreen(fr'{parent_dir}warning.png', confidence=0.8)

def is_operation_success():
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

def is_line_at_end():
    return locateOnScreen(fr'{parent_dir}spooling.png', confidence=0.98)

# ---------------------------------------------------------------------------- #
#                         player status bar analyzation                        #
# ---------------------------------------------------------------------------- #
def is_energy_high(threshold: float) -> bool:
    """Check if the energy level is high enough to harvest baits

    :param threshold: energy level threshold
    :type threshold: float
    :return: True if high enough, False otherwise
    :rtype: bool
    """
    pos = get_energy_icon_position()
    if not pos:
        return False
    x, y = int(pos.x), int(pos.y)
    # default threshold: 0.74,  well done FishSoft
    last_point = int(19 + 152 * threshold) - 1
    return pixel(x + 19, y) == pixel(x + last_point, y)
    
def is_food_level_low() -> bool:
    """Check if food level is low.

    :return: True if lower than 50%, False otherwise
    :rtype: bool
    """
    pos = get_food_icon_position()
    if not pos:
        return False
    x, y = int(pos.x), int(pos.y)
    last_point = int(18 + 152 * 0.5) - 1
    return not pixel(x + 18, y) == pixel(x + last_point, y)

def is_comfort_low() -> bool:
    """Check if comfort is low.

    :return: True if lower than 51%, False otherwise
    :rtype: bool
    """
    pos = get_comfort_icon_position()
    if not pos:
        return False
    x, y = int(pos.x), int(pos.y)
    last_point = int(18 + 152 * 0.51) - 1
    return not pixel(x + 18, y) == pixel(x + last_point, y)