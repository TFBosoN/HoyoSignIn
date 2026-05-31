"""
Module for performing check-ins in HoYoverse games.
"""
import time
import json
import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional
from .http_client import HttpClient
from .config import GameConfig

logger = logging.getLogger(__name__)


@dataclass
class SignResult:
    """
    Structured result from a single game check-in.
    All fields are available as template variables — see config.py GAME_ROW_TEMPLATE.
    """
    game: str           # "Genshin" | "HSR" | "HI3" | "ToT" | "ZZZ"
    success: bool       # False only on actual errors; "Already done!" counts as True
    status: str         # "OK" | "Already done!" | "Please check in manually" | "Error: …"
    player_name: str = 'N/A'
    uid: str = 'N/A'
    ar: int = 0         # Adventure Rank / Trailblaze Level / Captain Level
    region: str = 'N/A'
    day: int = 0        # Total sign-in days including today
    reward_name: str = 'N/A'
    reward_count: int = 0

    @property
    def level(self) -> int:
        """Alias for ar — use either {ar} or {level} in your template."""
        return self.ar

    @property
    def status_icon(self) -> str:
        return '✅' if self.success else '❌'


class BaseSign:
    """Base class for working with API."""

    def __init__(self, cookies: str, http_client: Optional[HttpClient] = None):
        if not isinstance(cookies, str):
            raise TypeError(f'{self.__class__.__name__} expects str, got {type(cookies)}')
        self._cookie = cookies
        self.http_client = http_client or HttpClient()

    def get_header(self, config: GameConfig) -> Dict[str, str]:
        header = {
            'User-Agent': config.wb_user_agent,
            'Referer': config.os_referer_url,
            'Accept-Encoding': 'gzip, deflate, br',
            'Cookie': self._cookie,
        }
        if config.os_headers:
            header.update(config.os_headers)
        return header


class Roles(BaseSign):
    """Fetches user roles and available rewards."""

    def get_awards(self, config: GameConfig) -> Dict[str, Any]:
        try:
            response = self.http_client.request('GET', config.os_reward_url, headers=self.get_header(config))
            return self.http_client.to_python(response.text)
        except json.JSONDecodeError as e:
            raise Exception(f"Error getting awards: {e}") from e

    def get_roles(self, config: GameConfig) -> Dict[str, Any]:
        try:
            response = self.http_client.request('GET', config.os_role_url, headers=self.get_header(config))
            data = self.http_client.to_python(response.text)
            retcode = data.get('retcode', 1)
            if retcode != 0 or data.get('data') is None:
                raise Exception(f"Error getting roles: {data.get('message', 'Unknown error')}")
            return data
        except Exception as e:
            logger.error(f"Error getting roles: {e}")
            raise


class Sign(BaseSign):
    """Performs the daily check-in for one game account."""

    def __init__(
        self,
        cookies: str,
        game_name: str,
        game_config: GameConfig,
        http_client: Optional[HttpClient] = None,
    ):
        super().__init__(cookies, http_client)
        self.game_name = game_name
        self.config = game_config
        self._region_name = ''
        self._uid = ''
        self._level: Any = 0
        self._nick_name = ''

    def _make_error_result(self, status: str) -> SignResult:
        return SignResult(
            game=self.game_name,
            success=False,
            status=status,
            player_name=self._nick_name or 'N/A',
            uid=str(self._uid) or 'N/A',
            ar=int(self._level) if str(self._level).isdigit() else 0,
            region=self._region_name or 'N/A',
        )

    def get_info(self) -> Dict[str, Any]:
        roles_handler = Roles(self._cookie, self.http_client)
        user_game_roles = roles_handler.get_roles(self.config)
        role_list = user_game_roles.get('data', {}).get('list', [])

        if not role_list:
            raise Exception(user_game_roles.get('message', 'Role list is empty'))

        # Pick the highest-level role
        index = max(range(len(role_list)), key=lambda i: role_list[i].get('level', 0))

        self._region_name = role_list[index].get('region_name', 'N/A')
        self._uid = role_list[index].get('game_uid', 'N/A')
        self._level = role_list[index].get('level', 0)
        self._nick_name = role_list[index].get('nickname', 'N/A')

        try:
            aid = self._cookie.split('account_id=')[1].split(';')[0]
            logger.info(f'Checking in for account id {aid}...')
        except (IndexError, AttributeError):
            logger.warning('Failed to extract account_id from cookies')

        response = self.http_client.request('GET', self.config.os_info_url, headers=self.get_header(self.config))
        return self.http_client.to_python(response.text)

    def run(self) -> SignResult:
        """Perform check-in and return a structured SignResult."""
        try:
            info = self.get_info()
            if not info:
                return self._make_error_result('Error: failed to get check-in info')

            data = info.get('data', {})
            total_sign_day: int = data.get('total_sign_day', 0)
            is_sign: bool = data.get('is_sign', False)
            first_bind: bool = data.get('first_bind', False)

            awards_data = Roles(self._cookie, self.http_client).get_awards(self.config)
            awards = awards_data.get('data', {}).get('awards', [])

            ar = int(self._level) if str(self._level).isdigit() else 0

            def reward_at(idx: int):
                if 0 <= idx < len(awards):
                    return awards[idx].get('name', 'N/A'), awards[idx].get('cnt', 0)
                return 'N/A', 0

            if is_sign:
                reward_name, reward_count = reward_at(total_sign_day - 1)
                return SignResult(
                    game=self.game_name, success=True, status='Already done!',
                    player_name=self._nick_name, uid=str(self._uid), ar=ar,
                    region=self._region_name, day=total_sign_day,
                    reward_name=reward_name, reward_count=reward_count,
                )

            if first_bind:
                return SignResult(
                    game=self.game_name, success=False, status='Please check in manually',
                    player_name=self._nick_name, uid=str(self._uid), ar=ar,
                    region=self._region_name, day=total_sign_day,
                )

            reward_name, reward_count = reward_at(total_sign_day)

            time.sleep(2)  # brief delay before the POST to appear more human-like
            try:
                response = self.http_client.request(
                    'POST', self.config.os_sign_url,
                    headers=self.get_header(self.config),
                    data=json.dumps({'act_id': self.config.os_act_id}, ensure_ascii=False),
                )
                result = self.http_client.to_python(response.text)
                code = result.get('retcode', 99999)

                if code != 0:
                    msg = result.get('message', f'Unknown error (code: {code})')
                    return SignResult(
                        game=self.game_name, success=False, status=f'Error: {msg}',
                        player_name=self._nick_name, uid=str(self._uid), ar=ar,
                        region=self._region_name, day=total_sign_day,
                        reward_name=reward_name, reward_count=reward_count,
                    )

                api_msg = result.get('message', 'OK')
                status = 'OK' if api_msg.lower() in ('ok', 'success', '') else api_msg
                logger.info('Check-in completed')
                return SignResult(
                    game=self.game_name, success=True, status=status,
                    player_name=self._nick_name, uid=str(self._uid), ar=ar,
                    region=self._region_name, day=total_sign_day + 1,
                    reward_name=reward_name, reward_count=reward_count,
                )

            except Exception as e:
                logger.error(f"Error performing check-in: {e}")
                return SignResult(
                    game=self.game_name, success=False, status=f'Error: {e}',
                    player_name=self._nick_name, uid=str(self._uid), ar=ar,
                    region=self._region_name, day=total_sign_day,
                    reward_name=reward_name, reward_count=reward_count,
                )

        except Exception as e:
            logger.error(f"Critical error during check-in: {e}")
            return self._make_error_result(f'Error: {e}')
