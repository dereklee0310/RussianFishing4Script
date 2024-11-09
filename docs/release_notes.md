
<div align="center">
<h1>Release Notes</h1>
Nov. 10, 2024 
</div>


## New Features
- A new `pirk_timeout_option` option for marine fishing mode, users can choose whether
  to reset and recast the rod or simply adjust the depth of the lure by setting it to
  `recast` or `adjust`.

- When using spin fishing mode, use `-L` or `--lure` flag to replace your lure with a 
  random favorite one regularly, delay can be set in `config.ini`.

- Use `-x` flag to move the mouse randomly before casting the rod.

- Use `-X` flag to open in-game control panel and pause the script regularly, duration
  and delay can be set in `config.ini`.

- Use `-B` to take a screenshot when a fish bites so you can see exactly where the fish 
  was hooked.

- Add a new marine fishing strategy for elevator technique: `marine_elevator`.

## Bug Fixes
- Fix a bug that the script will stuck if no baits have been dug up during harvesting stage.

## Improvements
- If a fish escapes during line retrieval when using marine fishing mode, the script 
  will now sink the lure immediately instead of resetting the rod to the ready state.
- Now, the script will always check a different rod than the previous one to avoid 
  checking the same one over and over again.
- Increase the color tolerance of friction brake bar detection.
- The screenshot will now be taken of your game window instead of the entire screen.

## Other Changes
- Rename fishing strategy `marine` as `marine_pirk` to distinguish it from `marine_elevator`.

 
> [!NOTE]
**Please refer to `template.ini` to check new settings**.