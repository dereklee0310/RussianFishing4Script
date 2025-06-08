"""Default yacs config node."""

from yacs.config import CfgNode as CN

_C = CN()
_C.VERSION = "0.5.2"

# ---------------------------------------------------------------------------- #
#                                    General                                   #
# ---------------------------------------------------------------------------- #
_C.SCRIPT = CN()
_C.SCRIPT.LANGUAGE = "en"  # Language for the script. Options: en, ru, zh-TW, zh-CN
_C.SCRIPT.LAUNCH_OPTIONS = ""  # Default launch options for the script, e.g., -r -c -H
_C.SCRIPT.SMTP_VERIFICATION = True
_C.SCRIPT.IMAGE_VERIFICATION = True
_C.SCRIPT.SNAG_DETECTION = True
_C.SCRIPT.SPOOLING_DETECTION = True
_C.SCRIPT.RANDOM_ROD_SELECTION = True  # For bottom mode
# Confidence threshold for spooling detection (lower = more sensitive)
_C.SCRIPT.SPOOL_CONFIDENCE = 0.98
# Delay before recasting spod rod (in seconds)
# Use bottom mode and -o to enable it.
_C.SCRIPT.SPOD_ROD_RECAST_DELAY = 1800
# Delay before changing lure randomly (in seconds)
# Use spin mode and -L to enable it.
_C.SCRIPT.LURE_CHANGE_DELAY = 1800
_C.SCRIPT.ALARM_SOUND = "./static/sound/guitar.wav"  # Path to alarm sound file
# Probability to add a redundant rod cast (0.0 to 1.0)
_C.SCRIPT.RANDOM_CAST_PROBABILITY = 0.25
# When using -s flag, only take screenshot of the fishes with tags below
# If left empty, the script will take screenshot of every fish you caught
_C.SCRIPT.SCREENSHOT_TAGS = ("green", "yellow", "blue", "purple", "pink")

# ---------------------------------------------------------------------------- #
#                                  Key Binding                                 #
# ---------------------------------------------------------------------------- #
_C.KEY = CN()
_C.KEY.TEA = -1  # Key binding for tea. Set to -1 to use quick selection menu
_C.KEY.CARROT = -1  # Key binding for carrot. Set to -1 to use quick selection menu
_C.KEY.BOTTOM_RODS = (1, 2, 3)  # Key bindings for bottom rods
_C.KEY.COFFEE = 4  # Key binding for coffee. Set to -1 to use quick selection menu
_C.KEY.DIGGING_TOOL = 5  # Key binding for digging tool
_C.KEY.ALCOHOL = 6  # Key binding for alcohol
# Key binding for the main rod (used when harvesting baits with one rod)
_C.KEY.MAIN_ROD = 1
_C.KEY.SPOD_ROD = 7  # Key binding for the spod rod (used in bottom mode)
# Key binding to stop the script (default is Ctrl-C)
# If you want to use a special quitting shortcut, please refer to pynput's docs:
# https://pynput.readthedocs.io/en/latest/keyboard.html#pynput.keyboard.Key .
_C.KEY.QUIT = "CTRL-C"

# ---------------------------------------------------------------------------- #
#                                 Player Stats                                 #
# ---------------------------------------------------------------------------- #
_C.STAT = CN()
# Minimum energy level before drinking coffee/harvesting baits
_C.STAT.ENERGY_THRESHOLD = 0.74
_C.STAT.HUNGER_THRESHOLD = 0.5  # Minimum hunger level before consuming carrot
_C.STAT.COMFORT_THRESHOLD = 0.51  # Minimum comfort level before consuming tea
_C.STAT.TEA_DELAY = 300  # Delay between tea drinks (in seconds)
_C.STAT.COFFEE_LIMIT = 10  # Maximum coffee drinks per fish fight.
_C.STAT.COFFEE_PER_DRINK = 1  # Amount of coffee consumed per drink
_C.STAT.ALCOHOL_DELAY = 900  # Delay between alcohol drinks (in seconds)
_C.STAT.ALCOHOL_PER_DRINK = 1  # Amount of alcohol consumed per drink

