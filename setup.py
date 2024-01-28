import configparser
import os
from pathlib import Path

def setup_config():
  config = configparser.ConfigParser()
  # config.read('config.ini')

  # for section in config.sections():
  #     print(section)
  #     for item in config[section]:
  #         print(item, config[section][item])

  if os.path.isfile('config.ini'):
    print('config.ini already exists')
    if 'y' != input('Do you want to restore the default configuration? [Y/n] ').lower():
      return False
    else:
      print('config.ini has been reset')
  else:
    print('config.ini has been created')

  with open('config.ini', 'w') as file:
    config['script'] = {'relogin': 'False',
                        'backup_rod': 'False',
                        'switch_map': 'False',
                        'keep_trophy': 'True',
                        'screenshot_trophy': 'True',
                        'sell_fish': 'False',
                        'digging': 'False'}
    
    config['game'] = {'resolution' : '1600, 900',
                      'premium' : 'False',
                      'inverse_shift' : 'True',
                      'map' : 'belaya',
                      'fishing_strategy': 'spinning',
                      'release_strategy': 'none',
                      'fish_spot' : '73, 48',
                      'fish_count' : '0'}

    config.write(file)

def create_screenshot_dir():
  screenshot_dir = Path("./screenshots")
  if os.path.exists(screenshot_dir):
    print('screenshots/ already exists')
  else:
    print('screenshots/ has been created')
    screenshot_dir.mkdir(exist_ok=True, parents=True)

# todo: revise this function
# setup_config() 
create_screenshot_dir()