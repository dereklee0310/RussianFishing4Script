**[[中文版]][CHANGELOG]**

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