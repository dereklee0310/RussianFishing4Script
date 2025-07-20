"""Default yacs config node."""

from yacs.config import CfgNode as CN

_C = CN()
_C.VERSION = "0.5.3"
# Game Language (options: en, ru, zh-TW, zh-CN)
_C.LANGUAGE = "en"


# ---------------------------------------------------------------------------- #
#                                 Key Bindings                                 #
# ---------------------------------------------------------------------------- #
_C.KEY = CN()
# Key for tea. Set to -1 to use quick selection menu (press T).
_C.KEY.TEA = -1
# Key for carrot. Set to -1 to use quick selection menu (press T).
_C.KEY.CARROT = -1
# Keys for bottom rods
_C.KEY.BOTTOM_RODS = (1, 2, 3)
# Key for coffee. Set to -1 to use quick selection menu (press T).
_C.KEY.COFFEE = 4
# Key for digging tools like shovel or scoop.
_C.KEY.DIGGING_TOOL = 5
# Key for alcohol
_C.KEY.ALCOHOL = 6
# Key for the main rod. This is used for switching back to fishing rod when
# you're fishing with one rod with baits harvesting feature enabled.
_C.KEY.MAIN_ROD = 1
# Key for the spod rod
_C.KEY.SPOD_ROD = 7
# Bot , craft, and harvest quit shortcut (see pynput docs for custom keys).
# https://pynput.readthedocs.io/en/latest/keyboard.html#pynput.keyboard.Key
# _C.KEY.QUIT = "CTRL-C"
_C.KEY.QUIT = "CTRL-C"
# Friction brake (standalone) reset shortcut
_C.KEY.FRICTION_BRAKE_RESET = "g"
# Friction brake (standalone) quit shortcut, CTRL-C is not supported.
_C.KEY.FRICTION_BRAKE_QUIT = "h"
# Move (standalone) pause shortcut
_C.KEY.MOVE_PAUSE = "w"
# Move (standalone) quit shortcut, CTRL-C is not supported.
_C.KEY.MOVE_QUIT = "s"


# ---------------------------------------------------------------------------- #
#                             Player Stats Settings                            #
# ---------------------------------------------------------------------------- #
_C.STAT = CN()
# Minimum energy level before drinking coffee/harvesting baits (0.0-1.0)
_C.STAT.ENERGY_THRESHOLD = 0.74
# Minimum hunger level before consuming carrot (0.0-1.0)
_C.STAT.HUNGER_THRESHOLD = 0.5
# Minimum comfort level before consuming tea (0.0-1.0)
_C.STAT.COMFORT_THRESHOLD = 0.51
# Delay between tea drinks
_C.STAT.TEA_DRINK_DELAY = 300
# Maximum coffee drinks per fish fight.
# The script will stop and let the game stay idle after the limit is reached.
_C.STAT.COFFEE_LIMIT = 10
# Amount of coffee to consume per drink
_C.STAT.COFFEE_PER_DRINK = 1
# Delay between alcohol drinks
_C.STAT.ALCOHOL_DRINK_DELAY = 900
# Amount of alcohol to consume per drink
_C.STAT.ALCOHOL_PER_DRINK = 1


# ---------------------------------------------------------------------------- #
#                                 Bot Settings                                 #
# ---------------------------------------------------------------------------- #
_C.BOT = CN()
# Default launch options for bot command.
# They will be appended like this: "main bot {lanuch options}"
_C.BOT.LAUNCH_OPTIONS = ""
# Verify smtp connection on startup when email notification is enabled
_C.BOT.SMTP_VERIFICATION = True
# Detect snag while fishing
_C.BOT.SNAG_DETECTION = True
# Detect spooling while fishing
_C.BOT.SPOOLING_DETECTION = True
# Fishing line's retrieval sensitivity (lower = more sensitive) (0.0-1.0)
_C.BOT.SPOOL_CONFIDENCE = 0.98
# Random rod cast probability (0.0-1.0).
_C.BOT.RANDOM_CAST_PROBABILITY = 0.25
# Time to wait before recasting the spod rod
_C.BOT.SPOD_ROD_RECAST_DELAY = 1800
# Time to wait before changing current lure with a random one
_C.BOT.LURE_CHANGE_DELAY = 1800
# Time to wait before between pauses
_C.BOT.PAUSE_DELAY = 1800
# Duration of a single pause
_C.BOT.PAUSE_DURATION = 600
# Whether the Windows ClickLock is enabled.
# The time you need to hold down the mouse button must be set to "long".
_C.BOT.CLICK_LOCK = True


