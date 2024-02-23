## About the Project
A simple script for AFKing Russian Fishing 4  

## Patchnotes
**Please read the README before running the latest version**  
- Improve: coffee drinking mechanism
- Improve: README and configuration guide
- Fix: Incorrect display of marked ratio
- Fix: plotting bug
- Add: Plotting option for catch per running/in-game hour
- Add: Maximum number of coffee to drink in a single battle against fish
- Add: spooling detection for retrieving stage
- Change: The flag for email sending has been renamed as `-e`

## Built With
* Python 3.11 
* PyAutoGUI
  
## Getting Started
### Install
```
git clone https://github.com/dereklee0310/RussianFishing4Script
```
### Prerequisites
- If your in-game language is not English, change the language option in `config.ini`
- Make sure that your tackles are powerful enough for the target fish species
- Enable Mouse ClickLock in Windows mouse settings and set the time before locking to "Long"  
![ClickLock](/static/readme/clicklock.png)
- To let the food/comfort refill functionality work, add the tea and carrot to your  
  favorite items so that it can be selected through quick food selection menu  
![Favorites](/static/readme/favorites.png)

### Dependencies
```
.\setup.bat
```

## Usage
Move your character to the fishing spot before executing the script.
- Spin Fishing/Marine Fishing: Pick up the rod you want to use
- Bottom Fishing: Add the tackles you want to use to the quick selection slots and place  
them nearby to let the script access them via quick selection keys (1 ~ 3)

### 1. Change the current working directory
```
cd src
```

### 2. Validate spool Icon (optional)
- Run this to check if the spool icon can be identified (The reel must be fully loaded)  
![Status](/static/readme/status.png)
```
python validate.py
```

### 3. Execute the main script (examples)
- Display a list of available user profiles and run with the default settings
```
python app.py
```
- Display a list of available user profiles and set the number of fishes in keepnet to 32 (68 fishes to catch before being stopped)
```
python app.py -n 32
```
- Select profile 3, drink the coffee while battling with the fish, and send an email to yourself after it's terminated
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
### Toggle moving forward
- Press w to stop, press it again to continue.
- Press s to quit.
```
python move.py
```

### Crafting groundbaits/baits/foods until materials run out
- The materials must be selected before the execution
```
python make.py
```

### Calculate the maximum friction brake you can use on your tackle
```
python calculator.py
```

### Harvest baits and refill food/comfort automatically without fishing
```
python harvest.py
```

## Troubleshooting
- How to exit the program?
  - Use Ctrl + C to send a KeyboardInterrupt signal
- Failed to exit the program?
  - The Shift key might have been pressed down
  - Press again to release it, then type Ctrl + C as usual
- Stuck at retrieving stage?
  - Change the game resolution until the `validation.py` is pass
  - Keep away from light sources, e.g., boat headlights in Norwegian Sea

## Configuration
- Edit settings in `config.ini` and `.env`.  
- At the current state, the constantly changing `.env` file might lead to a conflicted `git pull`  
- Please use `git clone` to get the latest version and paste your user settings and profiles into `config.ini`.

## Roadmap
- [x] Line chart of fish captured time
- [x] Email notification
- [x] Refine configuration file 
- [x] Spooling detection
- [ ] Carp fishing
- [ ] Wakey rig
- [ ] Snag detection

## License
RussianFishing4Script is licensed under the [GNU General Public License version 3](LICENSE).

## Contributing 
Any contribution, bug report, and idea about new features is welcome.

## Contact me
Email: dereklee0310@gmail.com 
