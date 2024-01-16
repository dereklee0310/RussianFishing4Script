## About the Project
A simple script for AFKing Russian Fishing 4  
- Spin fishing
- Bottom fishing
- Marine fishing
- Toggle moving
- Making lures/baits/groundbaits/foods
- Calculate maximum friction brake

## Built With
* Python 3.11 
  
## Getting Started
### Install
```
git clone https://github.com/dereklee0310/RussianFishing4Script
```
### Prerequisites
- If your in-game language is not English, change the language option in `config.ini`.
- Make sure that your tackles are powerful enough for the target fish species.
- Enable Mouse ClickLock in Windows  
- Set the time before locking to "Long"  
![ClickLock](/static/readme/clicklock.png) 

### Dependencies
```
.\setup.bat
```

## Usage
Before executing the script, you must move to the desired fishing location and set up the tackles.
- Bottom Fishing: Add the tackles you want to use to the quick selection slots and place  
them nearby to let the script access them via quick selection keys (1 ~ 3).
- Spin Fishing/Marine Fishing: Pick up the rod you want to use.

### 1. Change the Current Working Directory
```
cd src
```

### 2. Validate Spool Icon (Optional)
- Run this to check if the spool icon can be identified (The reel must be fully loaded).  
![Status](/static/readme/status.png)
```
python validate.py
```

### 3. Execute the Main Fishing Script
- By default (no arguments), it will display a list of available profiles, then start fishing with empty keepnet and keep all the fishes you caught.
```
python app.py [-h] [-p PID] [-n FISH_COUNT] [-a] [-m]
```
- Display help information
```
python app.py -h
```
## Other Useful Scripts
### Toggle moving
- Press w to stop, press it again to continue.
- Press s to quit.
```
python move.py
```

### Making groundbaits/foods 
- The materials must be selected before the execution.
```
python make.py
```

### Calculate the maximum friction brake you can use
```
python calculator.py
```

## Troubleshooting
- How to exit the program?
  - Use Ctrl + C to send a KeyboardInterrupt signal.
- Failed to exit the program?
  - The Shift key or a mouse button might have been pressed down by the script.
  - Press the button to release it, then type Ctrl + C as usual.  
- Stuck at retrieving stage?
  - Change the game resolution until the `validation.py` is pass.
  - Keep away from light sources, e.g., boat headlights on Norwegian Sea's boat.

## Roadmap
- [x] Marine fishing
- [x] Making lures/baits/groundbaits/foods
- [x] Add command line arguments support
- [x] Refactor bottom fishing
- [ ] Carp fishing
- [ ] Snag detection
- [ ] Spooling detection
- [ ] Wakey rig
- [ ] Jig step/Twitching/Stop and go/Retrieval and pause/Walk the dog
- [ ] Reel parameters customization
- [ ] GUI
- [ ] Refactor code using FSM
- [ ] Revise setup.py

## License
RussianFishing4Script is licensed under the [GNU General Public License version 3](LICENSE).

## Contributing 
Any kind of contribution and bug report is welcome.
## Contact me
Email: dereklee0310@gmail.com 
