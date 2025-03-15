**[[中文版]][README]**
<div align="center">

![RF4S][RF4S logo]
<h1 align="center">RF4S: Russian Fishing 4 Script</h1>

**A simple fishing bot for Russian Fishing 4, supporting spin, bottom, marine, and float fishing.**

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

> [!TIP]
> Join the [Discord server][Discord] if you want to suggest new features, report bugs or get help on how to use the script.


## Getting Started  
### Prerequisites
Download and install **[Python 3.12][Python]**.  

> [!IMPORTANT] 
> Ensure Python is added to `PATH` during installation.

> [!WARNING] 
> Python 3.13+ is not supported.

### Installation
1. Open cmd or powershell
2. Clone the repository and navigate into the project directory:
```
git clone https://github.com/dereklee0310/RussianFishing4Script.git
cd RussianFishing4Script
```
> [!TIP]
> If you don't have git, **[download this repository][Download]** and unzip it.

> [!WARNING] 
> The download path cannot contain non-English characters.

### Dependencies
Run the setup script to install required packages and create the default configuration file:
```
setup.bat
```

> [!TIP] 
> Create a virtual environment to avoid version conflicts if you already have Python installed.

### Setup
- Enable **[Mouse ClickLock][Clicklock]** in Windows mouse settings and set the time before locking to "Long"
- Make sure your game language is the same as the setting in `config.yaml` (default is `EN`).
- Set interface scale to `1x`.
- Set display mode to `window mode` or `borderless windowed`.
- Make sure your reel is fully loaded, or equip a rainbow line and use `-R` flag.
- Add tea, carrot, and coffee to your **[favorites][Favorite food]** if you want to use `-r` or `-c` flag.
- To use a feature that replaces an item for you, you must add items to your **[favorites][Favorite lure]** for replacement.

## Usage
### Before you start...
- Move your character to the fishing spot before running the script
- For Spin/Marine/Float/Wakey Rig Fishing: Pick up the rod you want to use.
- For Bottom Fishing:
    - Add tackles to quick selection slots.
    - Cast them and place them nearby so the bot can access them via shortcuts (1 ~ 3).
> [!NOTE]
> Currently, only bottom fishing mode support multiple rods.

### Let's Run it!
Run the script with default configuration:
```
python tools\main.py
```
For more advanced usage, see **[configuration guide][Configuration guide]**.
> [!IMPORTANT]
> Navigate to into the project directory first before you run the command if you want to run it in a new terminal window.
> ```
> cd "path\to\your\project\RussianFishing4Script"
> ```

> [!NOTE]
> The script stops once the keepnet is full. Stop it manually by typing `Ctrl-C` in your terminal. 

## Tools
### Craft Items
**Craft items until materials run out (press `Ctrl-C` to quit):**
```
python tools\craft.py
```
**Craft 10 items:**
```
python tools\craft.py -n 10
```
**Discard crafted groundbaits:**
```
python tools\craft.py -d
```
> [!IMPORTANT]
> Select materials before you run the script.
### Harvest Baits
**Harvest baits (press `Ctrl-C` to quit):**
```
python tools\harvest.py
```
**Replenish hunger and comfort while harvesting:**
```
python tools\harvest.py -r
```
**Open control panel while waiting (reduces power consumption):**
```
python tools\harvest.py -s
```
### Toggle moving forward
**Toggle Auto-Move (`W`to pause, `S` to quit):**
```
python tools\move.py
```
**Move while holding Shift:**
```
python tools\move.py -s
```

### Automate Friction Brake
**Automate Friction Brake (`G` to reset, `H` to quit):**
```
python tools\auto_friction_brake.py
```

### Calculate tackle's stats and friction brake
**Show your reel's real drag and leader's real load capacity based on wear:**
```
python tools\calculate.py
```

## Configuration
See **[Configuration guide][Configuration guide].**

## Troubleshooting
<details>
<summary>How to stop the script?</summary>

- Type `Ctrl-C` in your terminal. 
</details>
<!-- ------------------------------- divide -------------------------------- -->
<details>
<summary>Can't stop the script?</summary>

- Some keys might have been pressed down (e.g. `Ctrl`, `Shift`, `Mouse button`, etc.),  
  press them again to release it and type `Ctrl-C` as usual.
</details>
<!-- ------------------------------- divide -------------------------------- -->
<details>
<summary>Stuck at casting 128%?</summary>

- Check that the game language and script language settings are the same.
- Make sure your reel is fully loaded, or equip a rainbow line and use `-R` flag. 
</details>

<!-- ------------------------------- divide -------------------------------- -->
<details>
<summary>Didn't lift the rod after the retrieval is finished?</summary>

- Make sure your reel is fully loaded, or equip a rainbow line and use `-R` flag. 
- Change the game window size.
- Lower the value of `SPOOL_CONFIDENCE` in `config.yaml`.
- Keep away from light sources or turn off the boat light.
</details>
<!-- ------------------------------- divide -------------------------------- -->
<details>
<summary>Script is running but nothing happen?</summary>

- Open a new terminal window as administrator and run it again.
</details>
<!-- ------------------------------- divide -------------------------------- -->

## Changelog
See **[changelog][Changelog].**

## License
**[GNU General Public License version 3][License]**

## Contributing
Any contribution, bug report, or idea about new features is welcome.

## Contact me
dereklee0310@gmail.com 

[RF4S logo]: static/readme/RF4S.png
[Python badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Windows badge]: https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white

[README]: /docs/zh-TW/README.md
[Discord]: https://discord.gg/BZQWQnAMbY
[Python]: https://www.python.org/downloads/
[Download]: https://github.com/dereklee0310/RussianFishing4Script/archive/refs/heads/main.zip
[Clicklock]: /static/readme/clicklock.png
[Favorite food]: /static/readme/favorites.png
[Favorite lure]: /static/readme/favorites_2.png
[Configuration guide]: /docs/en/CONFIGURATION.md
[Changelog]: /docs/en/CHANGELOG.md

[License]: /LICENSE