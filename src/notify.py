"""
Module for sending notifications via Telegram.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from .http_client import HttpClient
from .config import get_telegram_config, get_proxy_config, TelegramConfig

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Class for sending Telegram notifications."""

    def __init__(self, telegram_config: Optional[TelegramConfig] = None):
        """
        Args:
            telegram_config: Telegram configuration. If None, loaded from environment.
        """
        self.config = telegram_config or get_telegram_config()
        self.http_client = HttpClient(proxy=get_proxy_config().get_telegram_proxy())
        self.base_url = f"https://api.telegram.org/bot{self.config.bot_token}"

        if not self.config.bot_token:
            logger.warning("Telegram bot token not configured. Notifications will be disabled.")
        elif not self.config.enable_notifications:
            logger.info("Telegram notifications disabled in configuration.")

    def _format_message_html(self, app: str, status: str, msg: str) -> str:
        date = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        # msg already contains per-account <blockquote> blocks built by checkin.py
        return (
            f"<b>{app}</b>  <i>{date}</i>\n"
            f"<b>{status}</b>\n\n"
            f"{msg}"
        )

    def _send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: str = 'HTML',
        disable_web_page_preview: bool = True
    ) -> bool:
        if not self.config.bot_token or not self.config.enable_notifications:
            return False
        if not chat_id:
            logger.warning("Chat ID not specified. Message not sent.")
            return False

        url = f"{self.base_url}/sendMessage"
        params = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': disable_web_page_preview,
        }

        try:
            response = self.http_client.request('GET', url, params=params)
            result = response.json()
            if result.get('ok'):
                logger.info(f"Notification sent to Telegram (chat_id: {chat_id})")
                return True
            error_description = result.get('description', 'Unknown error')
            logger.error(f"Telegram API error: {error_description}")
            self._log_error(f"Telegram API error: {error_description}")
            return False
        except Exception as e:
            logger.error(f"Exception sending notification: {e}")
            self._log_error(f"Exception sending Telegram notification: {e}")
            return False

    def send(
        self,
        chat_id: Optional[str],
        app: str = 'HoyoSignIn',
        status: str = '',
        msg: str = '',
        use_html: bool = True
    ) -> bool:
        """
        Send a notification.

        Args:
            chat_id: Target chat ID. Falls back to default_chat_id if None.
            app: Application name shown in the message header.
            status: Short status line.
            msg: Detailed message body.
            use_html: Whether to use HTML formatting.

        Returns:
            True if the message was delivered successfully.
        """
        if not self.config.enable_notifications:
            return False

        target_chat_id = chat_id or self.config.default_chat_id
        if not target_chat_id:
            logger.warning("No chat ID configured. Notification not sent.")
            return False

        logger.info(f'Check-in result: {status}\n\n{msg}')

        formatted = (
            self._format_message_html(app, status, msg)
            if use_html
            else f"{app}\n{status}\n{msg}"
        )
        return self._send_message(
            target_chat_id,
            formatted,
            parse_mode='HTML' if use_html else None,
        )

    def send_batch(self, notifications: List[Dict[str, Any]]) -> int:
        """Send multiple notifications. Returns the count of successful sends."""
        return sum(1 for n in notifications if self.send(**n))

    @staticmethod
    def _log_error(error_msg: str):
        """Append error to error_log.txt."""
        try:
            with open("../error_log.txt", "a", encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] {error_msg}\n")
        except Exception as e:
            logger.error(f"Error writing to error_log.txt: {e}")


# Backward-compatibility wrapper
class Notify:
    def __init__(self, telegram_chat_id: Optional[str] = None):
        self.telegram = TelegramNotifier()
        self.default_chat_id = telegram_chat_id

    def send(self, app: str = '', status: str = '', msg: str = '', **kwargs):
        if isinstance(msg, (list, dict)):
            msg = '\n\n'.join(str(m) for m in msg)
        if not kwargs.get('hide'):
            logger.info(f'Check-in result: {status}\n\n{msg}')
        chat_id = self.default_chat_id or self.telegram.config.default_chat_id
        self.telegram.send(chat_id=chat_id, app=app, status=status, msg=msg)