# ---------------------------------------------------------------------------- #
#                   Friction Brake (Use -f flag to enable it)                  #
# ---------------------------------------------------------------------------- #
_C.FRICTION_BRAKE = CN()
_C.FRICTION_BRAKE.INITIAL = 29  # Initial friction brake value
_C.FRICTION_BRAKE.MAX = 30  # Maximum friction brake value
# Delay before starting to adjust friction brake after a fish is hooked
_C.FRICTION_BRAKE.START_DELAY = 2.0
_C.FRICTION_BRAKE.INCREASE_DELAY = 1.0  # Delay before increasing friction brake
_C.FRICTION_BRAKE.SENSITIVITY = "medium"  # Sensitivity of friction brake detection

# ---------------------------------------------------------------------------- #
#                                    Keepnet                                   #
# ---------------------------------------------------------------------------- #
_C.KEEPNET = CN()
_C.KEEPNET.CAPACITY = 100
_C.KEEPNET.FISH_DELAY = 0.0  # Delay before keeping the fish (for screenshots)
_C.KEEPNET.GIFT_DELAY = 4.0  # Delay before keeping the gift (for screenshots)
_C.KEEPNET.FULL_ACTION = "quit"  # Action when keepnet is full. Options: quit, alarm
# Whitelist for untagged fish releasing when using -t flag
# Options: mackerel, saithe, herring, squid, scallop, mussel, perch, shorthorn_sculpin
_C.KEEPNET.WHITELIST = (
    "mackerel",
    "saithe",
    "herring",
    "squid",
    "scallop",
    "mussel",
)
# Fish in the blacklist will always be released
# Options: mackerel, saithe, herring, squid, scallop, mussel, perch, shorthorn_sculpin
_C.KEEPNET.BLACKLIST = ()
# When using -t flag, only the fish with tags below would be kept
_C.KEEPNET.TAGS = ("green", "yellow", "blue", "purple", "pink")


# ---------------------------------------------------------------------------- #
#                                 Notification                                 #
# ---------------------------------------------------------------------------- #
_C.NOTIFICATION = CN()
_C.NOTIFICATION.EMAIL = "email@example.com"
_C.NOTIFICATION.PASSWORD = "password"
_C.NOTIFICATION.SMTP_SERVER = "smtp.gmail.com"
_C.NOTIFICATION.MIAO_CODE = "example"
_C.NOTIFICATION.DISCORD_WEBHOOK_URL = ""

# ---------------------------------------------------------------------------- #
#                       Pause ( use -X flag to enable it)                      #
# ---------------------------------------------------------------------------- #
_C.PAUSE = CN()
_C.PAUSE.DELAY = 1800  # Delay between pauses (in seconds)
_C.PAUSE.DURATION = 600  # Duration of pause (in seconds)

_C.PROFILE = CN()
# ---------------------------------------------------------------------------- #
#                             Spin Fishing Profile                             #
# ---------------------------------------------------------------------------- #
_C.PROFILE.SPIN = CN()
_C.PROFILE.SPIN.MODE = "spin"
# Launch options that overwrites SCRIPT.LAUNCH_OPTIONS
# Fall back to SCRIPT.LAUNCH_OPTIONS if left empty
_C.PROFILE.SPIN.LAUNCH_OPTIONS = ""
# Power level for casting, 1 ~ 5
# 1: 0%, 2: ~25%, 3: ~50%, 4: ~75% 5: 100%+ (power cast), FYR
# For instance, 2.5 cast_power_level equals to 37.5% casting power
_C.PROFILE.SPIN.CAST_POWER_LEVEL = 5.0
# Delay after casting before lure sinks
_C.PROFILE.SPIN.CAST_DELAY = 6.0
# Duration to tighten the fishing line after casting
_C.PROFILE.SPIN.TIGHTEN_DURATION = 0.0
# Duration of retrieving the line or lifting the rod (right mosue button)
_C.PROFILE.SPIN.RETRIEVAL_DURATION = 0.0
# Delay after retrieving the line or lifting the rod (right mosue button)
_C.PROFILE.SPIN.RETRIEVAL_DELAY = 0.0
# Timeout for retrieving with pause/lift, followed by the normal retrieval
_C.PROFILE.SPIN.RETRIEVAL_TIMEOUT = 256.0
# Hold down the Shift key when performing special spin fishing techniques
_C.PROFILE.SPIN.PRE_ACCELERATION = False
# Hold Shift key during fish fight. Options: on, off, auto
_C.PROFILE.SPIN.POST_ACCELERATION = "off"
# Type of special spin fishing technique to perform. Options: normal, pause, lift
_C.PROFILE.SPIN.TYPE = "normal"

