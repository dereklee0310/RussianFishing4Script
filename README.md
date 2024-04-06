## About the Project
A simple fishing bot for Russian Fishing 4, supporting spin, bottom and marine fishing.  
- [Discord](https://discord.gg/BZQWQnAMbY)
- [文字教程](中文版教程.md)

## 4/6 Patchnotes
- Added new language options: zh-TW and zh-CN
- Fixed [#issue16](https://github.com/dereklee0310/RussianFishing4Script/issues/16) 
- Fixed a potential perma-stuck bug in tackle resetting plase
- Fixed bug where the script would start pirking without closing the reel if the fish  
  was hooked and immediately escaped during sinking phase

## Built With
- Python 3.11 
- PyAutoGUI

## Getting Started  
### Prerequisites
- Set the language in `config.ini` and change your in-game language
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
Edit `SMTP_SERVER` in `.env` if you want to use SMTP server other than GMAIL SMTP (default).
E.g., Change it to `smtp.qq.com` if QQ mail is used.

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
Here are some examples of how to execute the script with different arguments (not all of them are listed):
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
python app.py -p 3 -c -e
```
- Release unmarked fish, enable hunger and comfort refill, and plot a catch/hour chart after it's terminated
```
python app.py -m -r -P
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

### Harvest baits and refill hunger and comfort automatically
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
[GNU General Public License version 3](LICENSE)

## Contributing
Any contribution, bug report, or idea about new features is welcome.

## Contact me
Email: dereklee0310@gmail.com 