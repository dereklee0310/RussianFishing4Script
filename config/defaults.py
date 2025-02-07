"""Default yacs config node."""

from yacs.config import CfgNode as CN

_C = CN()
_C.VERSION = 1.0



_C.SCRIPT = CN()
_C.SCRIPT.LAUNCH_OPTIONS = ""
_C.SCRIPT.CONFIG_CONFIRMATION = True
_C.SCRIPT.SMTP_VALIDATION = True
_C.SCRIPT.IMAGE_VALIDATION = True


_C.GENERAL = CN()
_C.GENERAL.LANGUAGE = "en"
_C.GENERAL.KEEPNET_CAPACITY = 100
_C.GENERAL.SPOOL_CONFIDENCE = 0.985
_C.GENERAL.KEEP_FISH_DELAY = 1.0
_C.GENERAL.SNAG_DETECTION = True
_C.GENERAL.RANDOM_ROD_SELECTION = True
_C.GENERAL.SPOD_ROD_RECAST_DELAY = 1800 # 30 minutes
_C.GENERAL.LURE_CHANGE_DELAY = 1800 # 30 minutes
_C.GENERAL.KEEPNET_FULL_ACTION = "quit"
_C.GENERAL.ALARM_SOUND = "../static/sound/guitar.wav"
_C.GENERAL.RELEASE_WHITELIST = ("mackerel", "saithe", "herring", "squid", "scallop", "mussel")


_C.KEY = CN()
_C.KEY.TEA = -1
_C.KEY.CARROT = -1
_C.KEY.RODS = (1, 2, 3)
_C.KEY.COFFEE = 4
_C.KEY.DIGGING_TOOL = 5
_C.KEY.ALCOHOL = 6
_C.KEY.MAIN_ROD = 1
_C.KEY.SPOD_ROD = 7
_C.KEY.QUIT = "CTRL-C"


_C.STAT = CN()
_C.STAT.ENERGY_THRESHOLD = 0.74
_C.STAT.HUNGER_THRESHOLD = 0.5
_C.STAT.COMFORT_THRESHOLD = 0.51
_C.STAT.COFFEE_LIMIT = 10
_C.STAT.COFFEE_PER_DRINK = 1
_C.STAT.ALCOHOL_DELAY = 900 # 15 minutes
_C.STAT.ALCOHOL_PER_DRINK = 1


_C.FRICTION_BRAKE = CN()
_C.FRICTION_BRAKE.INITIAL = 29
_C.FRICTION_BRAKE.MAX = 30
_C.FRICTION_BRAKE.START_DELAY = 2.0
_C.FRICTION_BRAKE.INCREASE_DELAY = 1.0


_C.PAUSE = CN()
_C.PAUSE.DELAY = 1800 # 30 minutes
_C.PAUSE.DURATION = 600 # 10 minutes


_C.MODE = CN()
# ---------------------------------------------------------------------------- #
#                               Spin Fishing Mode                              #
# ---------------------------------------------------------------------------- #
_C.MODE.SPIN = CN()
_C.MODE.SPIN.CAST_POWER_LEVEL = 5.0
_C.MODE.SPIN.CAST_DELAY = 6.0
_C.MODE.SPIN.TIGHTENING_DURATION = 1.0
_C.MODE.SPIN.RETRIEVE_DURATION = 1.1
_C.MODE.SPIN.RETRIEVE_DELAY = 3.0
_C.MODE.SPIN.PRE_ACCELERATION = False
_C.MODE.SPIN.POST_ACCELERATION = "off"


# ---------------------------------------------------------------------------- #
#                              Bottom Fishing Mode                             #
# ---------------------------------------------------------------------------- #
_C.MODE.BOTTOM = CN()
_C.MODE.BOTTOM.CAST_POWER_LEVEL = 5.0
_C.MODE.BOTTOM.CAST_DELAY = 4.0
_C.MODE.BOTTOM.ACCELERATION = "off"
_C.MODE.BOTTOM.CHECK_DELAY = 32.0

# ---------------------------------------------------------------------------- #
#                        Marine / Wakey Rig Pirking Mode                       #
# ---------------------------------------------------------------------------- #
_C.MODE.PIRK = CN()
_C.MODE.PIRK.CAST_POWER_LEVEL = 1.0
_C.MODE.PIRK.CAST_DELAY = 4.0
_C.MODE.PIRK.SINK_TIMEOUT = 60.0
_C.MODE.PIRK.TIGHTEN_DURATION = 1.0
_C.MODE.PIRK.PIRK_DURATION = 0.5
_C.MODE.PIRK.PIRK_DELAY = 2.0
_C.MODE.PIRK.PIRK_TIMEOUT = 32.0
_C.MODE.PIRK.PIRK_TIMEOUT_ACTION = "adjust"
_C.MODE.PIRK.ACCELERATION = "auto"
_C.MODE.PIRK.HOOK_DELAY = 0.0
_C.MODE.PIRK.TROLLING = "off"

# ---------------------------------------------------------------------------- #
#                             Marine Elevator Mode                             #
# ---------------------------------------------------------------------------- #
_C.MODE.ELEVATOR = CN()
_C.MODE.ELEVATOR.CAST_POWER_LEVEL = 1.0
_C.MODE.ELEVATOR.CAST_DELAY = 4.0
_C.MODE.ELEVATOR.SINK_TIMEOUT = 60.0
_C.MODE.ELEVATOR.TIGHTEN_DURATION = 1.0
_C.MODE.ELEVATOR.ELEVATE_DURATION = 4.0
_C.MODE.ELEVATOR.ELEVATE_DELAY = 4.0
_C.MODE.ELEVATOR.ELEVEATE_TIMEOUT = 40.0
_C.MODE.ELEVATOR.ACCELERATION = "auto"
_C.MODE.ELEVATOR.HOOK_DELAY = 0.0
_C.MODE.ELEVATOR.TROLLING = "off"


# ---------------------------------------------------------------------------- #
#                              Float Fishing Mode                              #
# ---------------------------------------------------------------------------- #
_C.MODE.FLOAT = CN()
_C.MODE.FLOAT.CAST_POWER_LEVEL = 5.0
_C.MODE.FLOAT.CAST_DELAY = 4.0
_C.MODE.FLOAT.FLOAT_SENSITIVITY = 0.65
_C.MODE.FLOAT.CHECK_DELAY = 1.0
_C.MODE.FLOAT.PULL_DELAY = 0.5
_C.MODE.FLOAT.DRIFTING_TIMEOUT = 16.0
_C.MODE.FLOAT.CAMERA_SHAPE = "square"



def get_cfg_defaults():
    """Get a yacs CfgNode object with default values for my_project."""
    # Return a clone so that the defaults will not be altered
    # This is for the "local variable" use pattern
    return _C.clone()
