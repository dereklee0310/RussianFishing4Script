## About the Project
A simple fishing bot for Russian Fishing 4, supporting spin, bottom and marine fishing.  
- [Discord][discord]
- [中文版教程][chinese_guide]

## 4/19 Patchnotes
**Please refer to `template.ini` to check newly added settings**
- Ended support for other languages, see [Integrity Guide][integrity_guide]
- Added file integrity check for images
- Improved image quality of zh-CN versions
- Added setting for default startup options
- Added whitelist setting for release of unmarked fish
- Added automatic broken lure replacement feature
- Added "replace" option for `lure_broken_action` setting in `config.ini`
- Fixed a bug that was causing the tackle to be identified as "not ready"
- Fixed a bug where the game wouldn't quit when the line was at the end
- Fixed a syntax error in `player.plot_and_save()`

## Built With
- Python 3.11 
- PyAutoGUI

## Getting Started  
### Prerequisites
- Set the language in `config.ini` and [add missing images][integrity_guide] if you want to use Russian or Chinese other than English version (default)
- Set your in-game interface scale as "1x"
- Enable Mouse ClickLock in Windows mouse settings and set the time before locking to "Long"  
![ClickLock][clicklock]
- To refill your stats without using shortcuts (e.g., 1 ~ 7), add tea, carrot, and coffee to your  
  favorites so that they can be selected through quick food selection menu
- To enable automatic broken lure replacement, the lures for replacement must be added to favorites
![Favorite food][favorite_food]
![Favorite lure][favorite_lure]


### Install
- Option1: [Download][download]
the repository and unzip it
- Option2: Use `git clone <url>`, Git must be installed
```
git clone https://github.com/dereklee0310/RussianFishing4Script
```

### Dependencies
```
.\setup.bat
```

### Configuration
- To edit user profiles, refer to the guides and examples in `template.ini` and edit `config.ini`  
- To enable email notification, set your Gmail address and Google app password in `.env`  
- Edit `SMTP_SERVER` in `.env` if you want to use SMTP server other than GMAIL SMTP server

## Usage
- Move your character to the fishing spot before executing the script
- Spin Fishing/Marine Fishing: Pick up the rod you want to use
- Bottom Fishing: Add the tackles you want to use to the quick selection slots and place  
them nearby to let the script access them via quick selection shortcuts (1 ~ 3)

### 1. Change the current working directory
```
cd src
```

### 2. Validate spool Icon (optional)
- If you are using this script for the first time,
  run this to check if the spool icon can be recognized (The reel must be fully loaded)
- The script use the meter of rainbow line for recognition instead if `-R` option is used.
![Spool icon][spool_icon]
```
python validate.py
```

### 3. Execute the main script
Here are some examples of how to execute the script with different arguments:
- Display help information
```
python app.py -h
```

- Run with default settings
```
python app.py
```
- Display a list of available user profiles and set the number of fishes in the keepnet to 32 (68 fishes to catch)
```
python app.py -n 32
```
- Select profile 3, drink the coffee while battling against fish, and send an email to yourself after it's terminated
```
python app.py -p 3 --coffee --email
```
- Release unmarked fish, enable hunger and comfort refill, and plot a catch/hour chart after it's terminated
```
python app.py -mrP
```
## Other Useful Scripts
### Toggle moving forward
- Press w to stop/continue, press s to quit.
- Use `-s` to hold the Shift key
```
python move.py [-s]
```

### Item crafting
- The materials must be selected before the execution
- Specify the number of items to craft with `-n QUANTITY` 
- Use `-d` to discard all the crafted items
```
python craft.py [-d] [-n QUANTITY]
```

### Calculate the maximum friction brake you can use on your tackle
```
python calculate.py
```

### Harvest baits and refill stats automatically
- Start a harvesting loop without moving or fishing
- Use `-s` to open control panel while waiting for energy to regenerate
- Use `-n CHECK_DELAY_SECOND` to specify the delay between two checks
```
python harvest.py [-s] [-n CHECK_DELAY_SECOND]
```

## Troubleshooting
- How to exit the program?
  - Use `Ctrl + C` to send a KeyboardInterrupt signal
- Failed to exit the program?
  - The Shift key might have been pressed down, press again to release it, then type `Ctrl + C` as usual
- Rod not getting lifted after the retrieval is finished?
  - Change the game resolution until the `validation.py` is pass
  - Lower the value of `spool_icon_confidence` in `config.ini`
  - Keep away from light sources or turn off the boat light

## License
[GNU General Public License version 3][license]

## Contributing
Any contribution, bug report, or idea about new features is welcome.

## Contact me
Email: dereklee0310@gmail.com 

[discord]: https://discord.gg/BZQWQnAMbY
[chinese_guide]: 中文版教程.md
[integrity_guide]: integrity_guide.md
[clicklock]: /static/readme/clicklock.png
[favorite_food]: /static/readme/favorites.png
[favorite_lure]: /static/readme/favorites_2.png
[download]: https://github.com/dereklee0310/RussianFishing4Script/archive/refs/heads/main.zip
[spool_icon]: /static/readme/status.png
[license]: LICENSE