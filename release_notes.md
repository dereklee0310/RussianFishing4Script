
<div align="center">
<h1>Release Notes</h1>
June 8, 2024
</div>


## New Features
* Hotkey to stop the script without typing Ctrl-C in the terminal
* Fishing mode: spin fishing with wakey rig
* Options to disable SMTP validation and file integrity check at startup
* Option to take screenshot of every fish you catch
* Option to hold Shift key while battling against the fish
* Option to disable pirking in marine and wakey rig fishing mode

## Bug Fixes
* Possible stuck when using float fishing mode

## Improvements
* Improve code quality using Pylint and Black formatter
* Refactor most of the code to improve readability
* Add a setting node for better config organization

## Other Changes
* Remove `validate.py`
* Add `中文版template.ini` for Chinese players
* Rename and delete some of the settings in `config.ini`

| Old | New |
| ----| --- |
| base_iteration | |
| enable_confirmation | confirmation_enabled |
| harvest_baits_threhold | energy_threhold |
| spool_icon_confidence | retrieval_detect_confidence |
| alcohol_quantity | alcohol_drinking_quantity |
| alarm_sound_file_path | alarm_sound_file |
| acceleration_enabled | pre_acceleration_enabled |
| | SMTP_validation_enabled |
| | image_verification_enabled |
| | quit |
| | cast_delay |
| | post_acceleration_enabled |

> [!NOTE]
**Please refer to `template.ini` to check new settings**.