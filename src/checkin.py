"""
Main module for performing daily check-ins.
"""
import logging
from datetime import datetime
from typing import List, Dict, Any
try:
    from .config import (
        get_proxy_config, load_accounts,
        GAME_CONFIGS, AccountConfig, GameConfig,
        GAME_ROW_TEMPLATE, ACCOUNT_HEADER_TEMPLATE,
    )
    from .http_client import HttpClient
    from .notify import TelegramNotifier
    from .sign import Sign, SignResult
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.config import (
        get_proxy_config, load_accounts,
        GAME_CONFIGS, AccountConfig, GameConfig,
        GAME_ROW_TEMPLATE, ACCOUNT_HEADER_TEMPLATE,
    )
    from src.http_client import HttpClient
    from src.notify import TelegramNotifier
    from src.sign import Sign, SignResult

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

logger = logging.getLogger(__name__)


class _SafeDict(dict):
    """dict subclass that leaves unknown format keys in place instead of raising."""
    def __missing__(self, key: str) -> str:
        return '{' + key + '}'


def _fmt(template: str, **kwargs) -> str:
    return template.format_map(_SafeDict(kwargs))


class CheckInManager:
    """Orchestrates check-ins across all configured accounts and games."""

    def __init__(self):
        self.telegram = TelegramNotifier()
        self.accounts = load_accounts()
        self._signin_proxy = get_proxy_config().get_signin_proxy()
        logger.info(f"Loaded {len(self.accounts)} account(s)")

    # ── Check-in execution ────────────────────────────────────────────────────

    def run_check_in_for_game(
        self,
        game_name: str,
        game_config: GameConfig,
        account: AccountConfig,
    ) -> SignResult:
        """Perform check-in for a single game / account pair."""
        logger.info(f'Starting check-in: {game_name} / account {account.account_id}')
        try:
            http_client = HttpClient(proxy=self._signin_proxy)
            return Sign(account.cookies, game_name, game_config, http_client).run()

        except IndexError:
            cookie_fields = ["account_id", "cookie_token", "ltoken", "ltuid"]
            missing = [f for f in cookie_fields if f not in account.cookies]
            if missing:
                logger.error(f'Missing cookie fields: {", ".join(missing)}')
            return SignResult(
                game=game_name, success=False,
                status='Error: invalid cookies (see README troubleshooting)',
            )

        except Exception as e:
            logger.error(f"{game_name} / account {account.account_id}: {e}")
            return SignResult(game=game_name, success=False, status=f'Error: {e}')

    def run_check_in_for_account(self, account: AccountConfig) -> List[SignResult]:
        """Perform check-in for all enabled games on an account."""
        results = []
        for game_name in account.enabled_games:
            if game_name not in GAME_CONFIGS:
                logger.warning(f"Unknown game '{game_name}' — skipping.")
                continue
            results.append(self.run_check_in_for_game(game_name, GAME_CONFIGS[game_name], account))
        return results

    def run_all(self):
        """Perform check-in for every account, then send consolidated notifications."""
        if not self.accounts:
            logger.error("No accounts found. Please check your configuration.")
            return

        all_results = []
        for account in self.accounts:
            logger.info(f"Processing account: {account.account_id}")
            all_results.append({
                'account_id': account.account_id,
                'telegram_chat_id': account.telegram_chat_id,
                'results': self.run_check_in_for_account(account),
            })

        self._send_notifications(all_results)

    # ── Message formatting ────────────────────────────────────────────────────

    @staticmethod
    def _format_game_row(result: SignResult) -> str:
        """Format one game entry using GAME_ROW_TEMPLATE."""
        return _fmt(
            GAME_ROW_TEMPLATE,
            game=result.game,
            player_name=result.player_name,
            uid=result.uid,
            ar=result.ar,
            level=result.ar,
            region=result.region,
            day=result.day,
            reward_name=result.reward_name,
            reward_count=result.reward_count,
            status=result.status,
            status_icon=result.status_icon,
        )

    @staticmethod
    def _format_account_block(account_id: str, results: List[SignResult]) -> str:
        """
        Build an expandable <blockquote> for one account.

        Telegram shows the first ~3 lines when collapsed, so the structure is:
          Line 1 — account header  (e.g. "Account 12345: 3/3 succeeded")
          Line 2 — icon bar        (e.g. "✅ ✅ ✅")
          Line 3 — blank spacer
          ...game rows...
        """
        success_count = sum(1 for r in results if r.success)
        total_count = len(results)
        status_icons = ' '.join(r.status_icon for r in results)
        date = datetime.now().strftime('%d.%m.%Y')

        header = _fmt(
            ACCOUNT_HEADER_TEMPLATE,
            account_id=account_id,
            success_count=success_count,
            total_count=total_count,
            status_icons=status_icons,
            date=date,
        )

        game_rows = '\n\n'.join(CheckInManager._format_game_row(r) for r in results)
        body = f"{header}\n{status_icons}\n\n{game_rows}"
        return f"<blockquote expandable>{body}</blockquote>"

    # ── Notification dispatch ─────────────────────────────────────────────────

    def _send_notifications(self, all_results: List[Dict[str, Any]]):
        """Group results by chat_id and send one message per chat."""
        notifications_by_chat: Dict[str, List[str]] = {}
        total_success = 0
        total_games = 0

        for account_result in all_results:
            sign_results: List[SignResult] = account_result['results']
            if not sign_results:
                continue

            account_id = account_result['account_id']
            chat_id = account_result.get('telegram_chat_id') or self.telegram.config.default_chat_id
            if not chat_id:
                continue

            total_success += sum(1 for r in sign_results if r.success)
            total_games += len(sign_results)

            block = self._format_account_block(account_id, sign_results)
            notifications_by_chat.setdefault(chat_id, []).append(block)

        overall_status = f"Total: {total_success}/{total_games} succeeded"

        for chat_id, blocks in notifications_by_chat.items():
            self.telegram.send(
                chat_id=chat_id,
                app='HoyoSignIn',
                status=overall_status,
                msg='\n\n'.join(blocks),
            )
