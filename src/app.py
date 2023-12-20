from fisherman import Fisherman
from pyautogui import getWindowsWithTitle
# from inputimeout import inputimeout, TimeoutOccurred
import configparser
from time import sleep
from userprofile import UserProfile

class App():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('../config.ini')
        self.profile_names = ['custom']
        self.profile = None


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
                self.profile_names.append(section)
                print(f'| {idx}. {section:{34 - idx // 10}} |')
                print('+---------------------------------------+')
                idx += 1
    

    def get_profile_id(self):
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
        self.profile_id = id
        

    def set_profile(self):
        profile_name = self.profile_names[int(self.profile_id)]
        section = self.config[profile_name]
        self.profile = UserProfile(
            profile_name,
            section['reel_name'],
            section['fishing_strategy'],
            section['release_strategy'],
            int(section['current_fish_count']))
        

    def display_selected_profile(self):
        profile = self.profile
        print('+---------------------------------------+')
        print(f'| Profile name: {profile.profile_name:23} |')
        print('+---------------------------------------+')
        print(f'| Reel name: {profile.release_strategy:26} |')
        print('+---------------------------------------+')
        print(f'| Fishing strategy: {profile.fishing_strategy:19} |')
        print('+---------------------------------------+')
        print(f'| Release strategy: {profile.release_strategy:19} |')
        print('+---------------------------------------+')
        print(f'| Current number of fish: {str(profile.current_fish_count):13} |')
        print('+---------------------------------------+')
    

    def start_count_down(self):
        if self.config['misc'].getboolean('enable_count_down'):
            print("Hint: Edit 'enable_count_down' option in config.ini to disable the count down")
            for i in range(5, 0, -1):
                print(f'The script will start in: {i} seconds', end='\r')
                sleep(1)
            print('')
        print('The script has been started.') 

    #todo
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


def main():
    app = App()
    app.show_welcome_prompt()
    app.get_profile_id()
    app.set_profile()
    app.display_selected_profile()
    app.start_count_down()
    window = getWindowsWithTitle("Russian Fishing 4")[0]
    window.activate()

    fisherman = Fisherman(app.profile) #todo: trophy mode is none
    fisherman.start_fishing()

if __name__ == '__main__':
    main()