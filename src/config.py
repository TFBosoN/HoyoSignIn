"""
Module for secure configuration and secrets management.
Uses Pydantic for validation and type hints.
"""
import os
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, validator
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for pydantic < 2.0
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
            # Support string format for compatibility
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
        required_fields = ['account_id', 'cookie_token', 'ltoken', 'ltuid']
        missing = [field for field in required_fields if field not in v]
        if missing:
            raise ValueError(f"Missing required fields in cookies: {', '.join(missing)}")
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
    """Proxy configuration."""
    use_proxy: bool = False
    proxy_data: Optional[str] = None


class AppSettings(BaseSettings):
    """Main application settings."""
    user_agent: Optional[str] = None
    use_proxy: bool = False
    proxy_data: Optional[str] = None
    bot_token: Optional[str] = None
    default_chat_id: Optional[str] = None
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False


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


def get_app_settings() -> AppSettings:
    """Get application settings from environment variables."""
    return AppSettings()


def load_accounts() -> List[AccountConfig]:
    """
    Load account configurations from environment variables.
    
    Environment variable format:
    - OS_COOKIE_<GAME_NAME>=cookie1@cookie2@cookie3 (for backward compatibility)
    - ACCOUNT_<ID>_COOKIES=cookie_string
    - ACCOUNT_<ID>_TELEGRAM_CHAT_ID=chat_id (optional)
    - ACCOUNT_<ID>_ENABLED_GAMES=Genshin,HSR,HI3 (optional)
    """
    accounts: List[AccountConfig] = []
    settings = get_app_settings()
    
    # Old format for backward compatibility
    for game_name in GAME_CONFIGS.keys():
        env_var = f'OS_COOKIE_{game_name}'
        cookies_str = os.getenv(env_var, '')
        if cookies_str:
            cookie_list = cookies_str.split('@')
            for idx, cookie in enumerate(cookie_list):
                if cookie.strip():
                    try:
                        account_id = cookie.split('account_id=')[1].split(';')[0] if 'account_id=' in cookie else f"{game_name}_{idx}"
                        chat_id_env = os.getenv(f'ACCOUNT_{account_id}_TELEGRAM_CHAT_ID')
                        enabled_games_str = os.getenv(f'ACCOUNT_{account_id}_ENABLED_GAMES', '')
                        enabled_games = [g.strip() for g in enabled_games_str.split(',')] if enabled_games_str else [game_name]
                        
                        accounts.append(AccountConfig(
                            account_id=account_id,
                            cookies=cookie,
                            telegram_chat_id=chat_id_env or settings.default_chat_id,
                            enabled_games=enabled_games
                        ))
                    except Exception as e:
                        logger.warning(f"Error parsing account from {env_var}: {e}")
    
    # New format - search for all ACCOUNT_*_COOKIES
    seen_ids = set()
    for key, value in os.environ.items():
        if key.startswith('ACCOUNT_') and key.endswith('_COOKIES'):
            account_id = key.replace('ACCOUNT_', '').replace('_COOKIES', '')
            if account_id in seen_ids:
                continue
            seen_ids.add(account_id)
            
            if value.strip():
                try:
                    chat_id = os.getenv(f'ACCOUNT_{account_id}_TELEGRAM_CHAT_ID', settings.default_chat_id)
                    enabled_games_str = os.getenv(f'ACCOUNT_{account_id}_ENABLED_GAMES', '')
                    enabled_games = [g.strip() for g in enabled_games_str.split(',')] if enabled_games_str else list(GAME_CONFIGS.keys())
                    
                    accounts.append(AccountConfig(
                        account_id=account_id,
                        cookies=value,
                        telegram_chat_id=chat_id,
                        enabled_games=enabled_games
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
        enable_notifications=True
    )


def get_proxy_config() -> ProxyConfig:
    """Get proxy configuration."""
    settings = get_app_settings()
    return ProxyConfig(
        use_proxy=settings.use_proxy or os.getenv('USE_PROXY', 'False').lower() == 'true',
        proxy_data=settings.proxy_data or os.getenv('PROXY_DATA')
    )


# Update USER_AGENT for all games if globally set
_app_settings = get_app_settings()
if _app_settings.user_agent:
    for game_config in GAME_CONFIGS.values():
        game_config.wb_user_agent = _app_settings.user_agent
