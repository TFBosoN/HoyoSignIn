"""
Module for secure configuration and secrets management.
Uses Pydantic for validation and type hints.
"""
import os
import logging
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, validator
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class GameConfig(BaseModel):
    """Configuration for a specific game."""
    log_level: int = logging.INFO
    lang: str = 'en-us'
    os_act_id: str
    os_referer_url: str
    os_reward_url: str
    os_role_url: str
    os_info_url: str
    os_sign_url: str
    wb_user_agent: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'
    os_headers: Dict[str, str] = Field(default_factory=dict)

    @validator('os_headers', pre=True)
    def parse_headers(cls, v):
        if isinstance(v, str):
            return {}
        return v or {}


class AccountConfig(BaseModel):
    """Configuration for a single account."""
    account_id: str
    cookies: str
    telegram_chat_id: Optional[str] = None
    enabled_games: List[str] = Field(default_factory=lambda: ['Genshin', 'HSR', 'HI3', 'ToT', 'ZZZ'])

    @validator('cookies')
    def validate_cookies(cls, v):
        # ltoken_v2 is valid alongside ltoken
        has_ltoken = 'ltoken' in v
        required_fields = ['account_id', 'cookie_token', 'ltuid']
        missing = [f for f in required_fields if f not in v]
        if not has_ltoken:
            missing.append('ltoken or ltoken_v2')
        if missing:
            raise ValueError(f"Missing required cookie fields: {', '.join(missing)}")
        return v


class TelegramConfig(BaseModel):
    """Telegram bot configuration."""
    bot_token: Optional[str] = None
    default_chat_id: Optional[str] = None
    enable_notifications: bool = True

    @validator('bot_token')
    def validate_bot_token(cls, v):
        if v and not v.strip():
            return None
        return v


class ProxyConfig(BaseModel):
    """Proxy configuration with separate flags for signin and Telegram traffic."""
    use_proxy_signin: bool = False
    use_proxy_telegram: bool = False
    proxy_data: Optional[str] = None

    def _build_proxy_dict(self) -> Optional[Dict[str, str]]:
        if not self.proxy_data:
            return None
        socks_proxy = f'socks5://{self.proxy_data}'
        return {'http': socks_proxy, 'https': socks_proxy}

    def get_signin_proxy(self) -> Optional[Dict[str, str]]:
        """Return proxy dict for game sign-in requests, or None."""
        if not self.use_proxy_signin:
            return None
        return self._build_proxy_dict()

    def get_telegram_proxy(self) -> Optional[Dict[str, str]]:
        """Return proxy dict for Telegram notification requests, or None."""
        if not self.use_proxy_telegram:
            return None
        return self._build_proxy_dict()


class AppSettings(BaseSettings):
    """
    Main application settings loaded from environment / .env file.

    Proxy env vars:
      PROXY_DATA          — socks5 address, e.g. user:pass@host:port or host:port
      USE_PROXY_SIGNIN    — true/false, route game sign-in calls through the proxy
      USE_PROXY_TELEGRAM  — true/false, route Telegram notification calls through the proxy
      USE_PROXY           — true/false, legacy flag that enables proxy for BOTH channels
    """
    user_agent: Optional[str] = None
    proxy_data: Optional[str] = None
    use_proxy_signin: bool = False
    use_proxy_telegram: bool = False
    use_proxy: bool = False  # legacy: enables proxy for both channels
    bot_token: Optional[str] = None
    default_chat_id: Optional[str] = None

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False


# ── Message templates ────────────────────────────────────────────────────────
# Edit these strings to customise how Telegram notifications look.
# Templates use Python str.format() — unknown variable names are left as-is.
# Supports standard Telegram HTML tags: <b>, <i>, <code>, <u>, <s>, <blockquote>.
#
# GAME_ROW_TEMPLATE — rendered once per game per account.
# Available variables:
#   {game}          — "Genshin" | "HSR" | "HI3" | "ToT" | "ZZZ"
#   {player_name}   — in-game nickname
#   {uid}           — game UID
#   {ar} / {level}  — Adventure Rank / Trailblaze Level / Captain Level
#   {region}        — server region name
#   {day}           — total sign-in days including today
#   {reward_name}   — today's reward item name
#   {reward_count}  — today's reward item quantity
#   {status}        — "OK" | "Already done!" | "Please check in manually" | "Error: …"
#   {status_icon}   — "✅" (success / already done) | "❌" (error)
#
GAME_ROW_TEMPLATE = (
    "{game}: {player_name} <code>{uid}</code>\n"
    "[Day {day}]: {reward_name} × {reward_count} — {status}"
)

