"""
Module for sending notifications via Telegram.
Uses modern Telegram API features.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from .http_client import HttpClient
from .config import get_telegram_config, TelegramConfig

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Class for sending Telegram notifications."""
    
    def __init__(self, telegram_config: Optional[TelegramConfig] = None):
        """
        Initialize notifications.
        
        Args:
            telegram_config: Telegram configuration. If None, loaded from environment.
        """
        self.config = telegram_config or get_telegram_config()
        self.http_client = HttpClient()
        self.base_url = f"https://api.telegram.org/bot{self.config.bot_token}"
        
        if not self.config.bot_token:
            logger.warning("Telegram bot token not configured. Notifications will be disabled.")
        elif not self.config.enable_notifications:
            logger.info("Telegram notifications disabled in configuration.")
    
    def _format_message_html(self, app: str, status: str, msg: str) -> str:
        """
        Format message using HTML.
        
        Args:
            app: Application name
            status: Operation status
            msg: Main message
            
        Returns:
            Formatted HTML message
        """
        date = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        
        html_message = f"""
<b>{app}</b>
<i>{date}</i>

<b>Status:</b> {status}

<b>Details:</b>
<blockquote expandable>{msg}</blockquote>
"""
        return html_message.strip()
    
    def _send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: str = 'HTML',
        disable_web_page_preview: bool = True
    ) -> bool:
        """
        Send message to Telegram.
        
        Args:
            chat_id: Chat ID for sending
            text: Message text
            parse_mode: Parse mode (HTML, Markdown)
            disable_web_page_preview: Disable link previews
            
        Returns:
            True if successful, False otherwise
        """
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
            'disable_web_page_preview': disable_web_page_preview
        }
        
        try:
            response = self.http_client.request('GET', url, params=params)
            result = response.json()
            
            if result.get('ok'):
                logger.info(f"Notification successfully sent to Telegram (chat_id: {chat_id})")
                return True
            else:
                error_description = result.get('description', 'Unknown error')
                logger.error(f"Error sending notification: {error_description}")
                self._log_error(f"Telegram API error: {error_description}")
                return False
                
        except Exception as e:
            logger.error(f"Exception sending notification: {e}")
            self._log_error(f"Exception sending Telegram notification: {str(e)}")
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
        Send notification.
        
        Args:
            chat_id: Chat ID for sending. If None, uses default_chat_id.
            app: Application name
            status: Operation status
            msg: Main message
            use_html: Use HTML formatting
            
        Returns:
            True if successfully sent
        """
        if not self.config.enable_notifications:
            logger.debug("Notifications disabled.")
            return False
        
        # Use provided chat_id or default
        target_chat_id = chat_id or self.config.default_chat_id
        
        if not target_chat_id:
            logger.warning("Chat ID not configured. Notification not sent.")
            return False
        
        # Log to console
        logger.info(f'Check-in result: {status}\n\n{msg}')
        
        # Format message
        if use_html:
            formatted_msg = self._format_message_html(app, status, msg)
        else:
            formatted_msg = f"{app}\n{status}\n{msg}"
        
        return self._send_message(target_chat_id, formatted_msg, parse_mode='HTML' if use_html else None)
    
    def send_batch(
        self,
        notifications: List[Dict[str, Any]]
    ) -> int:
        """
        Send multiple notifications.
        
        Args:
            notifications: List of dictionaries with keys: chat_id, app, status, msg
            
        Returns:
            Number of successfully sent notifications
        """
        success_count = 0
        for notification in notifications:
            if self.send(**notification):
                success_count += 1
        return success_count
    
    @staticmethod
    def _log_error(error_msg: str):
        """Write error to file."""
        try:
            with open("error_log.txt", "a", encoding='utf-8') as error_file:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                error_file.write(f"[{timestamp}] {error_msg}\n")
        except Exception as e:
            logger.error(f"Error writing to error_log.txt: {e}")


# For backward compatibility
class Notify:
    """Wrapper for backward compatibility with old code."""
    
    def __init__(self, telegram_chat_id: Optional[str] = None):
        """
        Initialize notifications.
        
        Args:
            telegram_chat_id: Telegram chat ID for this notification
        """
        self.telegram = TelegramNotifier()
        self.default_chat_id = telegram_chat_id
    
    def send(self, app: str = '', status: str = '', msg: str = '', **kwargs):
        """
        Send notification (backward compatibility).
        
        Args:
            app: Application name
            status: Status
            msg: Message
            **kwargs: Additional parameters
        """
        hide = kwargs.get('hide', '')
        
        if isinstance(msg, (list, dict)):
            msg = '\n\n'.join(str(m) for m in msg)
        
        if not hide:
            logger.info(f'Check-in result: {status}\n\n{msg}')
        
        chat_id = self.default_chat_id or self.telegram.config.default_chat_id
        self.telegram.send(chat_id=chat_id, app=app, status=status, msg=msg)
