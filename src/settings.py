"""
Settings module for backward compatibility.
Uses new configuration system under the hood.
"""
import logging
from .config import GAME_CONFIGS, get_app_settings, get_telegram_config, get_proxy_config
from .http_client import HttpClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)

log = logger = logging

# For backward compatibility - convert new configuration to old format
config = {}
for game_name, game_config in GAME_CONFIGS.items():
    config[game_name] = {
        "LOG_LEVEL": game_config.log_level,
        "LANG": game_config.lang,
        "OS_ACT_ID": game_config.os_act_id,
        "OS_REFERER_URL": game_config.os_referer_url,
        "OS_REWARD_URL": game_config.os_reward_url,
        "OS_ROLE_URL": game_config.os_role_url,
        "OS_INFO_URL": game_config.os_info_url,
        "OS_SIGN_URL": game_config.os_sign_url,
        "WB_USER_AGENT": game_config.wb_user_agent,
        "OS_HEADERS": game_config.os_headers
    }

# HTTP client for backward compatibility
proxy_config = get_proxy_config()
req = HttpClient(use_proxy=proxy_config.use_proxy)

# Message template for backward compatibility
MESSAGE_TEMPLATE = '''
{today:=^12} ({uid}) {today:=^12}
    Account: {nick_name} - AR{level}
    Reward: {award_name} × {award_cnt}
    Count: {total_sign_day} days
    Result: {status}
'''

__all__ = ['log', 'config', 'req', 'MESSAGE_TEMPLATE']
