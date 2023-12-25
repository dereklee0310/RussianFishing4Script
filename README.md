## About the Project
This is an experimental script for AFK fishing in Russian Fishing 4  

- Currently Support Strategies
  - Stable: Spin Fishing, Bottom Fishing
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

### Change the Current Directory
```
cd src
```

### Validate Spool Icon (Optional)
- Run this to check if the spool icon can be identified.  
![image](/static/status.png)
```
python validate.py
```

### Execute the Fishing Script
- If no additional command line argument is provided, it will show a list of available  
  profiles to choose from.
```
python app.py <profile id>
```

### Useful Scripts
- Toggle moving (W key).
```
python move.py
```
- Making groundbaits/foods (The materials must be selected before the execution).
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
  - Use the script mentioned above to validate the spool icon.
  - Change resolution to 2560x1440 or 1600x900.
  - Avoid stading in front of the boat headlights in Norwegian Sea.
- Stuck at pulling stage:
  - Make sure your tackle is powerful enough for targeting fish, otherwise,
    you might need to pull it manually.

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