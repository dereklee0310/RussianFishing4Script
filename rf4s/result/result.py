from dataclasses import dataclass

from rf4s.controller.timer import Timer
from rf4s.i18n import t

STOP_REASON_KEYS = {
    "Keepnet is full": "stop_keepnet_full",
    "Tackle is broken": "stop_tackle_broken",
    "Fishing line is at its end": "stop_line_at_end",
    "Coffee limit reached": "stop_coffee_limit",
    "Run out of bait": "stop_no_bait",
    "All rods are unavailable": "stop_no_rods",
    "Lure is broken": "stop_lure_broken",
    "Line is snagged": "stop_line_snagged",
    "Boat ticket expired": "stop_ticket_expired",
    "New boat ticket not found": "stop_no_ticket",
    "Favorite item not found": "stop_no_favorite",
    "Game disconnected": "stop_disconnected",
    "Terminated by user": "stop_terminated",
}


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

        stop_key = STOP_REASON_KEYS.get(msg)
        stop_reason = t(stop_key) if stop_key else msg

        return {
            t("result_stop_reason"): stop_reason,
            t("result_start_time"): timer.get_start_datetime(),
            t("result_end_time"): timer.get_cur_datetime(),
            t("result_running_time"): timer.get_running_time_str(),
            t("result_bite_rate"): bite_rate,
            t("result_total_fish"): self.total,
            t("result_kept_fish"): self.kept,
            t("result_kept_ratio"): kept_ratio,
            t("result_green_tag"): self.green,
            t("result_yellow_tag"): self.yellow,
            t("result_blue_tag"): self.blue,
            t("result_purple_tag"): self.purple,
            t("result_pink_tag"): self.pink,
            t("result_card"): self.card,
            t("result_gift"): self.gift,
            t("result_tea"): self.tea,
            t("result_carrot"): self.carrot,
            t("result_alcohol"): self.alcohol,
            t("result_coffee"): self.coffee,
            t("result_bait"): self.bait,
            t("result_ticket"): self.ticket,
        }


@dataclass
class CraftResult:
    success: int = 0
    fail: int = 0
    material: int = 0

    def as_dict(self) -> dict:
        return {
            t("result_success_crafts"): self.success,
            t("result_fail_crafts"): self.fail,
            t("result_materials"): self.material,
        }


@dataclass
class HarvestResult:
    tea: int = 0
    carrot: int = 0
    bait: int = 0

    def as_dict(self) -> dict:
        return {
            t("result_tea"): self.tea,
            t("result_carrot"): self.carrot,
            t("result_bait"): self.bait,
        }
