# Configuring RF4S

---

## Interface Language

RF4S supports **English** (`en`) and **Russian** (`ru`) interfaces. The `LANGUAGE` parameter in `config.yaml` determines:
- The image set used for game element recognition (`static/en/` or `static/ru/`)

```yaml
# English
LANGUAGE: "en"

# Russian
LANGUAGE: "ru"
```

> [!IMPORTANT]
> The `LANGUAGE` value must match the language set in Russian Fishing 4 itself.

One-time override via command line (without modifying the config):
```
python main.py LANGUAGE "ru"
```

---

## Launch Options

Launch options allow you to enable features when starting the script.

### Launch Methods

**Executable file:**
```
.\main.exe [command] [options]
```

**Python:**
```
python main.py [command] [options]
```

**uv:**
```
uv run main.py [command] [options]
```

> [!NOTE]
> If no options are specified (or launched by double-clicking), the script will enter interactive mode: it will display a list of features, prompt you to select by number, and enter options.
>
> ![Launch options][launch_options]

### Interactive Mode

When launched without arguments:
1. A list of features (0-5) is displayed
2. Enter a feature number, `h` for help, `q` to quit
3. Enter launch options or press Enter to skip

---

## Commands

### 1. `bot` — Fishing Bot

Automates the fishing process.

```
python main.py bot [options]
```

#### Main Options

| Option | Description |
|---|---|
| `-V`, `--version` | Show version and exit |
| `-p PID`, `--pid PID` | Specify profile ID (0-N) |
| `-N NAME`, `--pname NAME` | Specify profile name |
| `-n COUNT`, `--fishes-in-keepnet COUNT` | Number of fish already in keepnet (default: 0) |

#### Fishing Modes

| Option | Description | Values |
|---|---|---|
| `-T [DIR]`, `--trolling [DIR]` | Trolling mode | `forward`, `left`, `right` (default: `forward`) |
| `-R [METERS]`, `--rainbow [METERS]` | Rainbow line mode | `0`, `5` (default: `5`) |
| `-BT [DAYS]`, `--boat-ticket [DAYS]` | Auto-renew boat ticket | `1`, `2`, `3`, `5` (default: `5`) |

#### Flags: Fish Management

| Flag | Description |
|---|---|
| `-t`, `--tag` | Keep only tagged fish |
| `-c`, `--coffee` | Drink coffee when stamina is low during retrieval |
| `-a`, `--alcohol` | Drink alcohol before saving fish |
| `-l`, `--lift` | Constantly lift the tackle during retrieval |

#### Flags: Tackle and Lures

| Flag | Description |
|---|---|
| `-L`, `--lure` | Change lure to a random favorite (mode: spinning) |
| `-BL`, `--broken-lure` | Replace broken lures with favorites |
| `-e`, `--electro` | Electro mode for Electro Raptor series reels |
| `-FB`, `--friction-brake` | Automatically adjust friction brake |
| `-GR`, `--gear-ratio` | Switch gear after reel timeout |

#### Flags: Groundbait (Bottom Fishing)

| Flag | Description |
|---|---|
| `-DM`, `--dry-mix` | Replenish dry mix |
| `-GB`, `--groundbait` | Replenish groundbait |
| `-PVA`, `--pva` | Replenish PVA bags |
| `-SR`, `--spod-rod` | Recast spod rod |

#### Flags: Bot Behavior

| Flag | Description |
|---|---|
| `-r`, `--refill` | Consume tea and carrots when hunger or comfort is low |
| `-H`, `--harvest` | Harvest bait before casting |
| `-m`, `--mouse` | Randomly move mouse before casting |
| `-P`, `--pause` | Occasionally pause the script before casting |
| `-RC`, `--random-cast` | Make random extra casts |
| `-SC`, `--skip-cast` | Skip the first cast |
| `-NA`, `--no-animation` | Disable waiting for trophy and gift animations |

#### Flags: Logging and Notifications

| Flag | Description |
|---|---|
| `-b`, `--bite` | Screenshot on bite (`screenshots/`) |
| `-s`, `--screenshot` | Screenshot after catching fish (`screenshots/`) |
| `-d`, `--data` | Save fishing data to `/logs` |
| `-E`, `--email` | Email notification on stop |
| `-M`, `--miaotixing` | Miaotixing notification on stop |
| `-D`, `--discord` | Discord notification on stop |
| `-TG`, `--telegram` | Telegram notification on stop |

#### Flags: Post-Stop Actions

| Flag | Description |
|---|---|
| `-S`, `--shutdown` | Shut down the computer |
| `-SO`, `--signout` | Sign out instead of closing the game |

#### Examples

```bash
# Bot with profile 0 and auto friction brake
python main.py bot -p 0 -FB

# Bot with named profile and screenshot saving
python main.py bot -N "MyProfile" -s -b

# Forward trolling with rainbow line
python main.py bot -T forward -R 5

# Bottom fishing with groundbait
python main.py bot -DM -GB -PVA

# Stat recovery + bait harvesting + coffee
python main.py bot -rcH
```

