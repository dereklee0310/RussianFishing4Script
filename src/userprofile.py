import configparser

class UserProfile():
    def __init__(self, profile_name, reel_name, fishing_strategy, release_strategy, current_fish_count):
        self.profile_name = profile_name
        self.reel_name = reel_name
        self.fishing_strategy = fishing_strategy
        self.release_strategy = release_strategy
        self.current_fish_count = current_fish_count