# ---------------------------------------------------------------------------- #
#                               Keepnet Settings                               #
# ---------------------------------------------------------------------------- #
_C.BOT.KEEPNET = CN()
# Capacity of the keepnet
_C.BOT.KEEPNET.CAPACITY = 100
# These fish will always be kept, regardless of whether or not they have been tagged.
# (options: mackerel, saithe, herring, squid, scallop, mussel, perch, shorthorn_sculpin)
_C.BOT.KEEPNET.WHITELIST = (
    "mackerel",
    "saithe",
    "herring",
    "squid",
    "scallop",
    "mussel",
)
# These fish will never be kept, regardless of whether or not they have been tagged.
# (options: mackerel, saithe, herring, squid, scallop, mussel, perch, shorthorn_sculpin)
_C.BOT.KEEPNET.BLACKLIST = ()
# Take a screenshot when capturing a fish with any tags below.
# Always take a screenshot if it's left empty.
# (options: green, yellow, blue, purple, pink)
_C.BOT.KEEPNET.SCREENSHOT_TAGS = ("yellow", "blue")
# Only keep the fish with any of the following tags
# (options: green, yellow, blue, purple, pink)
_C.BOT.KEEPNET.KEEP_TAGS = ("green", "yellow", "blue", "purple", "pink")


# ---------------------------------------------------------------------------- #
#                             Notification Settings                            #
# ---------------------------------------------------------------------------- #
_C.BOT.NOTIFICATION = CN()
# Email
_C.BOT.NOTIFICATION.EMAIL = "email@example.com"
_C.BOT.NOTIFICATION.PASSWORD = "password"
_C.BOT.NOTIFICATION.SMTP_SERVER = "smtp.gmail.com"

# Miaotixing
_C.BOT.NOTIFICATION.MIAO_CODE = "example"

# Discord
_C.BOT.NOTIFICATION.DISCORD_WEBHOOK_URL = ""

# Telegram
_C.BOT.NOTIFICATION.TELEGRAM_BOT_TOKEN = ""
_C.BOT.NOTIFICATION.TELEGRAM_CHAT_ID = -1


# ---------------------------------------------------------------------------- #
#                       Friction Brake Settings (for bot)                      #
# ---------------------------------------------------------------------------- #
_C.BOT.FRICTION_BRAKE = CN()
# Initial friction brake value (1-30)
_C.BOT.FRICTION_BRAKE.INITIAL = 29
# Maximum friction brake value (1-30)
_C.BOT.FRICTION_BRAKE.MAX = 30
# Delay before starting to adjust the friction brake after a fish is hooked
_C.BOT.FRICTION_BRAKE.START_DELAY = 2.0
# Delay between each friction brake increment
_C.BOT.FRICTION_BRAKE.INCREASE_DELAY = 1.0
# Delay after decreasing the friction brake
_C.BOT.FRICTION_BRAKE.DECREASE_DELAY = 1.0
# Sensitivity of friction brake detection
# (options: low, medium, high, very_high)
_C.BOT.FRICTION_BRAKE.SENSITIVITY = "high"

# ---------------------------------------------------------------------------- #
#                                Craft Settings                                #
# ---------------------------------------------------------------------------- #
_C.CRAFT = CN()
# Default launch options for craft command.
# They will be appended like this: "main craft {lanuch options}"
_C.CRAFT.LAUNCH_OPTIONS = ""


# ---------------------------------------------------------------------------- #
#                                 Move Settings                                #
# ---------------------------------------------------------------------------- #
_C.MOVE = CN()
# Default launch options for move command.
# They will be appended like this: "main move {lanuch options}"
_C.MOVE.LAUNCH_OPTIONS = ""


# ---------------------------------------------------------------------------- #
#                               Harvset Settings                               #
# ---------------------------------------------------------------------------- #
_C.HARVEST = CN()  # TODO: REMOVE THIS
# Default launch options for harvest command.
# They will be appended like this: "main harvest {lanuch options}"
_C.HARVEST.LAUNCH_OPTIONS = ""
# Open control panel between checks to reduce power consumption
_C.HARVEST.POWER_SAVING = False
# Delay time between each checks
_C.HARVEST.CHECK_DELAY = 32