> [!IMPORTANT]
> For `-r` and `-c`, add tea, carrots, and coffee to your **[favorites][favorite_food]**.
> For auto tackle replacement, add items to your **[favorites][favorite_lure]**.

---

### 2. `craft` — Craft Items

Automates the creation of baits, groundbaits, lures, etc.

```
python main.py craft [options]
```

| Option | Description |
|---|---|
| `-V`, `--version` | Show version |
| `-d`, `--discard` | Discard all crafted items (for groundbaits) |
| `-i`, `--ignore` | Ignore unselected material slots |
| `-n COUNT`, `--craft-limit COUNT` | Number of items (default: -1, infinite) |

```bash
# Craft 10 items
python main.py craft -n 10

# Craft groundbait and discard
python main.py craft -d
```

---

### 3. `move` — Move Forward

Toggles character forward movement (holds the `W` key).

```
python main.py move [options]
```

| Option | Description |
|---|---|
| `-V`, `--version` | Show version |
| `-s`, `--shift` | Hold Shift while moving (sprint) |

```bash
# Normal movement
python main.py move

# Sprint with Shift
python main.py move -s
```

---

### 4. `harvest` — Harvest Bait

Automatically harvests bait in idle mode.

```
python main.py harvest [options]
```

| Option | Description |
|---|---|
| `-V`, `--version` | Show version |
| `-r`, `--refill` | Replenish hunger and comfort with tea and carrots |

```bash
# Simple bait harvesting
python main.py harvest

# Harvesting with stat recovery
python main.py harvest -r
```

---

### 5. `frictionbrake` (or `fb`) — Auto Friction Brake

Automatically adjusts the reel's friction brake.

```
python main.py frictionbrake
python main.py fb
```

| Option | Description |
|---|---|
| `-V`, `--version` | Show version |

---

### 6. `calculate` (or `cal`) — Tackle Calculator

Calculates tackle stats and recommended friction brake considering wear.

```
python main.py calculate
python main.py cal
```

| Option | Description |
|---|---|
| `-V`, `--version` | Show version |

---

## Hotkeys During Operation

Configured in `config.yaml` (section `KEY`):

| Default Key | Action | Config Parameter |
|---|---|---|
| `[` | Pause / resume (bot) | `KEY.PAUSE` |
| `Ctrl+C` | Terminate script | `KEY.QUIT` |
| `[` | Reset friction brake | `KEY.FRICTION_BRAKE_RESET` |
| `]` | Exit friction brake mode | `KEY.FRICTION_BRAKE_QUIT` |
| `w` | Pause movement | `KEY.MOVE_PAUSE` |
| `s` | Exit movement mode | `KEY.MOVE_QUIT` |

---

## Configuration File

All settings are stored in `config.yaml` in the project root. Changes take effect after restart.

Reference for all parameters: [`defaults.py`][default.py]

### Main Parameters

| Parameter | Description | Values |
|---|---|---|
| `LANGUAGE` | Interface and recognition language | `"en"`, `"ru"` |
| `BOT.CLICK_LOCK` | Windows mouse ClickLock | `true`, `false` |
| `BOT.KEEPNET.CAPACITY` | Keepnet capacity | number |
| `BOT.SPOOL_CONFIDENCE` | Spool detection sensitivity | `0.0`-`1.0` |
| `BOT.JITTER_SCALE` | Random delay scale | number |

---

## Profiles

Profiles allow you to save settings for different fishing styles.

### Adding a New Profile

Copy an existing profile from the config, edit it, and add it to the `PROFILE` section:

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
    DESCRIPTION: "My bottom fishing setup."
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
> - The profile name must be **unique**.
> - Ensure correct **indentation** (YAML is sensitive to it).
> - Valid `MODE` values: `spin`, `bottom`, `pirk`, `elevator`, `telescopic`, `bolognese`.

---

## Configuration Override

You can temporarily change any parameter from `config.yaml` without editing the file — via command-line arguments:

```
.\main.exe LANGUAGE "ru"
```
```
.\main.exe bot BOT.KEEPNET.CAPACITY 200
```

This is useful for one-time launches with non-standard settings.

---

## Two-Rod Trolling

Trolling on a boat is essentially bottom fishing while holding movement keys. Use a bottom fishing profile with the `-T` flag:

```
.\main.exe bot -T KEY.BOTTOM_RODS "(1, 2)"
```

There is no third rod pod on the boat, so the rod keys are overridden to `1` and `2`.

---

## Folder Structure

The following folders are automatically created after launch:

| Folder | Contents |
|---|---|
| `screenshots/` | Screenshots of bites and caught fish |
| `logs/` | Execution logs, fishing data, charts |

[launch_options]: /static/readme/launch_options.png
[config.yaml]: /rf4s/config/config.yaml
[default.py]: /rf4s/config/defaults.py
[favorite_food]: /static/readme/favorite_food.png
[favorite_lure]: /static/readme/favorite_lure.png
