**[[中文版]][installation]**
## Installation
### Approach 1: Clone via Git
```
git clone https://github.com/dereklee0310/RussianFishing4Script.git
cd RussianFishing4Script
.\setup.bat
```
> [!IMPORTANT] 
> Git must be installed on your system.
### Approach 2: Manual Download
1. [Download this repositorydownloadDownload].
2. Right-click `RussianFishing4Script-main.zip` and select "Extract here".
3. Open the extracted folder (`RussianFishing4Script-main`) and double-click `setup.bat` to install dependencies.
> [!TIP] 
> Create a virtual environment to avoid version conflicts if you already have Python installed.

> [!WARNING] 
> The download path cannot contain non-English characters.

## Environment Setup
### Enable Mouse ClickLock
- Go to Windows Mouse Settings > Enable **[Mouse ClickLock][clicklock]**.
- Set the time before locking to "Long".
### Language
- Confirm your game language matches the language setting in config.yaml (default is "EN").
### Display
- Set both system and in-game interface scales to "1x".
- Use "window mode" or "borderless windowed" for the game window mode.
### Spool Detection
- By default, the bot checks the status of the spool (red box) for retrieval detection.  
  The spool must be filled with fishing line so the bot can decide whether the retriaval is finished.
- If you have rainbow line equiped, use `-R` option to detect meter instead (green box) for better accuracy. 
- Please refer to [configuration guide][configuration] to see how to use launch options.
  
![status]

[installation]: /docs/zh-TW/INSTALLATION.md
[download]: https://github.com/dereklee0310/RussianFishing4Script/archive/refs/heads/main.zip
[configuration]: /docs/en/CONFIGURATION.md
[clicklock]: /static/readme/clicklock.png
[status]: /static/readme/status.png