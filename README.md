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
- Set the time before button locking to "Long"  
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

### Change the Current Directory
```
cd src
```

### Validate Spool Icon (Optional)
- Run this to check if the spool icon can be identified (The reel must be fully loaded).  
![Status](/static/readme/status.png)
```
python validate.py
```

### Execute the Fishing Script
- If no additional command line argument is provided, it will display a list of available profiles for you to choose from.
```
python app.py <profile id>
```

## Other Useful Scripts
### Toggle moving (W key)
```
python move.py
```

### Making groundbaits/foods (The materials must be selected before the execution)
```
python make.py
```

### Calculate the maximum friction brake you can use on your tackle.
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
  - Keep away from light sources, e.g., boat headlights in Norwegian Sea.

## Roadmap
- [x] Marine fishing
- [x] Making lures/baits/groundbaits/foods
- [ ] Add command line arguments support
- [ ] Refactor bottom fishing
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

## Contributing 
Any kind of contribution and bug report is welcome.
## Contact me
Email: dereklee0310@gmail.com 