# ---------------------------------------------------------------------------- #
#                     Friction Brake Settings (standalone)                     #
# ---------------------------------------------------------------------------- #
_C.FRICTION_BRAKE = CN()
# Default launch options for frictionbrake command.
# They will be appended like this: "main frictionbrake {lanuch options}"
_C.FRICTION_BRAKE.LAUNCH_OPTIONS = ""
# Initial friction brake value (1-30)
_C.FRICTION_BRAKE.INITIAL = 29
# Maximum friction brake value (1-30)
_C.FRICTION_BRAKE.MAX = 30
# Delay before starting to adjust the friction brake after a fish is hooked
_C.FRICTION_BRAKE.START_DELAY = 2.0
# Delay between each friction brake increment
_C.FRICTION_BRAKE.INCREASE_DELAY = 1.0
# Delay after decreasing the friction brake
_C.FRICTION_BRAKE.DECREASE_DELAY = 1.0
# Sensitivity of friction brake detection
# (options: low, medium, high, very_high)
_C.FRICTION_BRAKE.SENSITIVITY = "high"


_C.PROFILE = CN()
# ---------------------------------------------------------------------------- #
#                             Spin Fishing Profile                             #
# ---------------------------------------------------------------------------- #
_C.PROFILE.SPIN = CN()
# Profile description (optional)
_C.PROFILE.SPIN.DESCRIPTION = "Default spin fishing profile."
# Fishing mode
_C.PROFILE.SPIN.MODE = "spin"
# Type of special spin fishing technique to perform
# (options: normal, pause, lift)
_C.PROFILE.SPIN.TYPE = "normal"
# Profile-level launch options that will be merged with the global BOT.LAUNCH_OPTIONS
_C.PROFILE.SPIN.LAUNCH_OPTIONS = ""
# Power level for casting (0.0-5.0).
# 1: 0%, 2: ~25%, 3: ~50%, 4: ~75% 5: 100%+ (power cast), FYR.
# For instance, 2.5 cast_power_level equals to 37.5% casting power.
_C.PROFILE.SPIN.CAST_POWER_LEVEL = 5.0
# Time to wait before the lure touches the water and sinks after the rod is cast
_C.PROFILE.SPIN.CAST_DELAY = 6.0
# Duration to tighten the fishing line after the lure sinks
_C.PROFILE.SPIN.TIGHTEN_DURATION = 0.0
# Duration of retrieving the line or lifting the rod when performing
# special spin fishing techniques.
_C.PROFILE.SPIN.RETRIEVAL_DURATION = 0.0
# Time to wait after retrieving the line or lifting the rod when performing
# special spin fishing techniques.
_C.PROFILE.SPIN.RETRIEVAL_DELAY = 0.0
# Timeout for pause/lift mode, fall back to normal retrieval if the timeout is reached
_C.PROFILE.SPIN.RETRIEVAL_TIMEOUT = 256.0
# Hold down the Shift key when performing special spin fishing techniques
_C.PROFILE.SPIN.PRE_ACCELERATION = False
# Hold down the Shift key during fish fight
# (options: on, off, auto)
_C.PROFILE.SPIN.POST_ACCELERATION = "off"

_C.PROFILE.SPIN_WITH_PAUSE = CN()
_C.PROFILE.SPIN_WITH_PAUSE.DESCRIPTION = "Spin fishing with short pauses."
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
_C.PROFILE.SPIN_WITH_LIFT.DESCRIPTION = "Spin fishing with short lifts."
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
# Profile description (optional)
_C.PROFILE.BOTTOM.DESCRIPTION = "Default bottom fishing profile."
# Fishing mode
_C.PROFILE.BOTTOM.MODE = "bottom"
# Profile-level launch options that will be merged with the global BOT.LAUNCH_OPTIONS
_C.PROFILE.BOTTOM.LAUNCH_OPTIONS = ""
# Power level for casting, (0.0-5.0).
# 1: 0%, 2: ~25%, 3: ~50%, 4: ~75% 5: 100%+ (power cast), FYR.
# For instance, 2.5 cast_power_level equals to 37.5% casting power.
_C.PROFILE.BOTTOM.CAST_POWER_LEVEL = 5.0
# Time to wait before the lure touches the water and sinks after the rod is cast
_C.PROFILE.BOTTOM.CAST_DELAY = 4.0
# Hold down the Shift key during fish fight
# (options: on, off, auto)
_C.PROFILE.BOTTOM.POST_ACCELERATION = "off"
# Time to wait before checking fish bite on the next rod
_C.PROFILE.BOTTOM.CHECK_DELAY = 32.0
# Maximum allowed misses before recasting the rod
_C.PROFILE.BOTTOM.CHECK_MISS_LIMIT = 16
# Time to wait before putting down the rod
_C.PROFILE.BOTTOM.PUT_DOWN_DELAY = 0.0
# Whether to check the rods randomly or sequentially
_C.PROFILE.BOTTOM.RANDOM_ROD_SELECTION = True


