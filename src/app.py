from fisherman import Fisherman
from pyautogui import getWindowsWithTitle
# from inputimeout import inputimeout, TimeoutOccurred
import configparser
from time import sleep
import sys

class Controller():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('../config.ini')

    def show_prompt(self):
        config = self.config
        print('+---------------------------------------+')
        print('| Welcome to use the RF4 fishing script |')
        print('|     Please select a configuration     |')
        print('+---------------------------------------+')
        print('| 0. edit custom configuration          |')
        print('+---------------------------------------+')
        for i, section in enumerate(config.sections()):
            print(f'| {i + 1}. {section:34} |')
            print('+---------------------------------------+')

        idx = input('Profile number: ')
        while not idx.isdigit() or int(idx) < 0 or int(idx) > len(config.sections()):
            print('Invalid profile number, please try again.')
            idx = input('Profile number: ')
        if int(idx) == 0:
            print('Not implemented yet.')
            exit()

        profile = config[config.sections()[int(idx) - 1]] 
        fishing_strategy = profile['fishing_strategy']
        release_strategy = profile['release_strategy']
        current_fish_count = int(profile['current_fish_count'])
        sleep(0.2)
        print(f'Fishing strategy: {fishing_strategy}')
        sleep(0.2)
        print(f'Release strategy: {release_strategy}')
        sleep(0.2)
        print(f'Current number of fish: {current_fish_count}')
        sleep(0.2)

        #todo: trophy mode

        for i in range(3, 0, -1):
            print(f'The script will start in: {i} seconds', end='\r')
            sleep(1)
        print('')
        print('Start executing the script')

        return fishing_strategy, release_strategy, current_fish_count
    
    def show_save_prompt(self, strategy, release_strategy, fish_count):
        if 'y' == input('Do you want to save the current setting?'):
            config = configparser.ConfigParser()
            name = input('Please enter the name of the new setting withoutt "-" or spaces: ')
            if '-' in name or ' ' in name:
                print('Failed to save the setting due to an invalid name')
                return
            config[name] = {
                'fishing_strategy': strategy,
                'release_strategy': release_strategy,
                'fish_count': fish_count
            }
        #todo


# fishing_strategy, release_strategy, fish_count, trophy_mode = Controller().show_prompt()
fishing_strategy, release_strategy, current_fish_count = Controller().show_prompt()
fisherman = Fisherman(fishing_strategy, release_strategy, current_fish_count, None) #todo: trophy mode is none
window = getWindowsWithTitle("Russian Fishing 4")[0]
window.activate()
fisherman.start_fishing()