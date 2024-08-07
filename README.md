<div align="center">

![RF4S][RF4S logo]
<h1 align="center">RF4S</h1>

**A simple bot for Russian Fishing 4, supporting spin, bottom, marine, and float fishing.**

<a target="_blank" href="https://opensource.org/license/gpl-3-0" style="background:none">
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" style="height: 22px;" />
</a>
<a target="_blank" href="https://discord.gg/BZQWQnAMbY" style="background:none">
    <img src="https://img.shields.io/badge/discord-join-rf44.svg?labelColor=191937&color=6F6FF7&logo=discord" style="height: 22px;" />
</a>
<a target="_blank" href="http://makeapullrequest.com" style="background:none">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat" style="height: 22px;" />
</a>
<a target="_blank" href="https://github.com/pylint-dev/pylint" style="background:none">
    <img src="https://img.shields.io/badge/linting-pylint-yellowgreen" style="height: 22px;" />
</a>
<a target="_blank" href="https://github.com/psf/black" style="background:none">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" style="height: 22px;" />
</a>
<!-- <a target="_blank" href="link_to_docs, tbd" style="background:none">
    <img src="https://img.shields.io/badge/docs-%23BE1B55" style="height: 22px;" />
</a> -->  

![Python badge][Python badge]
![Windows badge][Windows badge]

</div>

## [Release Notes][Release notes]
> [!TIP]
> Join us on our [Discord server][Discord] to get the latest news about the project.

## Built With
- Python 3.11
- PyAutoGUI

## Getting Started  
### Prerequisites
- [Python3.10+][Python]


### Install
[Download][Download] the repository and unzip it, or:
```
git clone https://github.com/dereklee0310/RussianFishing4Script
```

### Dependencies
```
cd "the path of the project"
.\setup.bat
```
> [!TIP]
> If you already have Python installed on your computer, create a virtual environment to prevent version conflicts.

## Usage

### Prerequisites
- Enable **[Mouse ClickLock][Clicklock]** in Windows mouse settings and set the time before locking to "Long"
- Change game language to "English"
- Set interface scale to "1x"
- Set display mode to "borderless windowed" or "window mode"
- Make sure your reel is fully loaded, or use `-R`  along with a rainbow line when executing the main script
- Add tea, carrot, and coffee to your **[favorites][Favorite food]** so that they can be selected through quick food selection menu
- To enable broken lure replacement, the lures for replacement must also be added to **[favorites][Favorite lure]**
> [!IMPORTANT]
> Please follow the instructions above step by step, otherwise, you may encounter unexpected errors at runtime
### Before you start...
- Move your character to the fishing spot before executing the script
- Spin/marine/float/wakey rig fishing: Pick up the rod you want to use
- Bottom Fishing: Add the tackles you want to use to the quick selection slots, 
  cast them, and place them nearby to let the bot access them via shortcuts (1 ~ 3)
> [!NOTE]
> Currently, We only support single rod for float fishing and wakey rig fishing.

> [!IMPORTANT]
> The value of `window_size` in `config.ini` must be set to the game window size correctly for float fishing.  

### 1. Change the current working directory
```
cd "the path of the project"
cd src
```

### 2. Execute the main script
Here are some examples of how to execute the script with different arguments:
- Run with default settings
```
python app.py
```
> [!WARNING]
> If the script doesn't focus on the game window automatically, 
> you might need to run your terminal as administrator.

- Display help information
```
python app.py -h
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
- Specify the number of items to craft with `-n QUANTITY` 
- Use `-d` to discard all the crafted items
```
python craft.py [-d] [-n QUANTITY]
```
> [!IMPORTANT]
> The materials must be selected before the execution.

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
- Please refer to the guides and examples in **[template.ini][Template]** 
  and edit your settings in **[config.ini][Config]**  
- Set the `language` setting in **[config.ini][Config]** 
  and **[add missing images][Integrity guide]** if the integrity check failed.
- To enable email notification, set your Gmail address and Google app password in `.env`  
- Edit `SMTP_SERVER` in `.env` if you want to use SMTP server other than Gmail SMTP server

## Troubleshooting
**How to exit the program?**
- Type `Ctrl + C` in your terminal.
   
**Cannot quit the program?**
- The Shift key might have been pressed down, press again to release it and type `Ctrl-C` as usual.  

**Rod not getting lifted after the retrieval is finished?**
- Fill up your reel, or use a rainbow main line with `-R` flag
- Change the game window size
- Lower the value of `retrieval_detect_confidence` in `config.ini`
- Keep away from light sources or turn off the boat light

## License
[GNU General Public License version 3][license]

## Contributing
Any contribution, bug report, or idea about new features is welcome.

## Contact me
dereklee0310@gmail.com 

[RF4S logo]: static/readme/RF4S.png

[Python badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Windows badge]: https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white

[Release notes]: release_notes.md
[Discord]: https://discord.gg/BZQWQnAMbY
[Python]: https://www.python.org/downloads/
[Download]: https://github.com/dereklee0310/RussianFishing4Script/archive/refs/heads/main.zip
[Clicklock]: /static/readme/clicklock.png
[Favorite food]: /static/readme/favorites.png
[Favorite lure]: /static/readme/favorites_2.png
[Template]: template.ini
[Config]: config.ini
[Integrity guide]: integrity_guide.md

[license]: LICENSE