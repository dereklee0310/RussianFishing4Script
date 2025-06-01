from dataclasses import dataclass

from rf4s.controller.timer import Timer


@dataclass
class Result:
    """Dummy result."""
    def as_dict(self) -> dict:
        return {}


@dataclass
class RF4SResult:
    tea: int = 0
    carrot: int = 0
    alcohol: int = 0
    coffee: int = 0
    bait: int = 0
    kept_fish: int = 0
    marked_fish: int = 0
    unmarked_fish: int = 0

    def as_dict(self, cause: str, timer: Timer) -> dict:
        total_fish_count = self.marked_fish + self.unmarked_fish
        # Will be 0 if total_fish_count = 0
        mark_ratio_str = (
            f"{self.marked_fish} / "
            f"{self.unmarked_fish} / "
            f"{int(self.marked_fish / max(1, total_fish_count) * 100)}%"
        )
        bite_rate_str = (
            f"{total_fish_count} / "
            f"{self.kept_fish} / "
            f"{(total_fish_count / (timer.get_running_time() / 3600)):.1f}/hr"
        )

        return {
            "Reason for termination": cause,
            "Start time": timer.get_start_datetime(),
            "End time": timer.get_cur_datetime(),
            "Running time": timer.get_running_time_str(),
            "Marked / Unmarked / Mark ratio": mark_ratio_str,
            "Total  / Kept     / Bite rate ": bite_rate_str,
            "Tea consumed": self.tea,
            "Carrot consumed": self.carrot,
            "Alcohol consumed": self.alcohol,
            "Coffee consumed": self.coffee,
            "Bait harvested": self.bait,
        }


@dataclass
class CraftResult:
    succes: int = 0
    fail: int = 0
    material: int = 0

    def as_dict(self) -> dict:
        return {
            "Successful crafts": self.succes,
            "Failed crafts": self.fail,
            "Materials used": self.material,
        }


@dataclass
class HarvestResult:
    tea: int = 0
    carrot: int = 0
    bait: int = 0

    def as_dict(self) -> dict:
        return {
            "Tea consumed": self.tea,
            "Carrot consumed": self.carrot,
            "Bait harvested": self.bait,
        }
