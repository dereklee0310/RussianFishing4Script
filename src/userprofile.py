"""
Module for UserProfile class.

Todo: fish count, bottom fishing delay
"""

class UserProfile():
    """Class for user profile encapsulation.
    """
    def __init__(self, profile_name: str, reel_name: str, fishing_strategy: str, 
                 release_strategy: str, current_fish_count: int):
        """Constructor method.

        :param profile_name: title of the user profile
        :type profile_name: str
        :param reel_name: reel name
        :type reel_name: str
        :param fishing_strategy: spin, bottom, marine, etc
        :type fishing_strategy: str
        :param release_strategy: None or marked
        :type release_strategy: str
        :param current_fish_count: int
        :type current_fish_count: str
        """
        self.profile_name = profile_name
        self.reel_name = reel_name
        self.fishing_strategy = fishing_strategy
        self.release_strategy = release_strategy
        self.current_fish_count = current_fish_count