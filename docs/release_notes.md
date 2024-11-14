
<div align="center">
<h1>Release Notes</h1>
Nov. 14, 2024 
</div>


## New Features
- A new `coffee_drinking_quantity` setting to set the number of coffee you want to drink
  at a time, just like `alcohol_drinking_quantity`.

## Bug Fixes
- A bug that the rod will not be picked up after the player harvest the baits in 
  spin fishing mode.

- A bug that the script will get stuck if the fish is captured during line retrieval 
  in `marine_pirk` and `marine_elevator` mode.

- A bug that sometimes the friction brake value recorded in the script doesn't match 
  with the real one.

## Improvements
<!-- - If a fish escapes during line retrieval when using marine fishing mode, the script 
  will now sink the lure immediately instead of resetting the rod to the ready state.
- Now, the script will always check a different rod than the previous one to avoid 
  checking the same one over and over again.
- Increase the color tolerance of friction brake bar detection.
- The screenshot will now be taken of your game window instead of the entire screen. -->

<!--  -->
## Other Changes
- Rename fishing strategy `marine` as `marine_pirk` to distinguish it from `marine_elevator`.
 
> [!NOTE]
**Please refer to `template.ini` to check new settings**.