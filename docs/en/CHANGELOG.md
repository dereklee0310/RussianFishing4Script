**[[中文版]][CHANGELOG]**

## TBD
- Increase minimum gray scale level
- Fix pull time out bug
- Fix bump version and uv.lock bug
- Fix telescopic/bolognese skip cast bug
- Fix bottom harvest bug
- Fix drink coffee while retrieving bug
- Fix drink coffee during pulling bug
- Add and finetune profiles in config.yaml

## 0.6.2 (2025-08-02)

### 🐛 Bug Fixes
- Fixed an issue where the bot would get stuck if the pull phase timed out.

### 🔧 Improvements
- Increased the default value of `HOOK_DELAY` to help prevent fish from escaping.

## 0.6.1 (2025-08-02)
### 🔧 Improvements
- Increased the check frequency for the friction brake bar to improve responsiveness.


## 0.6.0 (2025-08-02)

### 🆕 New Features
- Added "Craft Items" feature to automate crafting of in-game items.
- Added "Calculate Tackle's Stats" feature to compute tackle's stats and recommend the appropriate friction brake based on wear levels.
- Added support for Telegram notifications to alert users of key events such as rare catches and received gifts.
- Added compatibility with `uv` as a faster alternative to `pip` for dependency management.
- Added a dedicated log file at `/logs/.log` to record runtime activity and errors for easier troubleshooting.
- Profiles now support a `DESCRIPTION` field, allowing users to document their purpose or strategy directly in the config.
- Introduced `BOT.CLICK_LOCK` to support users who have Windows Mouse ClickLock enabled.
- Added `BOT.KEEPNET.BYPASS_TAGS` to always keep fish that match specific tags (e.g., trophy, rare trophy).
- Added tracking and recording of collected cards and gifts.
- Added optional screenshot notifications for fish catches, card discoveries, and gift pickups.
- Added delay time jitter to introduce small random variations in actions, improving human-like behavior.
- Implemented full keepnet protection: the bot now exits safely even if the fish count is misconfigured.
- Added the `-R [{0,5}]` option, allowing users to choose between 0m or 5m detection for fishing line retrieval end.
- Added a compile script to simplify setup for both `venv` and `uv` users.
- Added a keyboard shortcut to pause and restart the bot for easier runtime control.
- Added logging of sink time during `pirk` and `elevator` fishing modes for better performance analysis.

### 🔧 Improvements
- Improved UI design for a more intuitive and user-friendly experience.
- Reworked the configuration file structure for better clarity, consistency, and ease of use.
- Enhanced fishing line retrieval control flow for smoother and more reliable operation.
- The control panel now closes automatically at startup to reduce distractions.
- Gear ratio is now reset immediately after casting, instead of during the pulling phase.
- Bottom fishing mode now harvests baits after checking the rod to improving efficiency.
- Increased frequency of energy checks during retrieval to ensure timely coffee consumption.
- The bot now closes the game when `BOT.STAT.COFFEE_LIMIT` is reached to prevent overuse.
- The `-d/--data` flag now saves the result table as a JSON file in the `/logs` directory for easy export and analysis.
- When both hunger and comfort are low, the bot will now randomly consume either tea or carrots.
- Increased check frequency on the friction brake bar.

### 🐛 Bug Fixes
- Fixed an issue where the terminal would close immediately after the user stops the bot.
- Fixed `-b/--bite`: it now takes a screenshot when a fish bites, not when the rod is cast.
- Fixed arrow key input not working correctly in trolling mode.
- Fixed bolognese fishing mode attempting to pull the fish before fully retrieving the line.
- Fixed `-DM/--dry-mix` not functioning on spod rods.
- Fixed a bug where `-d/--data` not functioning on executable file.

### 🗃️ Deprecations
- Deprecated earlier versions of configuration files.
- Removed `auto/on/off` options for `POST_ACCELERATION`; now accepts only `true` or `false`.
- Discontinued support for zh-TW and zh-CN game languages.
- Removed the "alarm" feature.
- Removed spool and file integrity checks at startup.

## 0.5.3 (2025-06-21)

### 🐛 Bug Fixes
- Fixed an issue where the Discord notification feature was not functioning properly.  
- Resolved a bug that prevented the script from displaying results after the Keepnet was full.  
- Fixed an issue where the script did not exit correctly when `-FB` mode was enabled.  
- Addressed a bug that caused the script to fail to quit when receiving a gift.  
- Removed the "Craft Items" feature due to potential ban risks.  
- Temporarily removed the "Calculate Tackle's Stats" feature as it was providing misleading results.

### 🔧 Improvements
- Added a build script to compile the source code into an executable file for easier distribution.

## 0.5.2 (2025-06-08)

