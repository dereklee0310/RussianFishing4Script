**[[中文版]][CHANGELOG]**

## tmp

Update app and window module

-e/--exit-key -> -q/--quit-key

type in calculate.py

-bl -> -BL

## 0.4.2 (2025-04-07)
- Fixed a bug where the friction brake threshold was not being applied correctly

- Fixed unexpected termination due to running out of fillet when using pirk/elevator mode


## 0.4.1 (2025-03-30)

- Fixed a bug that left/right trolling mode doesn't work properly

- Fixed an issue where electro mode doesn't work and compatible with `-g` flag

- Fixed broken lure detection mechanism

- Fixed a bug that pause is hard to trigger when using "toggle moving foward" tool 

- Added missing `POST_ACCELERATION` setting to `BOLOGNESE` mode

- Tools now display config before running

- Improved configuration guide

## 0.4.0 (2025-03-16)

- Fixed a bug that the casting power level cannot be set to a value other than 1 or 5.

- Added `RETRIEVAL_TIMEOUT` to `SPIN` mode, allowing the script fall back to normal
  retrieval after retrieval with lift/pause timed out.

## 0.3.0 (2025-03-16)

- Reduced the sensitivity of lure break detection to avoid abnormal termination in the RU version.

- Added a new `KEEPNET.BLACKLIST` setting, blacklisted fish will always be released.

- Added a new `SHIFT` setting to `PIRK` mode, allowing users to hold shift while pirking.

- Increased check frequency for better user experience.

- Fixed a bug that the auto-friction-brake is not working properly.

- Updated READMEs


## 0.2.1 (2025-03-08)

- Fixed a bug that auto-friction-brake, snag detection, and spooling detection are always
  disabled even the correct flags are used.

## 0.2.0 (2025-03-07)

- Fixed a bug that `-c` feature is not working properly.

-  Added a `DEPTH_ADJUST_DURATION` setting to the `pirk` fishing mode to allow the user to set the duration of tightening the fishing line after opening the reel to adjust the depth of the lure.

## 0.1.0 (2025-03-06)

- New config system, bolognese mode, trolling mode, window mode support, and more.

[CHANGELOG]: /docs/zh-TW/CHANGELOG.md