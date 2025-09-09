**[[中文版]][readme_zh-TW]** **[[Русская версия]][readme_ru]**
<div align="center">

![RF4S][rf4s_logo]
<h1 align="center">RF4S: Russian Fishing 4 Script</h1>

**A simple Russian Fishing 4 fishing bot, supporting spin, bottom, marine, and float fishing modes.**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://opensource.org/license/gpl-3-0)
[![Discord](https://img.shields.io/badge/discord-join-rf44.svg?labelColor=191937&color=6F6FF7&logo=discord)](https://discord.gg/BZQWQnAMbY)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](http://makeapullrequest.com)
[![Python: 3.10 | 3.11 | 3.12](https://img.shields.io/badge/python-3.10_%7C_3.11_%7C_3.12-blue)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

<!-- <a target="_blank" href="https://github.com/pylint-dev/pylint" style="background:none">
    <img src="https://img.shields.io/badge/linting-pylint-yellowgreen" style="height: 22px;" />
</a> -->
<!-- <a target="_blank" href="https://github.com/psf/black" style="background:none">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" style="height: 22px;" />
</a> -->
<!-- <a target="_blank" href="link_to_docs, tbd" style="background:none">
    <img src="https://img.shields.io/badge/docs-%23BE1B55" style="height: 22px;" />
</a> -->  

</div>

> [!TIP]
> Join our [Discord server][discord] if you want to suggest new features, report bugs or get help on how to use the script.


## Installation
> [!WARNING] 
> The download path cannot contain non-English characters.
### Executable File (.exe)
Download `rf4s.zip` from [Releases][releases]. 
> [!WARNING] 
> The executable file is more likely to be detected. Consider using Python to run it instead.  
> If you're not sure how to run it using Python, see **[INSTALLATION][installation]**.
### pip
```
git clone https://github.com/dereklee0310/RussianFishing4Script.git
cd RussianFishing4Script
pip install -r requirements.txt
```
> [!IMPORTANT] 
> Python 3.13+ is not supported, required versions: >=3.10,<=3.12.

### uv
```
git clone https://github.com/dereklee0310/RussianFishing4Script.git
cd RussianFishing4Script
uv sync
```

## Settings
### Windows Mouse ClickLock
If Windows Mouse ClickLock is enabled, set the time to long.  

![click_lock]
### Display
Set both system and in-game interface scales to "1x", and use "window mode" or "borderless windowed" for game window mode.
### Spool Detection
By default, the bot monitors the spool (red box) to detect retrieval progress.  
Ensure the spool is fully loaded with fishing line for accurate detection of retrieval completion.  
If using a rainbow line, enable the `-R` flag to switch detection to the meter (green box) for better precision.  
Please refer to **[CONFIGURATION][configuration]** to see how to use it.  

![status]

## Usage
### Bottom fishing
Add your rods to quick selection slots, cast and place them nearby so the bot can access them via shortcuts (1 ~ 3).
### Spin, marine, telescopic, etc.
Pick up the rod you want to use.
> [!NOTE]
> Currently, only bottom mode support multiple rods.
### Executable File (.exe)
Double-click to run it, or:
```
.\main.exe
```
### Python
```
python main.py
```
### uv
```
uv run main.py
```
> [!TIP]
> See **[CONFIGURATION][configuration]** for advanced usage and configuration options.

## Features
| Feature                  | Description                                              |
| ------------------------ | -------------------------------------------------------- |
| Fishing Bot              | Auto fishing bot                                         |
| Craft Items              | Craft baits, groundbaits, lures, etc                     |
| Moving Forward           | Toggle `W` (or `Shift + W` for sprinting)                |
| Harvest Baits            | Stay idle and harvest baits automatically                |
| Auto Friction Brake      | Adjust the friction brake automatically                  |
| Calculate Tackle's Stats | Calculate the tackle's stats and friction brake to use   |

## Troubleshooting
<details>
<summary>Windows Defender detect it as a malware?</summary>

- It's a false postive, see [this][malware]. 
</details>
<!-- ------------------------------- divide -------------------------------- -->
<details>
<summary>Can't stop the script?</summary>

- Some keys might have been pressed down (e.g. `Ctrl`, `Shift`, `Mouse button`, etc.).  
  Press them again to release it and type `Ctrl-C` as usual.
</details>
<!-- ------------------------------- divide -------------------------------- -->
<details>
<summary>Stuck at casting 12x%?</summary>

- Check that the game language and script language settings are the same.
- Make sure your reel is fully loaded, or equip a rainbow line and use `-R` flag. 
</details>

<!-- ------------------------------- divide -------------------------------- -->
<details>
<summary>Didn't lift the rod after the retrieval is finished?</summary>

- Make sure your reel is fully loaded, or equip a rainbow line and use `-R` flag. 
- Resize the game window.
- Reduce the value of `BOT.SPOOL_CONFIDENCE` in `config.yaml`.
- Avoid bright light sources (e.g., direct sunlight) or turn off the boat’s onboard lights.
</details>
<!-- ------------------------------- divide -------------------------------- -->
<details>
<summary>Bot is running but nothing happen?</summary>

- Run it as administrator.
</details>
<!-- ------------------------------- divide -------------------------------- -->

## Changelog
See **[CHANGELOG][changelog].**

## License
**[GNU General Public License version 3][license]**

## Contributing
Any contribution, bug report, or idea about new features is welcome.

## Contact me
dereklee0310@gmail.com 

[readme_zh-TW]: /docs/zh-TW/README.md
[readme_ru]: /docs/ru/README.md
[rf4s_logo]: /static/readme/RF4S.png
[python_badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[windows_badge]: https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white
[click_lock]: /static/readme/clicklock.png
[malware]: https://nuitka.net/user-documentation/common-issue-solutions.html#windows-virus-scanners

[discord]: https://discord.gg/BZQWQnAMbY
[python]: https://www.python.org/downloads/
[releases]: https://github.com/dereklee0310/RussianFishing4Script/releases
[status]: /static/readme/status.png
[configuration]: /docs/en/CONFIGURATION.md
[changelog]: /docs/en/CHANGELOG.md
[license]: /LICENSE
[installation]: /docs/en/INSTALLATION.md