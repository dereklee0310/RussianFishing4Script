"""
Module for UserProfile class.

Todo: bottom fishing delay
"""

class UserProfile():
    """Class for user profile encapsulation.
    """
    def __init__(self, profile_name: str, reel_name: str, fishing_strategy: str, 
                 keep_strategy: str, current_fish_count: int, duration: float, delay: float):
        """Constructor method.

        :param profile_name: title of the user profile
        :type profile_name: str
        :param reel_name: reel name
        :type reel_name: str
        :param fishing_strategy: spin, bottom, marine, etc
        :type fishing_strategy: str
        :param keep_strategy: all or marked
        :type keep_strategy: str
        :param current_fish_count: int
        :type current_fish_count: str
        #todo: duration and delay
        """
        self.profile_name = profile_name
        self.reel_name = reel_name
        self.fishing_strategy = fishing_strategy
        self.keep_strategy = keep_strategy
        self.current_fish_count = current_fish_count
        self.duration = duration
        self.delay = delay