_C.PROFILE.SPIN_WITH_PAUSE = CN()
_C.PROFILE.SPIN_WITH_PAUSE.MODE = "spin"
_C.PROFILE.SPIN_WITH_PAUSE.LAUNCH_OPTIONS = ""
_C.PROFILE.SPIN_WITH_PAUSE.CAST_POWER_LEVEL = 5.0
_C.PROFILE.SPIN_WITH_PAUSE.CAST_DELAY = 6.0
_C.PROFILE.SPIN_WITH_PAUSE.TIGHTEN_DURATION = 1.0
_C.PROFILE.SPIN_WITH_PAUSE.RETRIEVAL_DURATION = 1.0
_C.PROFILE.SPIN_WITH_PAUSE.RETRIEVAL_DELAY = 3.0
_C.PROFILE.SPIN_WITH_PAUSE.RETRIEVAL_TIMEOUT = 256.0
_C.PROFILE.SPIN_WITH_PAUSE.PRE_ACCELERATION = False
_C.PROFILE.SPIN_WITH_PAUSE.POST_ACCELERATION = "off"
_C.PROFILE.SPIN_WITH_PAUSE.TYPE = "pause"


_C.PROFILE.SPIN_WITH_LIFT = CN()
_C.PROFILE.SPIN_WITH_LIFT.MODE = "spin"
_C.PROFILE.SPIN_WITH_LIFT.LAUNCH_OPTIONS = ""
_C.PROFILE.SPIN_WITH_LIFT.CAST_POWER_LEVEL = 5.0
_C.PROFILE.SPIN_WITH_LIFT.CAST_DELAY = 6.0
_C.PROFILE.SPIN_WITH_LIFT.TIGHTEN_DURATION = 0.0
_C.PROFILE.SPIN_WITH_LIFT.RETRIEVAL_DURATION = 1.0
_C.PROFILE.SPIN_WITH_LIFT.RETRIEVAL_DELAY = 1.0
_C.PROFILE.SPIN_WITH_LIFT.RETRIEVAL_TIMEOUT = 256.0
_C.PROFILE.SPIN_WITH_LIFT.PRE_ACCELERATION = False
_C.PROFILE.SPIN_WITH_LIFT.POST_ACCELERATION = "off"
_C.PROFILE.SPIN_WITH_LIFT.TYPE = "lift"


# ---------------------------------------------------------------------------- #
#                            Bottom Fishing Profile                            #
# ---------------------------------------------------------------------------- #
_C.PROFILE.BOTTOM = CN()
_C.PROFILE.BOTTOM.MODE = "bottom"
# Launch options that overwrites SCRIPT.LAUNCH_OPTIONS
# Fall back to SCRIPT.LAUNCH_OPTIONS if left empty
_C.PROFILE.BOTTOM.LAUNCH_OPTIONS = ""
# Power level for casting, 1 ~ 5
# 1: 0%, 2: ~25%, 3: ~50%, 4: ~75% 5: 100%+ (power cast), FYR
# For instance, 2.5 cast_power_level equals to 37.5% casting power
_C.PROFILE.BOTTOM.CAST_POWER_LEVEL = 5.0
_C.PROFILE.BOTTOM.CAST_DELAY = 4.0  # Delay after casting before lure sinks
# Hold Shift key during fish fight. Options: on, off, auto
_C.PROFILE.BOTTOM.POST_ACCELERATION = "off"
# Delay before checking fish bite on next rod
_C.PROFILE.BOTTOM.CHECK_DELAY = 32.0
# Maximum allowed misses before recasting the rod
_C.PROFILE.BOTTOM.CHECK_MISS_LIMIT = 16
# Delay before checking if a fish is hooked again and putting down the rod
_C.PROFILE.BOTTOM.PUT_DOWN_DELAY = 0.0


