import json
import smtplib
from datetime import datetime, timezone
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from pathlib import Path
from urllib import parse, request

import requests
from discord_webhook import DiscordEmbed, DiscordWebhook
from rich import box
from rich.console import Console
from rich.table import Table
from yacs.config import CfgNode as CN

from rf4s.controller import logger
from rf4s.i18n import t

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


def send_screenshot(cfg: CN, filepath: Path) -> None:
    if cfg.ARGS.DISCORD:
        DiscordNotification(cfg).send_screenshot(filepath)
    if cfg.ARGS.EMAIL:
        EmailNotification(cfg).send_screenshot(filepath)
    if cfg.ARGS.MIAOTIXING:
        MiaotixingNotification(cfg).send_screenshot(filepath)
    if cfg.ARGS.TELEGRAM:
        TelegramNotification(cfg).send_screenshot(filepath)


def send_result(cfg: CN, result: dict) -> None:
    if cfg.ARGS.DISCORD:
        DiscordNotification(cfg).send_result(result)
    if cfg.ARGS.EMAIL:
        EmailNotification(cfg).send_result(result)
    if cfg.ARGS.MIAOTIXING:
        MiaotixingNotification(cfg).send_result(result)
    if cfg.ARGS.TELEGRAM:
        TelegramNotification(cfg).send_result(result)


class DiscordColor(Enum):
    BLURPLE = 5793266
    GREEN = 5763719
    YELLOW = 16705372
    FUSCHIA = 15418782
    RED = 15548997
    WHITE = 16777215
    BLACK = 2303786


class DiscordNotification:
    def __init__(self, cfg):
        self.cfg = cfg

    def _get_raw_result_table(self, result: dict) -> str:
        console = Console(width=100, force_terminal=True, color_system=None)
        table = Table(box=box.HEAVY, show_header=False)

        for key, value in result.items():
            table.add_row(key, str(value))

        with console.capture() as capture:
            console.print(table)
        return capture.get().strip()

    def _get_webhook(self) -> DiscordWebhook:
        return DiscordWebhook(
            url=self.cfg.BOT.NOTIFICATION.DISCORD_WEBHOOK_URL,
            username="RF4S",
            avatar_url=ICON_URL,
        )

    def _get_embed(self, title: str) -> DiscordEmbed:
        return DiscordEmbed(
            title=title,
            color=DiscordColor.BLURPLE.value,  # TODO: dynamic color
            timestamp=datetime.now(timezone.utc).isoformat(),
            footer={"text": "RF4S: Russian Fishing 4 Script", "icon_url": ICON_URL},
        )

    def _send_webhook(self, webhook: DiscordWebhook) -> None:
        response = webhook.execute()
        if response.status_code == 200:
            logger.info(t("notification.sent_success"))
        else:
            logger.error(t("notification.send_failed", error=response.text))

    def send_result(self, result: dict):
        logger.info(t("notification.discord.sending_result"))
        webhook = self._get_webhook()
        embed = self._get_embed(t("notification.discord.running_result"))

        # Wrap it with a code block
        embed.description = f"```\n{self._get_raw_result_table(result)}\n```"
        webhook.add_embed(embed)
        self._send_webhook(webhook)

    def send_screenshot(self, filepath: Path):
        logger.info(t("notification.discord.sending_screenshot"))
        webhook = self._get_webhook()
        embed = self._get_embed(t("notification.discord.catch"))
        with open(filepath, "rb") as f:
            webhook.add_file(file=f.read(), filename=filepath.name)
        embed.set_image(url=f"attachment://{filepath.name}")
        webhook.add_embed(embed)
        self._send_webhook(webhook)


