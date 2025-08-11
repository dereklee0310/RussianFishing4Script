## Launch Options
You can use launch options to enable one or more functionalities at startup.
### Executable file
```
.\main.exe ...
```
### Python
```
python main.py ...
```
### uv
```
uv run main.py ...
```
> [!NOTE]
> If no launch options are given or if you run it by double-clicking, you can enter it after you select a feature to use.
>
> ![Launch options][launch_options]
### Examples (Executable File)
#### Use "Fishing Bot" and set the number of fishes in the keepnet to 32 (68 fishes to catch):
```
.\main.exe bot -n 32
```
#### Use "Fishing Bot", select profile 3, drink the coffee while battling against fish, and send an email to yourself when it stops:
```
.\main.exe bot -p 3 -c --email
```
#### Use "Fishing Bot", consume carrots, tea, and coffee to replenish player stats, and harvest baits before casting if possible:**
```
.\main.exe bot -rcH
```
#### Use "Craft Items" to create 10 items:
```
.\main.exe craft -n 10
```
#### Use "Calculate Tackle's Stats":
```
.\main.exe cal
```

> [!TIP]
> Use `-h` to see help messages.

> [!IMPORTANT]
> Add tea and carrot/coffee to your **[favorites][favorite_food]** if you want to use `-r` or `-c`.  
> To use a option that replaces an item for you, you also need to add items to your **[favorites][favorite_lure]**.


## Configuration
### Configure Settings
Edit your settings in [`config.yaml`][config.yaml], changes will be applied when you restart it.  
see [`default.py`][default.py] for config references.

### Add a New Profile
Copy an existing profile from the default configuration file, edit it, and add it back to the `PROFILE` section.

Here we add a new profile called `MY_BOTTOM_FISHING`, it would pop up in the profile list when you restart it:
```yaml
PROFILE:
  BOTTOM:
    DESCRIPTION: "Default bottom fishing."
    LAUNCH_OPTIONS: ""
    MODE: "bottom"
    CAST_POWER_LEVEL: 5.0
    CAST_DELAY: 4.0
    POST_ACCELERATION: false
    CHECK_DELAY: 16.0
    CHECK_MISS_LIMIT: 16
    PUT_DOWN_DELAY: 2.0
    RANDOM_ROD_SELECTION: true
            .
            .
            .
  MY_BOTTOM_FISHING:
    DESCRIPTION: "My bottom fishing."
    LAUNCH_OPTIONS: "-rctdDR"
    MODE: "bottom"
    CAST_POWER_LEVEL: 5.0
    CAST_DELAY: 4.0
    POST_ACCELERATION: false
    CHECK_DELAY: 16.0
    CHECK_MISS_LIMIT: 64
    PUT_DOWN_DELAY: 4.0
    RANDOM_ROD_SELECTION: false
```
> [!IMPORTANT]
> - Use a distint name for your new profile.  
> - Make sure the indentation level of the new profile is correct.
> - `MODE` must be `spin`, `bottom`, `pirk`, `elevator`, `telescopic`, or `bolognese`.

### Overwrite Configuration
Sometimes you might want to change a setting in [`config.yaml`][config.yaml] for one-time use,  
you can achieve this by using launch options without modifying your configuration file.  
Here's a simple example that overwrites your language setting:
```
.\main.exe LANGUAGE "ru"
```

### Two-rod Trolling Mode
Since trolling on a boat is just bottom fishing with trolling and direction keys pressed,  
you can combine a bottom fishing profile with the `-T` flag to get things done.  
There's no 3rd rod pod on the boat, so you should overwrite the bottom rod keys like this:
```
.\main.exe bot -T KEY.BOTTOM_RODS "(1, 2)"
```

[launch_options]: /static/readme/launch_options.png
[path]: /static/readme/path.png
[config.yaml]: /rf4s/config/config.yaml
[default.py]: /rf4s/config/defaults.py
[favorite_food]: /static/readme/favorite_food.png
[favorite_lure]: /static/readme/favorite_lure.png