# ---------------------------------------------------------------------------- #
#                      Marine / Wakey Rig Pirking Profile                      #
# ---------------------------------------------------------------------------- #
_C.PROFILE.PIRK = CN()
_C.PROFILE.PIRK.MODE = "pirk"
# Launch options that overwrites SCRIPT.LAUNCH_OPTIONS
# Fall back to SCRIPT.LAUNCH_OPTIONS if left empty
_C.PROFILE.PIRK.LAUNCH_OPTIONS = ""
# Power level for casting, 1 ~ 5
# 1: 0%, 2: ~25%, 3: ~50%, 4: ~75% 5: 100%+ (power cast), FYR
# For instance, 2.5 cast_power_level equals to 37.5% casting power
_C.PROFILE.PIRK.CAST_POWER_LEVEL = 1.0
_C.PROFILE.PIRK.CAST_DELAY = 4.0  # Delay after casting before lure sinks
_C.PROFILE.PIRK.SINK_TIMEOUT = 60.0  # Maximum time allowed for sinking
# Duration to tighten the line after sinking lure/adjusting lure depth
_C.PROFILE.PIRK.TIGHTEN_DURATION = 1.0
# Delay after opening reel to adjust lure depth, set this to 0 to recast the rod instead
_C.PROFILE.PIRK.DEPTH_ADJUST_DELAY = 4.0
# Durtion to tighten the line after opening reel for DEPTH_ADJUST_DELAY seconds
_C.PROFILE.PIRK.DEPTH_ADJUST_DURATION = 1.0
_C.PROFILE.PIRK.CTRL = False  # Hold Ctrl key during pirking
_C.PROFILE.PIRK.SHIFT = False  # Hold Shift key during pirking
# Duration of lifting the rod, set this to 0 if you want to wait instead of pirking
_C.PROFILE.PIRK.PIRK_DURATION = 0.5
_C.PROFILE.PIRK.PIRK_DELAY = 2.0  # Delay after lifting the rod
# Timeout for pirking session
_C.PROFILE.PIRK.PIRK_TIMEOUT = 32.0
# Retrieve the fishing line during pirking
_C.PROFILE.PIRK.PIRK_RETRIEVAL = False
# When a fish is hooked, check if the fish is still hooked
# after HOOK_DELAY seconds, continue pirking if not
_C.PROFILE.PIRK.HOOK_DELAY = 0.5
# Hold Shift key during fish fight. Options: on, off, auto
_C.PROFILE.PIRK.POST_ACCELERATION = "auto"

_C.PROFILE.PIRK_WITH_RETRIEVAL = CN()
_C.PROFILE.PIRK_WITH_RETRIEVAL.MODE = "pirk"
_C.PROFILE.PIRK_WITH_RETRIEVAL.LAUNCH_OPTIONS = ""
_C.PROFILE.PIRK_WITH_RETRIEVAL.CAST_POWER_LEVEL = 1.0
_C.PROFILE.PIRK_WITH_RETRIEVAL.CAST_DELAY = 4.0
_C.PROFILE.PIRK_WITH_RETRIEVAL.SINK_TIMEOUT = 60.0
_C.PROFILE.PIRK_WITH_RETRIEVAL.TIGHTEN_DURATION = 1.0
_C.PROFILE.PIRK_WITH_RETRIEVAL.DEPTH_ADJUST_DELAY = 0.0
_C.PROFILE.PIRK_WITH_RETRIEVAL.DEPTH_ADJUST_DURATION = 1.0
_C.PROFILE.PIRK_WITH_RETRIEVAL.CTRL = False
_C.PROFILE.PIRK_WITH_RETRIEVAL.SHIFT = False
_C.PROFILE.PIRK_WITH_RETRIEVAL.PIRK_DURATION = 0.5
_C.PROFILE.PIRK_WITH_RETRIEVAL.PIRK_DELAY = 2.0
_C.PROFILE.PIRK_WITH_RETRIEVAL.PIRK_TIMEOUT = 32.0
_C.PROFILE.PIRK_WITH_RETRIEVAL.PIRK_RETRIEVAL = True
_C.PROFILE.PIRK_WITH_RETRIEVAL.HOOK_DELAY = 0.5
_C.PROFILE.PIRK_WITH_RETRIEVAL.POST_ACCELERATION = "auto"