# ACCOUNT_HEADER_TEMPLATE — first line(s) of each account's blockquote.
# Telegram shows the first ~3 lines when the quote is collapsed, so put
# the most useful summary information here.
# Available variables:
#   {account_id}    — account identifier from your .env
#   {success_count} — games that succeeded (new sign-in or already done)
#   {total_count}   — total enabled games for this account
#   {status_icons}  — e.g. "✅ ✅ ❌" — one icon per game in order
#   {date}          — today's date  DD.MM.YYYY
#
ACCOUNT_HEADER_TEMPLATE = "Account {account_id}: {success_count}/{total_count} succeeded"

# ─────────────────────────────────────────────────────────────────────────────

# Global game configurations
GAME_CONFIGS: Dict[str, GameConfig] = {
    "HI3": GameConfig(
        os_act_id='e202110291205111',
        os_referer_url='https://act.hoyolab.com/bbs/event/signin-bh3/index.html?act_id=e202110291205111',
        os_reward_url='https://sg-public-api.hoyolab.com/event/mani/home?lang=en-us&act_id=e202110291205111',
        os_role_url='https://api-os-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz=bh3_global',
        os_info_url='https://sg-public-api.hoyolab.com/event/mani/info?lang=en-us&act_id=e202110291205111',
        os_sign_url='https://sg-public-api.hoyolab.com/event/mani/sign?lang=en-us',
    ),
    "Genshin": GameConfig(
        os_act_id='e202102251931481',
        os_referer_url='https://act.hoyolab.com/ys/event/signin-sea-v3/e202102251931481.html?act_id=e202102251931481',
        os_reward_url='https://sg-hk4e-api.hoyolab.com/event/sol/home?lang=en-us&act_id=e202102251931481',
        os_role_url='https://api-os-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz=hk4e_global',
        os_info_url='https://sg-hk4e-api.hoyolab.com/event/sol/info?lang=en-us&act_id=e202102251931481',
        os_sign_url='https://sg-hk4e-api.hoyolab.com/event/sol/sign?lang=en-us',
    ),
    "ToT": GameConfig(
        os_act_id='e202308141137581',
        os_referer_url='https://act.hoyolab.com/bbs/event/signin/nxx/index.html?act_id=e202308141137581',
        os_reward_url='https://sg-public-api.hoyolab.com/event/luna/os/home?lang=en-us&act_id=e202308141137581',
        os_role_url='https://api-os-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz=nxx_global',
        os_info_url='https://sg-public-api.hoyolab.com/event/luna/os/info?lang=en-us&act_id=e202308141137581',
        os_sign_url='https://sg-public-api.hoyolab.com/event/luna/os/sign?lang=en-us',
    ),
    "HSR": GameConfig(
        os_act_id='e202303301540311',
        os_referer_url='https://act.hoyolab.com/bbs/event/signin/hkrpg/e202303301540311.html?act_id=e202303301540311',
        os_reward_url='https://sg-public-api.hoyolab.com/event/luna/os/home?lang=en-us&act_id=e202303301540311',
        os_role_url='https://api-os-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz=hkrpg_global',
        os_info_url='https://sg-public-api.hoyolab.com/event/luna/os/info?lang=en-us&act_id=e202303301540311',
        os_sign_url='https://sg-public-api.hoyolab.com/event/luna/os/sign?lang=en-us',
    ),
    "ZZZ": GameConfig(
        os_act_id='e202406031448091',
        os_referer_url='https://act.hoyolab.com/bbs/event/signin/zzz/e202406031448091.html?act_id=e202406031448091',
        os_reward_url='https://sg-public-api.hoyolab.com/event/luna/zzz/os/home?lang=en-us&act_id=e202406031448091',
        os_role_url='https://api-os-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz=nap_global',
        os_info_url='https://sg-public-api.hoyolab.com/event/luna/zzz/os/info?lang=en-us&act_id=e202406031448091',
        os_sign_url='https://sg-public-api.hoyolab.com/event/luna/zzz/os/sign?lang=en-us',
        os_headers={"x-rpc-signgame": "zzz"}
    )
}

