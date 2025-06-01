from enum import Enum
from rich.console import Console
from rich.table import Table
from rich import box
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime, timezone


WEBHOOK_URL = "https://discordapp.com/api/webhooks/1250718168725454849/0l1B6QJk2Gsg0lJ-_VzMCc-uFPU5tX3gx36kRNLCt9sbxOhN5u4yzTtQvDeM6eH0jq8q"
ICON_URL = "https://i.ibb.co/RpLYcdkm/icon.png"

# Name                             | Int value | Hex code
# ---------------------------------|-----------|----------
# `BLURPLE`                        | 5793266   | `#5865F2`
# `GREEN`                          | 5763719   | `#57F287`
# `YELLOW`                         | 16705372  | `#FEE75C`
# `FUSCHIA`                        | 15418782  | `#EB459E`
# `RED`                            | 15548997  | `#ED4245`
# `WHITE`                          | 16777215  | `#FFFFFF`
# `BLACK`                          | 2303786   | `#23272A`


class DiscordColor(Enum):
    BLURPLE = 5793266
    GREEN = 5763719
    YELLOW = 16705372
    FUSCHIA = 15418782
    RED = 15548997
    WHITE = 16777215
    BLACK = 2303786


class DiscordNotification:
    def __init__(self, cfg, result):
        self.cfg = cfg
        self.result = result

    def build_raw_table(self) -> str:
        console = Console(width=100, force_terminal=True, color_system=None)
        table = Table("Field", "Value", box=box.DOUBLE, show_header=False)

        for key, value in self.result.items():
            table.add_row(key, str(value))

        with console.capture() as capture:
            console.print(table)

        return capture.get().strip()

    def send(self, color: DiscordColor):
        raw_table = self.build_raw_table()
        webhook = DiscordWebhook(
            url=self.cfg.NOTIFICATION.DISCORD_WEBHOOK_URL,
            username="RF4S",
            avatar_url=ICON_URL,
        )

        embed = DiscordEmbed(
            title="Running Result",
            color=color,
            timestamp=datetime.now(timezone.utc).isoformat(),
            footer={"text": "RF4S: Russian Fishing 4 Script", "icon_url": ICON_URL},
        )
        embed.description = f"```\n{raw_table}\n```"  # Wrap in code block

        webhook.add_embed(embed)
        response = webhook.execute()

        if response.status_code == 200:
            print("✅ Result successfully sent to Discord.")
        else:
            print(f"❌ Failed to send result to Discord: {response.text}")
