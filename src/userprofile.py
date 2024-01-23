"""
Module for UserProfile class.

Todo: bottom fishing delay
"""
class UserProfile():
    """Class for user profile encapsulation.
    """
    def __init__(self, 
                 profile_name: str, 
                 reel_type: str, 
                 fishing_strategy: str, 
                 keep_strategy: str, 
                 current_fish_count: int, 
                 duration: float, 
                 delay: float, 
                 check_delay_second: float,
                 cast_power_level: int):
        """Constructor method.

        :param profile_name: title of the user profile
        :type profile_name: str
        :param reel_type: reel type
        :type reel_type: str
        :param fishing_strategy: spin, bottom, marine, etc
        :type fishing_strategy: str
        :param keep_strategy: all or marked
        :type keep_strategy: str
        :param current_fish_count: int
        :type current_fish_count: str
        #todo: duration and delay
        """
        self.profile_name = profile_name
        self.reel_type = reel_type
        self.fishing_strategy = fishing_strategy
        self.keep_strategy = keep_strategy
        self.current_fish_count = current_fish_count
        self.duration = duration
        self.delay = delay
        self.check_delay_second = check_delay_second
        self.cast_power_level = cast_power_level