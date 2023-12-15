from fisherman import Fisherman
from pyautogui import getWindowsWithTitle
# from inputimeout import inputimeout, TimeoutOccurred
import configparser
from time import sleep
import sys

class App():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('../config.ini')
        self.profiles = ['custom']


    def show_welcome_prompt(self):
        print('+---------------------------------------+')
        print('|   Welcome to use RF4 fishing script   |')
        print('|     Please select a configuration     |')
        print('+---------------------------------------+')
        print('| 0. edit custom configuration          |')
        print('+---------------------------------------+')

        idx = 1
        for section in self.config.sections():
            if self.config.has_option(section, 'fishing_strategy'):
                self.profiles.append(section)
                print(f'| {idx}. {section:34} |')
                print('+---------------------------------------+')
                idx += 1
    

    def get_profile(self):
        id = input('Profile number: ')
        while not id.isdigit() or int(id) < 0 or int(id) > len(self.config.sections()):
            print('Invalid profile number, please try again or press q to quit')
            id = input('Profile number: ')
            if id == 'q':
                print('The script has been terminated.')
                exit()
        if int(id) == 0:
            print('Not implemented yet.') #todo
            exit()
        self.profile_name = self.profiles[int(id)]
        self.profile = self.config[self.profile_name ]


    def display_selected_profile(self):
        self.fishing_strategy = self.profile['fishing_strategy']
        self.release_strategy = self.profile['release_strategy']
        self.current_fish_count = int(self.profile['current_fish_count'])
        
        print('+---------------------------------------+')
        print(f'| Profile name: {self.profile_name:23} |')
        print('+---------------------------------------+')
        print(f'| Fishing strategy: {self.fishing_strategy:19} |')
        print('+---------------------------------------+')
        print(f'| Release strategy: {self.release_strategy:19} |')
        print('+---------------------------------------+')
        print(f'| Current number of fish: {str(self.current_fish_count):13} |')
        print('+---------------------------------------+')
    

    def start_count_down(config):
        if config['misc'].getboolean('enable_count_down'):
            print("Hint: Edit 'enable_count_down' option in config.ini to disable the count down")
            for i in range(5, 0, -1):
                print(f'The script will start in: {i} seconds', end='\r')
                sleep(1)
        print('')
        print('Start executing the script')     


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


# entry point
def main():
    app = App()
    app.show_welcome_prompt()
    app.get_profile()
    app.display_selected_profile()

    if app.config['misc'].getboolean('enable_count_down'):
        print("Hint: Edit 'enable_count_down' option in config.ini to disable the count down.")
        for i in range(5, 0, -1):
            print(f'The script will start in: {i} seconds', end='\r')
            sleep(1)
        print('')
    print('The script has been started.') 

    #todo: edit arguments
    fisherman = Fisherman(app.fishing_strategy, app.release_strategy, app.current_fish_count, None) #todo: trophy mode is none
    window = getWindowsWithTitle("Russian Fishing 4")[0]
    window.activate()
    fisherman.start_fishing()

if __name__ == '__main__':
    main()