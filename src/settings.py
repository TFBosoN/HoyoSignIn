# settings
import logging
import json
import requests
import socks
import os
from dotenv import load_dotenv
from requests.exceptions import HTTPError

load_dotenv()

__all__ = ['log', 'config', 'req']

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S')

log = logger = logging

config = {
    "HI3":{
        "LOG_LEVEL": logging.INFO,
        "LANG": 'en-us',
        "OS_ACT_ID": 'e202110291205111',
        "OS_REFERER_URL": 'https://act.hoyolab.com/bbs/event/signin-bh3/index.html?act_id={}'.format('e202110291205111'),
        "OS_REWARD_URL": 'https://sg-public-api.hoyolab.com/event/mani/home?lang={}&act_id={}'.format('en-us', 'e202110291205111'),
        "OS_ROLE_URL": 'https://api-os-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz={}'.format('bh3_global'),
        "OS_INFO_URL": 'https://sg-public-api.hoyolab.com/event/mani/info?lang={}&act_id={}'.format('en-us', 'e202110291205111'),
        "OS_SIGN_URL": 'https://sg-public-api.hoyolab.com/event/mani/sign?lang={}'.format('en-us'),
        "WB_USER_AGENT": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'
    },
    "Genshin": {
        "LOG_LEVEL": logging.INFO,
        "LANG": 'en-us',
        "OS_ACT_ID": 'e202102251931481',
        "OS_REFERER_URL": 'https://act.hoyolab.com/ys/event/signin-sea-v3/e202102251931481.html?act_id={}'.format('e202102251931481'),
        "OS_REWARD_URL": 'https://sg-hk4e-api.hoyolab.com/event/sol/home?lang={}&act_id={}'.format('en-us', 'e202102251931481'),
        "OS_ROLE_URL": 'https://api-os-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz={}'.format('hk4e_global'),
        "OS_INFO_URL": 'https://sg-hk4e-api.hoyolab.com/event/sol/info?lang={}&act_id={}'.format('en-us', 'e202102251931481'),
        "OS_SIGN_URL": 'https://sg-hk4e-api.hoyolab.com/event/sol/sign?lang={}'.format('en-us'),
        "WB_USER_AGENT": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'
    },
    "ToT": {
        "LOG_LEVEL": logging.INFO,
        "LANG": 'en-us',
        "OS_ACT_ID": 'e202308141137581',
        "OS_REFERER_URL": 'https://act.hoyolab.com/bbs/event/signin/nxx/index.html?act_id={}'.format('e202308141137581'),
        "OS_REWARD_URL": 'https://sg-public-api.hoyolab.com/event/luna/os/home?lang={}&act_id={}'.format('en-us', 'e202308141137581'),
        "OS_ROLE_URL": 'https://api-os-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz={}'.format('nxx_global'),
        "OS_INFO_URL": 'https://sg-public-api.hoyolab.com/event/luna/os/info?lang={}&act_id={}'.format('en-us', 'e202308141137581'),
        "OS_SIGN_URL": 'https://sg-public-api.hoyolab.com/event/luna/os/sign?lang={}'.format('en-us'),
        "WB_USER_AGENT": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'
    },
    "HSR": {
        "LOG_LEVEL": logging.INFO,
        "LANG": 'en-us',
        "OS_ACT_ID": 'e202303301540311',
        "OS_REFERER_URL": 'https://act.hoyolab.com/bbs/event/signin/hkrpg/e202303301540311.html?act_id={}'.format('e202303301540311'),
        "OS_REWARD_URL": 'https://sg-public-api.hoyolab.com/event/luna/os/home?lang={}&act_id={}'.format('en-us', 'e202303301540311'),
        "OS_ROLE_URL": 'https://api-os-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz={}'.format('hkrpg_global'),
        "OS_INFO_URL": 'https://sg-public-api.hoyolab.com/event/luna/os/info?lang={}&act_id={}'.format('en-us', 'e202303301540311'),
        "OS_SIGN_URL": 'https://sg-public-api.hoyolab.com/event/luna/os/sign?lang={}'.format('en-us'),
        "WB_USER_AGENT": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'
    },
    "ZZZ": {
        "LOG_LEVEL": logging.INFO,
        "LANG": 'en-us',
        "OS_ACT_ID": 'e202406031448091',
        "OS_REFERER_URL": 'https://act.hoyolab.com/bbs/event/signin/zzz/e202406031448091.html?act_id={}'.format('e202406031448091'),
        "OS_REWARD_URL": 'https://sg-act-nap-api.hoyolab.com/event/luna/zzz/os/home?lang={}&act_id={}'.format('en-us', 'e202406031448091'),
        "OS_ROLE_URL": 'https://api-os-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz={}'.format('nap_global'),
        "OS_INFO_URL": 'https://sg-act-nap-api.hoyolab.com/event/luna/zzz/os/info?lang={}&act_id={}'.format('en-us', 'e202406031448091'),
        "OS_SIGN_URL": 'https://sg-act-nap-api.hoyolab.com/event/luna/zzz/os/sign?lang={}'.format('en-us'),
        "WB_USER_AGENT": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'
    }
}

class HttpRequest(object):
    def __init__(self, use_proxy=False):
        self.use_proxy = use_proxy
        self.proxy = self._get_proxy() if self.use_proxy else None
        
    def _get_proxy(self):
        socks_proxy = 'socks5://' + os.getenv('PROXY_DATA')
        return {'http': socks_proxy, 'https': socks_proxy}
        
    @staticmethod
    def to_python(json_str: str):
        return json.loads(json_str)

    @staticmethod
    def to_json(obj):
        return json.dumps(obj, indent=4, ensure_ascii=False)

    def request(self, method, url, max_retry: int = 2,
                params=None, data=None, json=None, headers=None, **kwargs):
        for i in range(max_retry + 1):
            try:
                s = requests.Session()

                if self.proxy:
                    s.proxies = self.proxy

                response = s.request(method, url, params=params,
                                    data=data, json=json, headers=headers, **kwargs)
            except HTTPError as e:
                log.error(f'HTTP error:\n{e}')
                log.error(f'The NO.{i + 1} request failed, retrying...')
            except KeyError as e:
                log.error(f'Wrong response:\n{e}')
                log.error(f'The NO.{i + 1} request failed, retrying...')
            except Exception as e:
                log.error(f'Unknown error:\n{e}')
                log.error(f'The NO.{i + 1} request failed, retrying...')
            else:
                return response

        raise Exception(f'All {max_retry + 1} HTTP requests failed, die.')

# Add an option to use_proxy, default is False
use_proxy_option = os.getenv('USE_PROXY', 'False').lower() == 'true'
req = HttpRequest(use_proxy=use_proxy_option)

MESSAGE_TEMPLATE = '''
{today:=^12} ({uid}) {today:=^12}
    Account: {nick_name} - AR{level}
    Reward: {award_name} × {award_cnt}
    Count: {total_sign_day} days
    Result: {status}
'''

for game, game_config in config.items():
    game_config["WB_USER_AGENT"] = os.getenv('USER_AGENT')