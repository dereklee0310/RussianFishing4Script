<div align="center">

<h1 align="center">RF4S</h1>

<a target="_blank" href="https://opensource.org/license/gpl-3-0" style="background:none">
    <img src="https://img.shields.io/badge/License-GPL--3.0--only-blue.svg" style="height: 22px;" />
</a>
<!-- <a target="_blank" href="link_to_docs, tbd" style="background:none">
    <img src="https://img.shields.io/badge/docs-%23BE1B55" style="height: 22px;" />
</a> -->
<a target="_blank" href="link_to_docs, tbd" style="background:none">
    <img src="https://img.shields.io/badge/Gmail-D14d36?style=for-the-badge&logo=gmail&logoColor=white" style="height: 22px;" />
</a>
<a target="_blank" href="https://discord.gg/BZQWQnAMbY" style="background:none">
    <img src="https://img.shields.io/badge/discord-join-rf44.svg?labelColor=191937&color=6F6FF7&logo=discord" style="height: 22px;" />
</a>
</div>

## About the Project
A simple bot for Russian Fishing 4, supporting spin, bottom, marine, and float fishing.  

## tbd
**Please refer to `template.ini` to check newly added settings**

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
[Download][download] the repository and unzip it, or:
```
git clone https://github.com/dereklee0310/RussianFishing4Script
```

### Dependencies
```
cd "the path of the project"
.\setup.bat
```

## Usage
- Move your character to the fishing spot before executing the script
- Spin Fishing/Marine Fishing/Float fishing: Pick up the rod you want to use
- Bottom Fishing: Add the tackles you want to use to the quick selection slots, 
  cast them, and place them nearby to let the bot access them via shortcuts (1 ~ 3)

### 1. Change the current working directory
```
cd src
```

### 2. Execute the main script
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

## Configuration
- Please refer to the guides and examples in `template.ini` and edit your settings in `config.ini`  
- To enable email notification, set your Gmail address and Google app password in `.env`  
- Edit `SMTP_SERVER` in `.env` if you want to use SMTP server other than Gmail SMTP server

## Troubleshooting
- How to exit the program?
  - Type `Ctrl + C` in your terminal
- Failed to exit the program?
  - The Shift key might have been pressed down, press again to release it and type `Ctrl + C` as usual
- Rod not getting lifted after the retrieval is finished?
  - Change the game resolution until the `validation.py` is pass
  - Lower the value of `spool_icon_confidence` in `config.ini`
  - Keep away from light sources or turn off the boat light

## License
[GNU General Public License version 3][license]

## Contributing
Any contribution, bug report, or idea about new features is welcome.

## Contact me
dereklee0310@gmail.com 

[integrity_guide]: integrity_guide.md
[clicklock]: /static/readme/clicklock.png
[favorite_food]: /static/readme/favorites.png
[favorite_lure]: /static/readme/favorites_2.png
[download]: https://github.com/dereklee0310/RussianFishing4Script/archive/refs/heads/main.zip
[spool_icon]: /static/readme/status.png
[license]: LICENSE