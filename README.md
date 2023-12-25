## About the Project
This is an experimental script for AFK fishing in Russian Fishing 4  

- Currently Support Strategies
  - Stable: Spin fishing
  - Not Stable: Marine Fishing/Carp Fishing (Might require manual intervention)
- Useful Scripts
  - Toggle Moving
  - Making Groundbaits/Foods
  - Calculating Maximum Friction Brake

## Built With
* Python 3.11 
  
## Getting Started
### Install
```
git clone https://github.com/dereklee0310/RF4_fishing_bot
```
### Prerequisites
* **Enable Mouse ClickLock in Windows**
* **Change game language to English**
* **The reel must be fully loaded**

To install dependencies and initialize user configurations:  
```
.\setup.bat
```

## Usage
Before executing the script, you must move to the desired fishing location and set up the rods.
- Bottom Fishing: Add the rods you want to use to the quick selection slots and place  
  them nearby to let the script access them via quick selection keys (1 ~ 3).
- Spin Fishing/Marine Fishing: Pick up the rod you want to use.

pick up the rod you want to use for spin fishing.  
### Change the current directory
```
cd src
```
### Execute the script
```
python app.py
```

### Useful Scripts
- Toggle moving (W key).
```
python move.py
```
- Making groundbaits/foods (Select the materials before executing the script).
```
python make.py
```
- Calculate maximum friction brake to use  based on the wear of reel and leader.
```
python calculator.py
```

## Troubleshooting
- How to exit the program?
  - Use Ctrl + C to send a KeyboardInterrupt signal.
- Failed to exit the program:
  - The Shift key might have been pressed down by the script.
  - Press the Shift key once to release it, then press Ctrl + C as usual.  
- Stuck at retrieving stage:  
  - Change resolution to 2560x1440 or 1600x900.
- Stuck at pulling stage:
  - Make sure your tackle is powerful enough for targeting fish, otherwise,
    you need to pull it manually.

## Roadmap
- [x] Marine Fishing
- [x] Making Groundbaits, Foods
- [ ] Carp Fishing
- [ ] Snag Detection
- [ ] Spooling Detection
- [ ] Wakey Rig
- [ ] Jig Step/Twitching/Stop and Go/Retrieval and Pause/Walk the Dog
- [ ] Reel Parameters Customization
- [ ] GUI
- [ ] Refactor code using FSM
- [ ] Revise setup.py

## Contributing 
Any kind of contribution and bug report is welcome.

## License
This project is not allowed to be used for commercial purposes.

## Contact
Author: Derek Lee  
Gmail: dereklee0310@gmail.com 