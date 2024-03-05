## About the Project
A simple bot for AFKing Russian Fishing 4, supporting spin, bottom and marine fishing.  
[文字教程](中文版教程.md)  
[視頻教程](https://www.youtube.com/watch?v=znLBYoXHxkw)

## 3/5 Patchnotes
- Improve fish catch plotting functionality
- Improve user guide

## Built With
- Python 3.11 
- PyAutoGUI

## Getting Started  
### Prerequisites
- If your in-game language is not English, change the language option in `config.ini`
- Enable Mouse ClickLock in Windows mouse settings and set the time before locking to "Long"  
![ClickLock](/static/readme/clicklock.png)
- To let food/comfort auto refill works, add the tea and carrot to your  
  favorite items so that they can be selected through quick food selection menu  
![Favorites](/static/readme/favorites.png)

### Install
```
git clone https://github.com/dereklee0310/RussianFishing4Script
```
Or, download the repository and unzip it.

### Update to latest version
```
git pull
```

### Dependencies
```
.\setup.bat
```

### Configuration
To edit user profiles, refer to the guides and examples in `config.ini` that generated from `template.ini` automatically.  
To enable email notification, set your Gmail address and Google app password in `.env`


## Usage
- Move your character to the fishing spot before executing the script.
- Spin Fishing/Marine Fishing: Pick up the rod you want to use
- Bottom Fishing: Add the tackles you want to use to the quick selection slots and place  
them nearby to let the script access them via quick selection keys (1 ~ 3)

### 1. Change the current working directory
```
cd src
```

### 2. Validate spool Icon (optional)
- If you are using this script for the first time, 
  run this to check if the spool icon can be identified (The reel must be fully loaded)  
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
- Display help information
```
python app.py -h
```
## Other Useful Scripts
### Toggle/untoggle moving forward
- Press w to stop, press it again to continue.
- Press s to quit.
- Use `-s` flag to hold the Shift key
```
python move.py [-s]
```

### Crafting items
- The materials must be selected before the execution
- Specify the limit with `-n` flag
```
python make.py [-n QUANTITY]
```

### Calculate the maximum friction brake you can use on your tackle
```
python calculator.py
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
- Stuck at retrieving stage?
  - Change the game resolution until the `validation.py` is pass
  - Keep away from light sources, e.g., boat headlights in Norwegian Sea

## Roadmap
- [ ] Improve logging messages
- [ ] Semi-automatic trolling
- [ ] Spod rod recast
- [ ] Customizable keybinds and number of bottom fishing rods
- [ ] Wakey rig
- [ ] Carp fishing
- [ ] Snag detection

## License
RussianFishing4Script is licensed under the [GNU General Public License version 3](LICENSE).

## Contributing 
Any contribution, bug report, or idea about new features is welcome.  
You can also share your own profiles by creating a pull request on `template.ini`. 

## Contact me
Email: dereklee0310@gmail.com 
