"""
Module for UserProfile class.
"""
class UserProfile():
    """Class for user profile encapsulation.
    """
    def __init__(self,
                 # general settings
                 fishes_in_keepnet: int, 
                 enable_unmarked_release: bool, 
                 enable_coffee_drinking: bool,
                 enable_food_comfort_refill: bool,
                 enable_baits_harvesting: bool,
                 enable_email_sending: bool,
                 fishing_strategy: str, 
                 cast_power_level: float,
                 # spin with pause
                 retrieval_duration: float, 
                 retrieval_delay: float, 
                 base_iteration: int,
                 enable_acceleration: bool,
                 # bottom
                 check_delay: float,
                 # marine
                 pirk_duration: float,
                 pirk_delay: float,
                 tighten_duration: float):
        """Constructor method.
        """
        
        self.fishes_in_keepnet = fishes_in_keepnet
        self.enable_unmarked_release = enable_unmarked_release
        self.enable_coffee_drinking = enable_coffee_drinking
        self.enable_food_comfort_refill = enable_food_comfort_refill
        self.enable_baits_harvesting = enable_baits_harvesting
        self.enable_email_sending = enable_email_sending
        self.fishing_strategy = fishing_strategy
        self.cast_power_level = cast_power_level

        self.retrieval_duration = retrieval_duration
        self.retrieval_delay = retrieval_delay
        self.base_iteration = base_iteration
        self.enable_acceleration = enable_acceleration

        self.check_delay = check_delay
        
        self.pirk_duration = pirk_duration
        self.pirk_delay = pirk_delay
        self.tighten_duration = tighten_duration