### 🐛 Bug Fixes
- Fixed an issue where the `-s` and `-d` flags were not functioning correctly when running the script via executables.
- Fixed a bug causing the script to exit unexpectedly when using `telescopic` mode.
- Fixed a bug where the script would fail to put down the tackle if it was unable to fetch the fish.

### 🔧 Improvements
- Integrated all features into a single executable.


## 0.5.1 (2025-06-08)

### 🐛 Bug Fixes
- Fixed an issue preventing the script from handling multiple gifts properly.  
- Resolved a bug affecting tea drinking functionality due to special characters in rod names.  
- Fixed an unexpected termination issue when using `telescopic/bolognese` mode.

### 🔧 Improvements
- Executables are now available for download in the [Releases](https://github.com/dereklee0310/RussianFishing4Script/releases) section.

## 0.5.0 (2025-06-06)

### 🆕 New Features
- **Discord Webhook Integration**: Added support for termination notifications via Discord webhooks. Set it with `NOTIFICATION.DISCORD_WEBHOOK_URL`.
- **Enhanced Tag Detection**: Added precise colored tag identification. Configure filtering with `KEEPNET.TAGS`.
- **Tag Filtering in Screenshots**: Integrated tag detection into screenshots. Use `SCRIPT.SCREENSHOT_TAGS` for filtering.
- **Profile-Specific Launch Options**: Profiles now support `LAUNCH_OPTIONS` that override global `SCRIPT.LAUNCH_OPTIONS`.
- **Bottom Mode Enhancement**: Added `PUT_DOWN_DELAY` to wait before checking other rods after hooking a fish.
- **Automated Gift Handling**: Automatically accepts gifts. Configure delay with `GIFT_DELAY`.
- **Random Rod Cast (`-RC`)**: Added flag for redundant casts. Adjust probability via `SCRIPT.RANDOM_CAST_PROBABILITY`.

### 🔧 Improvements
- **Result Table**: More detailed information has been added.
- **Stage Transitions**: Smoother reset/retrieve/pull sequences.
- **Gear Protection**: Decreases friction brake before quitting when using `-f` flag.
- **Configuration Fallback**: Gracefully defaults to built-in settings on missing configurations.

### 🐛 Bug Fixes
- Fixed PVA/groundbait refill issues across different rigs.
- Fixed missing material checks during crafting.
- Fixed crash caused by small `CHECK_DELAY` values.
- Fixed improper merging of `opts` into launch options.
- Resolved incompatibility between `-E` and `-g` flags.
- Fixed unexpected termination of `pirk` mode in edge cases.

### 🗃️ Deprecations & Renames
- `KEEPNET.DELAY` → `KEEPNET.FISH_DELAY`.
- `KEEPNET.RELEASE_WHITELIST` → `KEEPNET.WHITELIST`.
- Renamed launch options for clarity and consistency. Run `python tools\main.py -h` for details.

### 🧼 Maintenance
- Migrated code formatting/linting from Pylint/Black to Ruff.

## 0.4.2 (2025-04-07)
- Fixed a bug where the friction brake threshold was not being applied correctly.
- Fixed unexpected termination due to running out of fillet when using pirk/elevator mode.

## 0.4.1 (2025-03-30)
- Fixed a bug that left/right trolling mode doesn't work properly.
- Fixed an issue where electro mode doesn't work and compatible with `-g` flag.
- Fixed broken lure detection mechanism.
- Fixed a bug that pause is hard to trigger when using "toggle moving forward" tool.
- Added missing `POST_ACCELERATION` setting to `BOLOGNESE` mode.
- Tools now display config before running.
- Improved configuration guide.

## 0.4.0 (2025-03-16)
- Fixed a bug that the casting power level cannot be set to a value other than 1 or 5.
- Added `RETRIEVAL_TIMEOUT` to `SPIN` mode, allowing the script fall back to normal retrieval after retrieval with lift/pause timed out.

## 0.3.0 (2025-03-16)
- Reduced the sensitivity of lure break detection to avoid abnormal termination in the RU version.
- Added a new `KEEPNET.BLACKLIST` setting, blacklisted fish will always be released.
- Added a new `SHIFT` setting to `PIRK` mode, allowing users to hold shift while pirking.
- Increased check frequency for better user experience.
- Fixed a bug that the auto-friction-brake is not working properly.
- Updated READMEs.

## 0.2.1 (2025-03-08)
- Fixed a bug that auto-friction-brake, snag detection, and spooling detection are always disabled even the correct flags are used.

## 0.2.0 (2025-03-07)
- Fixed a bug that `-c` feature is not working properly.
- Added a `DEPTH_ADJUST_DURATION` setting to the `pirk` fishing mode to allow the user to set the duration of tightening the fishing line after opening the reel to adjust the depth of the lure.

## 0.1.0 (2025-03-06)
- New config system, bolognese mode, trolling mode, window mode support, and more.

[CHANGELOG]: /docs/zh-TW/CHANGELOG.md