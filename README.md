**[[中文版]][readme]**
<div align="center">

![RF4S][rf4s_logo]
<h1 align="center">RF4S: Russian Fishing 4 Script</h1>

**A simple Russian Fishing 4 fishing bot, supporting spin, bottom, marine, and float fishing modes.**

<a target="_blank" href="https://opensource.org/license/gpl-3-0" style="background:none">
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" style="height: 22px;" />
</a>
<a target="_blank" href="https://discord.gg/BZQWQnAMbY" style="background:none">
    <img src="https://img.shields.io/badge/discord-join-rf44.svg?labelColor=191937&color=6F6FF7&logo=discord" style="height: 22px;" />
</a>
<a target="_blank" href="http://makeapullrequest.com" style="background:none">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat" style="height: 22px;" />
</a>
<!-- <a target="_blank" href="https://github.com/pylint-dev/pylint" style="background:none">
    <img src="https://img.shields.io/badge/linting-pylint-yellowgreen" style="height: 22px;" />
</a> -->
<!-- <a target="_blank" href="https://github.com/psf/black" style="background:none">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" style="height: 22px;" />
</a> -->
<!-- <a target="_blank" href="link_to_docs, tbd" style="background:none">
    <img src="https://img.shields.io/badge/docs-%23BE1B55" style="height: 22px;" />
</a> -->  

![Python badge][python_badge]
![Windows badge][windows_badge]

</div>

> [!TIP]
> Join our [Discord server][discord] if you want to suggest new features, report bugs or get help on how to use the script.


## Getting Started
### Prerequisites
**[Python 3.12.*][python]** is required if you want to run the Python code instead of the executable file.
> [!WARNING] 
> Python 3.13+ are not supported.

### Installation
#### Executable File
Download `rf4s.zip` from [Releases][releases] and unzip it.  
#### Python Code and Environment (for developer)
```
git clone https://github.com/dereklee0310/RussianFishing4Script.git
cd RussianFishing4Script
.\setup.bat
```
> [!WARNING] 
> The download path cannot contain non-English characters.

### Environment Setup
#### Language
- Confirm your game language matches the language setting in `config.yaml` ("en" by default).
#### Display
- Set both system and in-game interface scales to "1x".
- Set game window mode to "window mode" or "borderless windowed".
#### Spool Detection
- By default, the bot monitors the spool (red box) to detect retrieval progress.  
  Ensure the spool is fully loaded with fishing line for accurate detection of retrieval completion.
- If using a rainbow line, enable the `-R` flag to switch detection to the meter (green box) for better precision.
- Please refer to **[CONFIGURATION][configuration]** to see how to use it.

![status]

## Usage
### Before you start...
#### Bottom Mode
Add your rods to quick selection slots, cast and place them nearby so the bot can access them via shortcuts (1 ~ 3).
#### Other Modes 
Pick up the rod you want to use.
> [!NOTE]
> Currently, only bottom mode support multiple rods.

### Let's Run it!
#### Executable File
Double-click the executable file to run it.
#### Python Code (for developer)
```
cd "path\to\the\project"
python tools\main.py
```
> [!TIP]
> See **[CONFIGURATION][configuration]** for advanced usage and configuration options.

## Features
| Feature                  | Functionality                                            |
| ------------------------ | -------------------------------------------------------- |
| Fishing Bot              | Main script                                              |
| Craft Items              | Automatically harvest baits while staying idle           |
| Harvest Baits            | Stay idle and harvest baits automatically                |
| Toggle Moving Forward    | Automatically presses `W` (or `Shift + W` for sprinting) |
| Automate Friction Brake  | Adjust the friction brake automatically                  |
| Calculate Tackle's Stats | Calculate the real drag or load capacity of the loadout  |

## Troubleshooting
<details>
<summary>How to stop the script?</summary>

- Type `Ctrl-C` in your terminal. 
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
- Reduce the value of `SPOOL_CONFIDENCE` in `config.yaml`.
- Avoid bright light sources (e.g., direct sunlight) or turn off the boat’s onboard lights.
</details>
<!-- ------------------------------- divide -------------------------------- -->
<details>
<summary>Script is running but nothing happen?</summary>

- Run the script as administrator.
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

[readme]: /docs/zh-TW/README.md
[rf4s_logo]: /static/readme/RF4S.png
[python_badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[windows_badge]: https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white

[discord]: https://discord.gg/BZQWQnAMbY
[python]: https://www.python.org/downloads/
[releases]: https://github.com/dereklee0310/RussianFishing4Script/releases
[status]: /static/readme/status.png
[configuration]: /docs/en/CONFIGURATION.md
[changelog]: /docs/en/CHANGELOG.md
[license]: /LICENSE