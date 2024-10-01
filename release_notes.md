
<div align="center">
<h1>Release Notes</h1>
Oct. 2, 2024 
</div>


## New Features
- Now you can skip the casting stage after restarting the script by using `-C` flag.
- Use `-N <profile name>` to select the profile by name.
- Enable friction brake auto-changer with `-f` flag.
- Enable spod rod recast with `-o` flag
- Snag detection can be enabled by setting `snag_detection_enabled` to `True` in `config.ini`.

## Bug Fixes
- Fix a bug that sometimes the number of fishes in keepnet is count incorrectly

## Improvements
- Remove `window_size` from `config.ini`, script can now detect the game window size automatically.
- Add random delay between bottom rod checkings
- Baits harvesting is now applicable to spin and float fishing modes

## Other Changes
- Add missing images of Russian version
- Add setting validation
- Fix typo

 
> [!NOTE]
**Please refer to `template.ini` to check new settings**.