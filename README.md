## About the Project
A simple bot for AFKing Russian Fishing 4, supporting spin, bottom and marine fishing.  
Star the repo to support this project, and "watch" it to get the latest news :)
- [文字教程](中文版教程.md)
- [視頻教程](https://www.youtube.com/watch?v=znLBYoXHxkw)

## Patchnotes
### 3/13
**Please refer to `template.ini` to configure newly added settings.**
- Change: Replace countdown before execution with user confirmation
- Change: Improve logging messages
- Change: Improve module import style, add docstrings
- Change: Refactor and improve `Toggle moving forward`
- Fix: `Item crafting` bug for groundbaits making
- Fix: Eliminate the delay before pulling when fishing for Atlantic saury 
- Add: Table of results for `Item crafting`
- Add: Discard option for `Item crafting`
- Add: Pirking timeout option for marine fishing
- Add: Option for delay time before keeping captured fish
- Add: Alcohol drinking option and settings
- Add: Quick selection menu support for carrot, tea and coffee
- Add: Option for hook checking delay for marine fishing

### 3/14
- Fix: Retrieval get stuck while performing marine fishing
- Fix: Pulling bug caused by mouse locking

## Built With
- Python 3.11 
- PyAutoGUI

## Getting Started  
### Prerequisites
- Set your in-game language in `config.ini`
- Set your in-game interface scale as "1x"
- Enable Mouse ClickLock in Windows mouse settings and set the time before locking to "Long"  
![ClickLock](/static/readme/clicklock.png)
- To refill player's stats automatically, add tea and carrot, and coffee to your  
  favorite items so that they can be selected through quick food selection menu.  
  Otherwise, they can only be accessed by quick selection shortcuts (e.g., 1 ~ 7)  
![Favorites](/static/readme/favorites.png)

### Install
```
git clone https://github.com/dereklee0310/RussianFishing4Script
```
Or, download the repository and unzip it.

### Dependencies
```
.\setup.bat
```

### Configuration
To edit user profiles, refer to the guides and examples in `template.ini` and edit `config.ini`.  
To enable email notification, set your Gmail address and Google app password in `.env`

## Usage
- Move your character to the fishing spot before executing the script.
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
![Status](/static/readme/status.png)
```
python validate.py
```

### 3. Execute the main script
Here are some examples of how to execute the script with different options:
- Display a list of available user profiles and run with the default settings
```
python app.py
```
- Display a list of available user profiles and set the number of fishes in keepnet to 32 (68 fishes to catch)
```
python app.py -n 32
```
- Select profile 3, drink the coffee while battling against fish, and send an email to yourself after it's terminated
```
python app.py -p 3 -c -e
```
- Release unmarked fishes, enable food/comfort refill, and plot a catch per running/in-game hour chart after it's terminated.
```
python app.py -m -r -P
```
- Drink alcohol regularly
```
python app.py -A
```
- Display help information
```
python app.py -h
```
## Other Useful Scripts
### Toggle moving forward
- Press w to stop, press it again to continue.
- Press s to quit.
- Use `-s` flag to hold the Shift key
```
python move.py [-s]
```

### Item crafting
- The materials must be selected before the execution
- Specify the limit with `-n` flag
- Use `-d` flag to discard all the crafted items
```
python craft.py [-n QUANTITY]
```

### Calculate the maximum friction brake you can use on your tackle
```
python calculate.py
```

### Harvest baits and refill food/comfort automatically
- Start a harvesting loop without moving or fishing
- The control panel will be opened constantly to save the power usage 
```
python harvest.py
```

## Troubleshooting
- The latest update is buggy, how to roll it back to previous version?
  - type `git reset HEAD^` in your terminal
- How to exit the program?
  - Use `Ctrl + C` to send a KeyboardInterrupt signal
- Failed to exit the program?
  - The Shift key might have been pressed down, press again to release it, then type `Ctrl + C` as usual
- Rod not getting lifted after the retrieval is finished?
  - Change the game resolution until the `validation.py` is pass
  - Lower the value of `spool_icon_confidence` in `config.ini`
  - Keep away from light sources, e.g., boat headlights in Norwegian Sea

## Roadmap
- [x] Improve logging messages
- [x] Customizable keybinds and number of bottom fishing rods
- [ ] Boat ticket auto-renewal
- [ ] Spool Recognition for rainbow line
- [ ] Retrieval with lifting
- [ ] Switch water layer automatically
- [ ] Semi-automatic trolling
- [ ] Spod rod recast
- [ ] Wakey rig
- [ ] Carp fishing
- [ ] Snag detection

## License
RussianFishing4Script is licensed under the [GNU General Public License version 3](LICENSE).

## Contributing 
Any contribution, bug report, or idea about new features is welcome.

## Contact me
Email: dereklee0310@gmail.com 