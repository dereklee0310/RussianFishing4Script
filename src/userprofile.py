"""
Module for UserProfile class.

Todo: bottom fishing delay docstring
"""
class UserProfile():
    """Class for user profile encapsulation.
    """
    def __init__(self,
                 # general game settings
                 keepnet_limit: int,
                 fishes_in_keepnet: int, 
                 coffee_shortcut: str,
                 # general strategy settings
                 fishing_strategy: str, 
                 enable_release_unmarked: str, 
                 enable_drink_coffee: bool,
                 reel_type: str, 
                 # spin with pause
                 retrieval_duration: float, 
                 retrieval_delay: float, 
                 base_iteration: int,
                 # bottom
                 check_delay: float,
                 cast_power_level: int,
                 # marine
                 pirk_duration: float,
                 pirk_delay: float,
                 tighten_duration: float):
        self.keepnet_limit = keepnet_limit
        self.fishing_strategy = fishing_strategy
        self.enable_release_unmarked = enable_release_unmarked
        self.reel_type = reel_type
        self.enable_drink_coffee = enable_drink_coffee
        self.coffee_shortcut = coffee_shortcut
        self.fishes_in_keepnet = fishes_in_keepnet
        self.retrieval_duration = retrieval_duration
        self.retrieval_delay = retrieval_delay
        self.check_delay = check_delay
        self.cast_power_level = cast_power_level
        self.base_iteration = base_iteration
        self.pirk_duration = pirk_duration
        self.pirk_delay = pirk_delay
        self.tighten_duration = tighten_duration
        

"""Constructor method.

:param profile_name: title of the user profile
:type profile_name: str
:param reel_type: reel type
:type reel_type: str
:param fishing_strategy: spin, bottom, marine, etc
:type fishing_strategy: str
:param keep_strategy: all or marked
:type keep_strategy: str
:param fishes_in_keepnet: int
:type fishes_in_keepnet: str
#todo: duration and delay, ..., etc.
"""