class EmailNotification:
    def __init__(self, cfg):
        self.cfg = cfg

    def _get_msg(self, subject: str) -> MIMEMultipart:
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = self.cfg.BOT.NOTIFICATION.EMAIL
        recipients = [self.cfg.BOT.NOTIFICATION.EMAIL]
        msg["To"] = ", ".join(recipients)
        return msg

    def _send_email(self, msg: MIMEMultipart) -> None:
        try:
            with smtplib.SMTP_SSL(self.cfg.BOT.NOTIFICATION.SMTP_SERVER, 465) as server:
                # smtp_server.ehlo()
                server.login(
                    self.cfg.BOT.NOTIFICATION.EMAIL, self.cfg.BOT.NOTIFICATION.PASSWORD
                )
                server.sendmail(
                    self.cfg.BOT.NOTIFICATION.EMAIL,
                    [self.cfg.BOT.NOTIFICATION.EMAIL],
                    msg.as_string(),
                )
            logger.info(t("notification.sent_success"))
        except Exception as e:
            logger.error(t("notification.send_failed", error=str(e)))

    def send_result(self, result: dict) -> None:
        """Send a notification email to the user's email address."""
        logger.info(t("notification.email.sending_result"))
        msg = self._get_msg(t("notification.email.subject_result"))
        text = ""
        for k, v in result.items():
            text += f"{k}: {v}\n"
        msg.attach(MIMEText(text))
        self._send_email(msg)

    def send_screenshot(self, filepath: Path) -> None:
        """Send a notification email to the user's email address."""
        logger.info(t("notification.email.sending_screenshot"))
        msg = self._get_msg(t("notification.email.subject_catch"))

        with open(filepath, "rb") as f:
            img = MIMEImage(f.read(), name=filepath.name)
        img.add_header("Content-Disposition", "attachment", filename=filepath.name)
        msg.attach(img)
        self._send_email(msg)


class MiaotixingNotification:
    def __init__(self, cfg):
        self.cfg = cfg

    def send_result(self, result: dict) -> None:
        """Send a notification to the user's miaotixing service.

        :param result: running result
        :type result: dict
        """
        logger.info(t("notification.miaotixing.sending_result"))

        text = ""
        for k, v in result.items():
            text += f"{k}: {v}\n"

        url = "http://miaotixing.com/trigger?" + parse.urlencode(
            {"id": self.cfg.BOT.NOTIFICATION.MIAO_CODE, "text": text, "type": "json"}
        )

        with request.urlopen(url) as page:
            result = page.read()
            json_object = json.loads(result)
            if json_object["code"] == 0:
                logger.info(t("notification.miaotixing.sent_success"))
            else:
                logger.error(
                    t("notification.miaotixing.error",
                      code=str(json_object["code"]),
                      msg=json_object["msg"])
                )

    def send_screenshot(self, _: Path) -> None:
        logger.error(t("notification.miaotixing.no_image"))


class TelegramNotification:
    def __init__(self, cfg):
        self.cfg = cfg

    def _check_response_status(self, response: requests.Response) -> None:
        if response.status_code == 200:
            logger.info(t("notification.sent_success"))
        else:
            logger.error(t("notification.send_failed", error=response.text))

    def send_result(self, result: dict) -> None:
        logger.info(t("notification.telegram.sending_result"))
        # Send a simple message, no need for fancy python-telegram-bot
        text = f"*{t('notification.telegram.running_result')}*\n```\n"
        for k, v in result.items():
            text += f"{k}: {v}\n"
        text += "```"
        payload = {
            "chat_id": self.cfg.BOT.NOTIFICATION.TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "MarkdownV2",
        }
        response = requests.post(
            "https://api.telegram.org/"
            f"bot{self.cfg.BOT.NOTIFICATION.TELEGRAM_BOT_TOKEN}/sendMessage",
            json=payload,
        )
        self._check_response_status(response)

    def send_screenshot(self, filepath: Path) -> None:
        logger.info(t("notification.telegram.sending_screenshot"))
        with open(filepath, "rb") as img:
            files = {"photo": img}
            payload = {
                "chat_id": self.cfg.BOT.NOTIFICATION.TELEGRAM_CHAT_ID,
                "parse_mode": "MarkdownV2",
            }
            response = requests.post(
                "https://api.telegram.org/"
                f"bot{self.cfg.BOT.NOTIFICATION.TELEGRAM_BOT_TOKEN}/sendPhoto",
                data=payload,
                files=files,
            )
        self._check_response_status(response)