# Spin fishing with wakey rig at Ladoga Archipelago
_C.PROFILE.WAKEY_RIG = CN()
_C.PROFILE.WAKEY_RIG.MODE = "pirk"
_C.PROFILE.WAKEY_RIG.LAUNCH_OPTIONS = ""
_C.PROFILE.WAKEY_RIG.CAST_POWER_LEVEL = 1.0
_C.PROFILE.WAKEY_RIG.CAST_DELAY = 4.0
_C.PROFILE.WAKEY_RIG.SINK_TIMEOUT = 45.0
_C.PROFILE.WAKEY_RIG.TIGHTEN_DURATION = 1.0
_C.PROFILE.WAKEY_RIG.DEPTH_ADJUST_DELAY = 4.0
_C.PROFILE.WAKEY_RIG.DEPTH_ADJUST_DURATION = 1.0
_C.PROFILE.WAKEY_RIG.CTRL = True
_C.PROFILE.WAKEY_RIG.CTRL = False
_C.PROFILE.WAKEY_RIG.PIRK_DURATION = 1.5
_C.PROFILE.WAKEY_RIG.PIRK_DELAY = 4.0
_C.PROFILE.WAKEY_RIG.PIRK_TIMEOUT = 32.0
_C.PROFILE.WAKEY_RIG.PIRK_RETRIEVAL = False
_C.PROFILE.WAKEY_RIG.HOOK_DELAY = 0.5
_C.PROFILE.WAKEY_RIG.POST_ACCELERATION = "auto"

# ---------------------------------------------------------------------------- #
#                            Marine Elevator Profile                           #
# ---------------------------------------------------------------------------- #
_C.PROFILE.ELEVATOR = CN()
_C.PROFILE.ELEVATOR.MODE = "elevator"
# Launch options that overwrites SCRIPT.LAUNCH_OPTIONS
# Fall back to SCRIPT.LAUNCH_OPTIONS if left empty
_C.PROFILE.ELEVATOR.LAUNCH_OPTIONS = ""
# Power level for casting, 1 ~ 5
# 1: 0%, 2: ~25%, 3: ~50%, 4: ~75% 5: 100%+ (power cast), FYR
# For instance, 2.5 cast_power_level equals to 37.5% casting power
_C.PROFILE.ELEVATOR.CAST_POWER_LEVEL = 1.0
# Delay after casting before lure sinks
_C.PROFILE.ELEVATOR.CAST_DELAY = 4.0
# Maximum time allowed for sinking
_C.PROFILE.ELEVATOR.SINK_TIMEOUT = 60.0
# Duration to tighten the line after sinking lure
_C.PROFILE.ELEVATOR.TIGHTEN_DURATION = 1.0
# Duration of retrieving the fishing line/opening the reel
_C.PROFILE.ELEVATOR.ELEVATE_DURATION = 4.0
# Delay after retrieving the fishing line/opening the reel
_C.PROFILE.ELEVATOR.ELEVATE_DELAY = 4.0
# Timeout for pirking session
_C.PROFILE.ELEVATOR.ELEVATE_TIMEOUT = 40.0
# Lock / Unlocking the reel after elevating timed out to drop the lure level by level
_C.PROFILE.ELEVATOR.DROP = False
# When a fish is hooked, check if the fish is still hooked
# after HOOK_DELAY seconds, continue elevating if not
_C.PROFILE.ELEVATOR.HOOK_DELAY = 0.5
# Hold Shift key during fish fight. Options: on, off, auto
_C.PROFILE.ELEVATOR.POST_ACCELERATION = "auto"

_C.PROFILE.ELEVATOR_WITH_DROP = CN()
_C.PROFILE.ELEVATOR_WITH_DROP.MODE = "elevator"
_C.PROFILE.ELEVATOR_WITH_DROP.LAUNCH_OPTIONS = ""
_C.PROFILE.ELEVATOR_WITH_DROP.CAST_POWER_LEVEL = 1.0
_C.PROFILE.ELEVATOR_WITH_DROP.CAST_DELAY = 4.0
_C.PROFILE.ELEVATOR_WITH_DROP.SINK_TIMEOUT = 60.0
_C.PROFILE.ELEVATOR_WITH_DROP.TIGHTEN_DURATION = 1.0
_C.PROFILE.ELEVATOR_WITH_DROP.ELEVATE_DURATION = 4.0
_C.PROFILE.ELEVATOR_WITH_DROP.ELEVATE_DELAY = 4.0
_C.PROFILE.ELEVATOR_WITH_DROP.ELEVATE_TIMEOUT = 40.0
_C.PROFILE.ELEVATOR_WITH_DROP.DROP = True
_C.PROFILE.ELEVATOR_WITH_DROP.HOOK_DELAY = 0.5
_C.PROFILE.ELEVATOR_WITH_DROP.POST_ACCELERATION = "auto"