# ---------------------------------------------------------------------------- #
#                      Marine / Wacky Rig Pirking Profile                      #
# ---------------------------------------------------------------------------- #
_C.PROFILE.PIRK = CN()
# Profile description (optional)
_C.PROFILE.PIRK.DESCRIPTION = "A marine fishing profile that perform pirking at the bottom layer for 34/41 holes in Norwegian Sea."
# Fishing mode
_C.PROFILE.PIRK.MODE = "pirk"
# Profile-level launch options that will be merged with the global BOT.LAUNCH_OPTIONS
_C.PROFILE.PIRK.LAUNCH_OPTIONS = ""
# Power level for casting, (0.0-5.0).
# 1: 0%, 2: ~25%, 3: ~50%, 4: ~75% 5: 100%+ (power cast), FYR.
# For instance, 2.5 cast_power_level equals to 37.5% casting power.
_C.PROFILE.PIRK.CAST_POWER_LEVEL = 1.0
# Time to wait before the lure touches the water and sinks after the rod is cast
_C.PROFILE.PIRK.CAST_DELAY = 4.0
# Maximum time allowed for sinking
_C.PROFILE.PIRK.SINK_TIMEOUT = 60.0
# Duration to tighten the line after sinking the lure
_C.PROFILE.PIRK.TIGHTEN_DURATION = 1.0
# Delay after opening reel to adjust lure depth, set this to 0 to recast the rod instead
_C.PROFILE.PIRK.DEPTH_ADJUST_DELAY = 4.0
# Durtion to tighten the line after opening reel for DEPTH_ADJUST_DELAY seconds
_C.PROFILE.PIRK.DEPTH_ADJUST_DURATION = 1.0
# Hold down the Ctrl key during pirking
_C.PROFILE.PIRK.CTRL = False
# Hold down the Shift key during pirking
_C.PROFILE.PIRK.SHIFT = False
# Duration of lifting the rod, set this to 0 if you want to wait instead of pirking.
_C.PROFILE.PIRK.PIRK_DURATION = 0.5
# Delay after lifting the rod.
_C.PROFILE.PIRK.PIRK_DELAY = 2.0
# Timeout for pirking.
# It will adjust the lure depth or recast the rod after the timeout is reached.
_C.PROFILE.PIRK.PIRK_TIMEOUT = 32.0
# Retrieve the fishing line during pirking.
_C.PROFILE.PIRK.PIRK_RETRIEVAL = False
# When a fish is hooked, check if the fish is still hooked after HOOK_DELAY seconds,
# continue pirking if not.
_C.PROFILE.PIRK.HOOK_DELAY = 0.5
# Hold down the Shift key during fish fight
# (options: on, off, auto)
_C.PROFILE.PIRK.POST_ACCELERATION = "auto"

_C.PROFILE.PIRK_WITH_RETRIEVAL = CN()
_C.PROFILE.PIRK_WITH_RETRIEVAL.DESCRIPTION = (
    "A marine fishing profile that retrieves the fishing line while parking."
)
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

