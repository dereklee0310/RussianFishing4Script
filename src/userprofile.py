"""
Module for UserProfile class.
"""
class UserProfile():
    """Class for user profile encapsulation.
    """
    def __init__(self,
                 # general settings
                 fishes_in_keepnet: int, 
                 enable_release_unmarked: bool, 
                 enable_coffee_drinking: bool,
                 enable_food_comfort_refill: bool,
                 enable_baits_harvesting: bool,
                 fishing_strategy: str, 
                 # spin with pause
                 retrieval_duration: float, 
                 retrieval_delay: float, 
                 base_iteration: int,
                 # bottom
                 check_delay: float,
                 cast_power_level: float,
                 # marine
                 pirk_duration: float,
                 pirk_delay: float,
                 tighten_duration: float):
        """Constructor method.
        """
        
        self.fishes_in_keepnet = fishes_in_keepnet
        self.enable_release_unmarked = enable_release_unmarked
        self.enable_coffee_drinking = enable_coffee_drinking
        self.enable_food_comfort_refill = enable_food_comfort_refill
        self.enable_baits_harvesting = enable_baits_harvesting
        self.fishing_strategy = fishing_strategy

        self.retrieval_duration = retrieval_duration
        self.retrieval_delay = retrieval_delay
        self.base_iteration = base_iteration

        self.check_delay = check_delay
        self.cast_power_level = cast_power_level
        
        self.pirk_duration = pirk_duration
        self.pirk_delay = pirk_delay
        self.tighten_duration = tighten_duration