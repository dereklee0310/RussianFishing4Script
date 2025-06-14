import json
import logging
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from urllib import parse, request

from discord_webhook import DiscordEmbed, DiscordWebhook
from rich import box
from rich.console import Console
from rich.table import Table

logger = logging.getLogger("rich")

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
        logger.info("Sending Discord notification")
        raw_table = self.build_raw_table()
        webhook = DiscordWebhook(
            url=self.cfg.NOTIFICATION.DISCORD_WEBHOOK_URL,
            username="RF4S",
            avatar_url=ICON_URL,
        )

        embed = DiscordEmbed(
            title="Running Result",
            color=color.value,
            timestamp=datetime.now(timezone.utc).isoformat(),
            footer={"text": "RF4S: Russian Fishing 4 Script", "icon_url": ICON_URL},
        )
        embed.description = f"```\n{raw_table}\n```"  # Wrap in code block

        webhook.add_embed(embed)
        response = webhook.execute()

        if response.status_code == 200:
            logger.info("Result successfully sent to Discord")
        else:
            logger.error(f"Failed to send result to Discord: {response.text}")


class EmailNotification:
    def __init__(self, cfg, result):
        self.cfg = cfg
        self.result = result

    def send(self) -> None:
        """Send a notification email to the user's email address."""
        logger.info("Sending email notification")

        msg = MIMEMultipart()
        msg["Subject"] = "RF4S: Notice of Program Termination"
        msg["From"] = self.cfg.NOTIFICATION.EMAIL
        recipients = [self.cfg.NOTIFICATION.EMAIL]
        msg["To"] = ", ".join(recipients)

        text = ""
        for k, v in self.result.items():
            text += f"{k}: {v}\n"
        msg.attach(MIMEText(text))

        try:
            with smtplib.SMTP_SSL(self.cfg.NOTIFICATION.SMTP_SERVER, 465) as server:
                # smtp_server.ehlo()
                server.login(
                    self.cfg.NOTIFICATION.EMAIL, self.cfg.NOTIFICATION.PASSWORD
                )
                server.sendmail(
                    self.cfg.NOTIFICATION.EMAIL, recipients, msg.as_string()
                )
            logger.info("Email sent successfully")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")


class MiaotixingNotification:
    def __init__(self, cfg, result):
        self.cfg = cfg
        self.result = result

    def send(self) -> None:
        """Send a notification to the user's miaotixing service.

        :param result: running result
        :type result: dict
        """
        logger.info("Sending miaotixing notification")

        text = ""
        for k, v in self.result.items():
            text += f"{k}: {v}\n"

        url = "http://miaotixing.com/trigger?" + parse.urlencode(
            {"id": self.cfg.NOTIFICATION.MIAO_CODE, "text": text, "type": "json"}
        )

        with request.urlopen(url) as page:
            result = page.read()
            json_object = json.loads(result)
            if json_object["code"] == 0:
                logger.info("Miaotixing notification sent successfully")
            else:
                logger.error(
                    "Miaotixing notification with error code: %s\nDescription: %s",
                    str(json_object["code"]),
                    json_object["msg"],
                )