_C.PROFILE.WACKY_RIG = CN()
_C.PROFILE.WACKY_RIG.DESCRIPTION = "A variation of marine fishing profile for pirking at the bottom layer at Ladoga Archipelago using wacky rig."
_C.PROFILE.WACKY_RIG.MODE = "pirk"
_C.PROFILE.WACKY_RIG.LAUNCH_OPTIONS = ""
_C.PROFILE.WACKY_RIG.CAST_POWER_LEVEL = 1.0
_C.PROFILE.WACKY_RIG.CAST_DELAY = 4.0
_C.PROFILE.WACKY_RIG.SINK_TIMEOUT = 45.0
_C.PROFILE.WACKY_RIG.TIGHTEN_DURATION = 1.0
_C.PROFILE.WACKY_RIG.DEPTH_ADJUST_DELAY = 4.0
_C.PROFILE.WACKY_RIG.DEPTH_ADJUST_DURATION = 1.0
_C.PROFILE.WACKY_RIG.CTRL = False
_C.PROFILE.WACKY_RIG.SHIFT = False
_C.PROFILE.WACKY_RIG.PIRK_DURATION = 1.5
_C.PROFILE.WACKY_RIG.PIRK_DELAY = 4.0
_C.PROFILE.WACKY_RIG.PIRK_TIMEOUT = 32.0
_C.PROFILE.WACKY_RIG.PIRK_RETRIEVAL = False
_C.PROFILE.WACKY_RIG.HOOK_DELAY = 0.5
_C.PROFILE.WACKY_RIG.POST_ACCELERATION = "auto"

# ---------------------------------------------------------------------------- #
#                            Marine Elevator Profile                           #
# ---------------------------------------------------------------------------- #
_C.PROFILE.ELEVATOR = CN()
# Profile description (optional)
_C.PROFILE.ELEVATOR.DESCRIPTION = (
    "A marine fishing profile for elevator while fishing/trolling."
)
# Fishing mode
_C.PROFILE.ELEVATOR.MODE = "elevator"
# Profile-level launch options that will be merged with the global BOT.LAUNCH_OPTIONS
_C.PROFILE.ELEVATOR.LAUNCH_OPTIONS = ""
# Power level for casting, (0.0-5.0).
# 1: 0%, 2: ~25%, 3: ~50%, 4: ~75% 5: 100%+ (power cast), FYR.
# For instance, 2.5 cast_power_level equals to 37.5% casting power.
_C.PROFILE.ELEVATOR.CAST_POWER_LEVEL = 1.0
# Time to wait before the lure touches the water and sinks after the rod is cast
_C.PROFILE.ELEVATOR.CAST_DELAY = 4.0
# Maximum time allowed for sinking
_C.PROFILE.ELEVATOR.SINK_TIMEOUT = 60.0
# Duration to tighten the line after sinking lure
_C.PROFILE.ELEVATOR.TIGHTEN_DURATION = 1.0
# Duration of retrieving the fishing line/opening the reel
_C.PROFILE.ELEVATOR.ELEVATE_DURATION = 4.0
# Delay after retrieving the fishing line/opening the reel
_C.PROFILE.ELEVATOR.ELEVATE_DELAY = 4.0
# Timeout for elevating.
# Retrieve/Drop will be reversed after the timeout is reached.
_C.PROFILE.ELEVATOR.ELEVATE_TIMEOUT = 40.0
# Lock / Unlocking the reel after elevating timed out to drop the lure level by level
_C.PROFILE.ELEVATOR.DROP = False
# When a fish is hooked, check if the fish is still hooked after HOOK_DELAY seconds,
# continue elevating if not.
_C.PROFILE.ELEVATOR.HOOK_DELAY = 0.5
# Hold down the Shift key during fish fight
# (options: on, off, auto)
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
#                             Float fishing profile                            #
# ---------------------------------------------------------------------------- #
_C.PROFILE.TELESCOPIC = CN()
# Profile description (optional)
_C.PROFILE.TELESCOPIC.DESCRIPTION = "Default float fishing profile for telescopic rod."
# Fishing mode
_C.PROFILE.TELESCOPIC.MODE = "telescopic"
# Profile-level launch options that will be merged with the global BOT.LAUNCH_OPTIONS
_C.PROFILE.TELESCOPIC.LAUNCH_OPTIONS = ""
# Power level for casting, (0.0-5.0).
# 1: 0%, 2: ~25%, 3: ~50%, 4: ~75% 5: 100%+ (power cast), FYR.
# For instance, 2.5 cast_power_level equals to 37.5% casting power.
_C.PROFILE.TELESCOPIC.CAST_POWER_LEVEL = 5.0
# Time to wait before the lure touches the water and sinks after the rod is cast
_C.PROFILE.TELESCOPIC.CAST_DELAY = 4.0
# Sensitivity of float detection
_C.PROFILE.TELESCOPIC.FLOAT_SENSITIVITY = 0.68
# Delay between fish bite checks
_C.PROFILE.TELESCOPIC.CHECK_DELAY = 1.0
# Time to wait before pulling a fish after the float status changed
_C.PROFILE.TELESCOPIC.PULL_DELAY = 0.5
# Recast rod after timed out, designed for flowing water maps.
_C.PROFILE.TELESCOPIC.DRIFT_TIMEOUT = 16.0
# Shape of the float camera, the script tracks the whole camrea window by default.
# (options: square, wide, tall)
_C.PROFILE.TELESCOPIC.CAMERA_SHAPE = "square"