# ---------------------------------------------------------------------------- #
#                          Telescopic fishing Profile                          #
# ---------------------------------------------------------------------------- #
_C.PROFILE.TELESCOPIC = CN()
_C.PROFILE.TELESCOPIC.MODE = "telescopic"
# Launch options that overwrites SCRIPT.LAUNCH_OPTIONS
# Fall back to SCRIPT.LAUNCH_OPTIONS if left empty
_C.PROFILE.TELESCOPIC.LAUNCH_OPTIONS = ""
# Power level for casting, 1 ~ 5
# 1: 0%, 2: ~25%, 3: ~50%, 4: ~75% 5: 100%+ (power cast), FYR
# For instance, 2.5 cast_power_level equals to 37.5% casting power
_C.PROFILE.TELESCOPIC.CAST_POWER_LEVEL = 5.0
# Delay after casting before lure sinks
_C.PROFILE.TELESCOPIC.CAST_DELAY = 4.0
# Sensitivity of float detection
_C.PROFILE.TELESCOPIC.FLOAT_SENSITIVITY = 0.68
_C.PROFILE.TELESCOPIC.CHECK_DELAY = 1.0  # Delay between fish bite checks
_C.PROFILE.TELESCOPIC.PULL_DELAY = 0.5  # Delay pulling a fish after it's hooked
# Recast rod after timed out, designed for flowing water maps
_C.PROFILE.TELESCOPIC.DRIFT_TIMEOUT = 16.0
# Shape of the float camera, the script tracks the whole camrea window by default
# Options: square, wide, tall
_C.PROFILE.TELESCOPIC.CAMERA_SHAPE = "square"


# ---------------------------------------------------------------------------- #
#                           Bolognese Fishing Profile                          #
# ---------------------------------------------------------------------------- #
_C.PROFILE.BOLOGNESE = CN()
_C.PROFILE.BOLOGNESE.MODE = "bolognese"
# Launch options that overwrites SCRIPT.LAUNCH_OPTIONS
# Fall back to SCRIPT.LAUNCH_OPTIONS if left empty
_C.PROFILE.BOLOGNESE.LAUNCH_OPTIONS = ""
# Power level for casting, 1 ~ 5
# 1: 0%, 2: ~25%, 3: ~50%, 4: ~75% 5: 100%+ (power cast), FYR
# For instance, 2.5 cast_power_level equals to 37.5% casting power
_C.PROFILE.BOLOGNESE.CAST_POWER_LEVEL = 5.0
# Delay after casting before lure sinks
_C.PROFILE.BOLOGNESE.CAST_DELAY = 4.0
# Sensitivity of float detection
_C.PROFILE.BOLOGNESE.FLOAT_SENSITIVITY = 0.68
_C.PROFILE.BOLOGNESE.CHECK_DELAY = 1.0  # Delay between fish bite checks
_C.PROFILE.BOLOGNESE.PULL_DELAY = 0.5  # Delay pulling a fish after it's hooked
# Recast rod after timed out, designed for flowing water maps
_C.PROFILE.BOLOGNESE.DRIFT_TIMEOUT = 32.0
# Shape of the float camera, the script tracks the whole camrea window by default
# Options: square, wide, tall
# (Fallback to float camera detection mode if the window size is not supported)
_C.PROFILE.BOLOGNESE.CAMERA_SHAPE = "square"
# Hold Shift key during fish fight. Options: on, off, auto
_C.PROFILE.BOLOGNESE.POST_ACCELERATION = "off"


def get_cfg_defaults():
    """Get a yacs CfgNode object with default values for my_project."""
    # Return a clone so that the defaults will not be altered
    # This is for the "local variable" use pattern
    return _C.clone()
