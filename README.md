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
> Join the [Discord server][discord] if you want to suggest new features, report bugs or get help on how to use the script.


## Getting Started
### Prerequisites
Download and install **[Python 3.12.*][python]**.  

> [!IMPORTANT] 
> Ensure the **"Add Python to PATH"** option is selected during installation.  

> [!WARNING] 
> Python 3.13+ are not supported.
### Installation
See **[INSTALLATION][installation]**.
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
1. Open cmd/PowerShell
2. Navigate into the project directory and run the script with default configuration. Type `CTRL-C` to quit.
```
cd "path\to\the\project"
python tools\main.py
```
> [!TIP]
> `path\to\the\project` is the directory where you placed the files after cloning or extracting the project.  
> ![path]

> [!TIP]
> See **[CONFIGURATION][configuration]** for advanced usage and configuration options.

## Tools
### Craft items
Select materials before you run it, press `Ctrl-C` to quit.
```
python tools\craft.py
```
### Harvest baits
Press `Ctrl-C` to quit.
```
python tools\harvest.py
```
### Toggle moving forward
Press `W`to pause, `S` to quit.
```
python tools\move.py
```
### Automate friction brake
Press `G` to reset, `H` to quit.
```
python tools\auto_friction_brake.py
```
### Calculate tackle's stats and friction brake
```
python tools\calculate.py
```

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
- Reduce the value of `SPOOL_CONFIDENCE` in `config.yaml`.
- Keep away from light sources or turn off the boat light.
</details>
<!-- ------------------------------- divide -------------------------------- -->
<details>
<summary>Script is running but nothing happen?</summary>

- Open cmd/Powershell as administrator and run it again.
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
[installation]: /docs/en/INSTALLATION.md
[configuration]: /docs/en/CONFIGURATION.md
[changelog]: /docs/en/CHANGELOG.md
[path]: /static/readme/path.png
[license]: /LICENSE