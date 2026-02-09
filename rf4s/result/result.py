from dataclasses import dataclass

from rf4s.controller.timer import Timer
from rf4s.i18n import t


@dataclass
class Result:
    """Dummy result."""

    def as_dict(self) -> dict:
        return {}


@dataclass
class BotResult:
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
    card: int = 0
    gift: int = 0
    ticket: int = 0

    def as_dict(self, msg: str, timer: Timer) -> dict:
        # Will be 0 if total_fish_count = 0
        try:
            kept_ratio = f"{int(self.kept / self.total * 100)}%"
            bite_rate = f"{int((self.total / (timer.get_running_time() / 3600)))}/hr"
        except ZeroDivisionError:
            kept_ratio = "0%"
            bite_rate = "0/hr"

        return {
            t("result.stop_reason"): msg,
            t("result.start_time"): timer.get_start_datetime(),
            t("result.end_time"): timer.get_cur_datetime(),
            t("result.running_time"): timer.get_running_time_str(),
            t("result.bite_rate"): bite_rate,
            t("result.total_fish"): self.total,
            t("result.kept_fish"): self.kept,
            t("result.kept_ratio"): kept_ratio,
            t("result.green_tag"): self.green,
            t("result.yellow_tag"): self.yellow,
            t("result.blue_tag"): self.blue,
            t("result.purple_tag"): self.purple,
            t("result.pink_tag"): self.pink,
            t("result.card"): self.card,
            t("result.gift"): self.gift,
            t("result.tea_consumed"): self.tea,
            t("result.carrot_consumed"): self.carrot,
            t("result.alcohol_consumed"): self.alcohol,
            t("result.coffee_consumed"): self.coffee,
            t("result.bait_harvested"): self.bait,
            t("result.ticket_used"): self.ticket,
        }


@dataclass
class CraftResult:
    success: int = 0
    fail: int = 0
    material: int = 0

    def as_dict(self) -> dict:
        return {
            t("result.successful_crafts"): self.success,
            t("result.failed_crafts"): self.fail,
            t("result.materials_used"): self.material,
        }


@dataclass
class HarvestResult:
    tea: int = 0
    carrot: int = 0
    bait: int = 0

    def as_dict(self) -> dict:
        return {
            t("result.harvest_tea"): self.tea,
            t("result.harvest_carrot"): self.carrot,
            t("result.harvest_bait"): self.bait,
        }
