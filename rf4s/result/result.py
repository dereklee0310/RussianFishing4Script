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
    kept: int = 0
    total: int = 0
    green: int = 0
    yellow: int = 0
    blue: int = 0
    purple: int = 0
    pink: int = 0

    def as_dict(self, msg: str, timer: Timer) -> dict:
        # Will be 0 if total_fish_count = 0
        kept_ratio = f"{int(self.kept / max(1, self.total) * 100)}%"
        bite_rate = f"{int((self.total / (timer.get_running_time() / 3600)))}/hr"

        return {
            "Stop reason": msg,
            "Start time": timer.get_start_datetime(),
            "End time": timer.get_cur_datetime(),
            "Running time": timer.get_running_time_str(),
            "Bite rate": bite_rate,
            "Total fish": self.total,
            "Kept fish": self.kept,
            "Kept ratio": kept_ratio,
            "Green tag fish": self.green,
            "Yellow tag fish": self.yellow,
            "Blue tag fish": self.blue,
            "Purple tag fish": self.purple,
            "Pink tag fish": self.pink,
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