_C.PROFILE.BOLOGNESE = CN()
# Profile description (optional)
_C.PROFILE.BOLOGNESE.DESCRIPTION = "Default float fishing profile for bolognese rod."
# Fishing mode
_C.PROFILE.BOLOGNESE.MODE = "bolognese"
# Profile-level launch options that will be merged with the global BOT.LAUNCH_OPTIONS
_C.PROFILE.BOLOGNESE.LAUNCH_OPTIONS = ""
# Power level for casting, (0.0-5.0).
# 1: 0%, 2: ~25%, 3: ~50%, 4: ~75% 5: 100%+ (power cast), FYR.
# For instance, 2.5 cast_power_level equals to 37.5% casting power.
_C.PROFILE.BOLOGNESE.CAST_POWER_LEVEL = 5.0
# Time to wait before the lure touches the water and sinks after the rod is cast
_C.PROFILE.BOLOGNESE.CAST_DELAY = 4.0
# Sensitivity of float detection
_C.PROFILE.BOLOGNESE.FLOAT_SENSITIVITY = 0.68
# Delay between fish bite checks
_C.PROFILE.BOLOGNESE.CHECK_DELAY = 1.0
# Time to wait before pulling a fish after the float status changed
_C.PROFILE.BOLOGNESE.PULL_DELAY = 0.5
# Recast rod after timed out, designed for flowing water maps.
_C.PROFILE.BOLOGNESE.DRIFT_TIMEOUT = 32.0
# Shape of the float camera, the script tracks the whole camrea window by default.
# (options: square, wide, tall)
# (Fall back to float camera detection mode if the window size is not supported.)
_C.PROFILE.BOLOGNESE.CAMERA_SHAPE = "square"
# Hold down the Shift key during fish fight
# (options: on, off, auto)
_C.PROFILE.BOLOGNESE.POST_ACCELERATION = "off"


_C.PROFILE.MATCH = CN()
# Profile description (optional)
_C.PROFILE.MATCH.DESCRIPTION = "Default float fishing profile for match rod."
# Fishing mode
_C.PROFILE.MATCH.MODE = "bolognese"
# Profile-level launch options that will be merged with the global BOT.LAUNCH_OPTIONS
_C.PROFILE.MATCH.LAUNCH_OPTIONS = ""
# Power level for casting, (0.0-5.0).
# 1: 0%, 2: ~25%, 3: ~50%, 4: ~75% 5: 100%+ (power cast), FYR.
# For instance, 2.5 cast_power_level equals to 37.5% casting power.
_C.PROFILE.MATCH.CAST_POWER_LEVEL = 5.0
# Time to wait before the lure touches the water and sinks after the rod is cast
_C.PROFILE.MATCH.CAST_DELAY = 4.0
# Sensitivity of float detection
_C.PROFILE.MATCH.FLOAT_SENSITIVITY = 0.68
# Delay between fish bite checks
_C.PROFILE.MATCH.CHECK_DELAY = 1.0
# Time to wait before pulling a fish after the float status changed
_C.PROFILE.MATCH.PULL_DELAY = 0.0
# Recast rod after timed out, designed for flowing water maps.
_C.PROFILE.MATCH.DRIFT_TIMEOUT = 64.0
# Shape of the float camera, the script tracks the whole camrea window by default.
# (options: square, wide, tall)
# (Fall back to float camera detection mode if the window size is not supported.)
_C.PROFILE.MATCH.CAMERA_SHAPE = "square"
# Hold down the Shift key during fish fight
# (options: on, off, auto)
_C.PROFILE.MATCH.POST_ACCELERATION = "off"


def get_cfg_defaults():
    """Get a yacs CfgNode object with default values for my_project."""
    # Return a clone so that the defaults will not be altered
    # This is for the "local variable" use pattern
    return _C.clone()