# Cached singletons — built once on first access
_app_settings: Optional[AppSettings] = None
_proxy_config: Optional[ProxyConfig] = None


def get_app_settings() -> AppSettings:
    """Return the cached AppSettings instance."""
    global _app_settings
    if _app_settings is None:
        _app_settings = AppSettings()
        if _app_settings.user_agent:
            for game_config in GAME_CONFIGS.values():
                game_config.wb_user_agent = _app_settings.user_agent
    return _app_settings


def get_proxy_config() -> ProxyConfig:
    """
    Return the cached ProxyConfig instance.

    USE_PROXY (legacy) enables proxy for both signin and Telegram.
    USE_PROXY_SIGNIN / USE_PROXY_TELEGRAM give per-channel control.
    """
    global _proxy_config
    if _proxy_config is None:
        s = get_app_settings()
        _proxy_config = ProxyConfig(
            use_proxy_signin=s.use_proxy_signin or s.use_proxy,
            use_proxy_telegram=s.use_proxy_telegram or s.use_proxy,
            proxy_data=s.proxy_data or os.getenv('PROXY_DATA'),
        )
    return _proxy_config


def load_accounts() -> List[AccountConfig]:
    """
    Load account configurations from environment variables.

    Supported formats:
      New: ACCOUNT_<ID>_COOKIES, ACCOUNT_<ID>_TELEGRAM_CHAT_ID, ACCOUNT_<ID>_ENABLED_GAMES
      Old: OS_COOKIE_<GAME>=cookie1@cookie2  (backward compat)
    """
    accounts: List[AccountConfig] = []
    settings = get_app_settings()

    # Old format — one env var per game, cookies separated by @
    for game_name in GAME_CONFIGS:
        cookies_str = os.getenv(f'OS_COOKIE_{game_name}', '')
        if not cookies_str:
            continue
        for idx, cookie in enumerate(cookies_str.split('@')):
            if not cookie.strip():
                continue
            try:
                account_id = (
                    cookie.split('account_id=')[1].split(';')[0]
                    if 'account_id=' in cookie
                    else f"{game_name}_{idx}"
                )
                chat_id = os.getenv(f'ACCOUNT_{account_id}_TELEGRAM_CHAT_ID') or settings.default_chat_id
                enabled_games_str = os.getenv(f'ACCOUNT_{account_id}_ENABLED_GAMES', '')
                enabled_games = [g.strip() for g in enabled_games_str.split(',')] if enabled_games_str else [game_name]

                accounts.append(AccountConfig(
                    account_id=account_id,
                    cookies=cookie,
                    telegram_chat_id=chat_id,
                    enabled_games=enabled_games,
                ))
            except Exception as e:
                logger.warning(f"Error parsing account from OS_COOKIE_{game_name}: {e}")

    # New format — ACCOUNT_<ID>_COOKIES
    seen_ids: set = set()
    for key, value in os.environ.items():
        if not (key.startswith('ACCOUNT_') and key.endswith('_COOKIES')):
            continue
        account_id = key[len('ACCOUNT_'):-len('_COOKIES')]
        if account_id in seen_ids or not value.strip():
            continue
        seen_ids.add(account_id)
        try:
            chat_id = os.getenv(f'ACCOUNT_{account_id}_TELEGRAM_CHAT_ID') or settings.default_chat_id
            enabled_games_str = os.getenv(f'ACCOUNT_{account_id}_ENABLED_GAMES', '')
            enabled_games = (
                [g.strip() for g in enabled_games_str.split(',')]
                if enabled_games_str
                else list(GAME_CONFIGS.keys())
            )
            accounts.append(AccountConfig(
                account_id=account_id,
                cookies=value,
                telegram_chat_id=chat_id,
                enabled_games=enabled_games,
            ))
        except Exception as e:
            logger.warning(f"Error parsing account {account_id}: {e}")

    return accounts


def get_telegram_config() -> TelegramConfig:
    """Get Telegram configuration."""
    settings = get_app_settings()
    return TelegramConfig(
        bot_token=settings.bot_token or os.getenv('BOT_API') or os.getenv('BOT_TOKEN'),
        default_chat_id=settings.default_chat_id or os.getenv('BOT_CHAT') or os.getenv('TELEGRAM_CHAT_ID'),
        enable_notifications=True,
    )
