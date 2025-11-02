"""
Module for performing check-ins in HoYoverse games.
"""
import time
import json
import logging
from typing import Dict, Any, Optional
from .http_client import HttpClient
from .config import GameConfig, GAME_CONFIGS

logger = logging.getLogger(__name__)

MESSAGE_TEMPLATE = '''
{nick_name}({uid}) - AR{level}
Reward: {award_name} × {award_cnt}
{total_sign_day} days - {status}
'''


class BaseSign:
    """Base class for working with API."""
    
    def __init__(self, cookies: str, http_client: Optional[HttpClient] = None):
        """
        Initialize.
        
        Args:
            cookies: Cookie string
            http_client: HTTP client. If None, creates a new one.
        """
        if not isinstance(cookies, str):
            raise TypeError(f'{self.__class__.__name__} expects str, got {type(cookies)}')
        
        self._cookie = cookies
        self.http_client = http_client or HttpClient()
    
    def get_header(self, config: GameConfig) -> Dict[str, str]:
        """
        Get headers for request.
        
        Args:
            config: Game configuration
            
        Returns:
            Dictionary with headers
        """
        header = {
            'User-Agent': config.wb_user_agent,
            'Referer': config.os_referer_url,
            'Accept-Encoding': 'gzip, deflate, br',
            'Cookie': self._cookie
        }
        
        # Add additional headers from configuration
        if config.os_headers:
            header.update(config.os_headers)
        
        return header


class Roles(BaseSign):
    """Class for working with roles and rewards."""
    
    def get_awards(self, config: GameConfig) -> Dict[str, Any]:
        """
        Get list of awards.
        
        Args:
            config: Game configuration
            
        Returns:
            API response with awards
        """
        try:
            response = self.http_client.request(
                'GET',
                config.os_reward_url,
                headers=self.get_header(config)
            )
            return self.http_client.to_python(response.text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error when getting awards: {e}")
            raise Exception(f"Error getting awards: {e}")
    
    def get_roles(self, config: GameConfig) -> Dict[str, Any]:
        """
        Get list of user roles.
        
        Args:
            config: Game configuration
            
        Returns:
            API response with roles
        """
        try:
            response = self.http_client.request(
                'GET',
                config.os_role_url,
                headers=self.get_header(config)
            )
            data = self.http_client.to_python(response.text)
            
            message = data.get('message', 'Unknown error')
            retcode = data.get('retcode', 1)
            
            if retcode != 0 or data.get('data') is None:
                raise Exception(f"Error getting roles: {message}")
            
            return data
        except Exception as e:
            logger.error(f"Error getting roles: {e}")
            raise


class Sign(BaseSign):
    """Class for performing check-ins."""
    
    def __init__(self, cookies: str, game_config: GameConfig, http_client: Optional[HttpClient] = None):
        """
        Initialize check-in.
        
        Args:
            cookies: Cookie string
            game_config: Game configuration
            http_client: HTTP client. If None, creates a new one.
        """
        super().__init__(cookies, http_client)
        self.config = game_config
        self._region_name = ''
        self._uid = ''
        self._level = ''
        self._nick_name = ''
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get check-in status information.
        
        Returns:
            Check-in information
        """
        roles_handler = Roles(self._cookie, self.http_client)
        user_game_roles = roles_handler.get_roles(self.config)
        role_list = user_game_roles.get('data', {}).get('list', [])
        
        if not role_list:
            raise Exception(user_game_roles.get('message', 'Role list is empty'))
        
        # Select role with highest level
        index = 0
        if len(role_list) > 1:
            highest_level = role_list[0].get('level', 0)
            for i in range(1, len(role_list)):
                current_level = role_list[i].get('level', 0)
                if current_level > highest_level:
                    highest_level = current_level
                    index = i
        
        self._region_name = role_list[index].get('region_name', 'NA')
        self._uid = role_list[index].get('game_uid', 'NA')
        self._level = role_list[index].get('level', 'NA')
        self._nick_name = role_list[index].get('nickname', 'NA')
        
        # Extract account_id from cookies
        try:
            aid = self._cookie.split('account_id=')[1].split(';')[0]
            logger.info(f'Checking in for account id {aid}...')
        except (IndexError, AttributeError):
            logger.warning('Failed to extract account_id from cookies')
        
        # Get check-in status information
        try:
            response = self.http_client.request(
                'GET',
                self.config.os_info_url,
                headers=self.get_header(self.config)
            )
            return self.http_client.to_python(response.text)
        except Exception as e:
            logger.error('Error getting check-in information')
            raise
    
    def run(self) -> str:
        """
        Perform check-in.
        
        Returns:
            Message about check-in result
        """
        message_list = []
        
        try:
            info_list = self.get_info()
            
            if not info_list:
                return "Error: failed to get check-in information"
            
            data = info_list.get('data', {})
            today = data.get('today', '')
            total_sign_day = data.get('total_sign_day', 0)
            is_sign = data.get('is_sign', False)
            first_bind = data.get('first_bind', False)
            
            roles_handler = Roles(self._cookie, self.http_client)
            awards_data = roles_handler.get_awards(self.config)
            awards = awards_data.get('data', {}).get('awards', [])
            
            uid = str(self._uid)
            
            # Small delay before check-in
            time.sleep(2)
            
            message = {
                'today': today,
                'region_name': self._region_name,
                'uid': uid,
                'level': self._level,
                'nick_name': self._nick_name,
                'total_sign_day': total_sign_day,
                'end': '',
            }
            
            # If already checked in today
            if is_sign:
                if total_sign_day > 0 and total_sign_day <= len(awards):
                    message['award_name'] = awards[total_sign_day - 1].get('name', 'Unknown')
                    message['award_cnt'] = awards[total_sign_day - 1].get('cnt', 0)
                else:
                    message['award_name'] = 'Unknown'
                    message['award_cnt'] = 0
                message['status'] = "Already done!"
                message_list.append(MESSAGE_TEMPLATE.format(**message))
                return ''.join(message_list)
            
            # If manual first-time check-in required
            if first_bind:
                message['award_name'] = 'N/A'
                message['award_cnt'] = 0
                message['status'] = 'Please check in manually once'
                message_list.append(MESSAGE_TEMPLATE.format(**message))
                return ''.join(message_list)
            
            # Perform check-in
            if total_sign_day < len(awards):
                message['award_name'] = awards[total_sign_day].get('name', 'Unknown')
                message['award_cnt'] = awards[total_sign_day].get('cnt', 0)
            else:
                message['award_name'] = 'Unknown'
                message['award_cnt'] = 0
            
            sign_data = {
                'act_id': self.config.os_act_id
            }
            
            try:
                response = self.http_client.request(
                    'POST',
                    self.config.os_sign_url,
                    headers=self.get_header(self.config),
                    data=json.dumps(sign_data, ensure_ascii=False)
                )
                result = self.http_client.to_python(response.text)
                
                code = result.get('retcode', 99999)
                
                # 0: success
                # -5003: already checked in
                if code != 0:
                    error_msg = result.get('message', f'Unknown error (code: {code})')
                    message['status'] = f'Error: {error_msg}'
                    message_list.append(MESSAGE_TEMPLATE.format(**message))
                    return ''.join(message_list)
                
                message['total_sign_day'] = total_sign_day + 1
                message['status'] = result.get('message', 'Success')
                message_list.append(MESSAGE_TEMPLATE.format(**message))
                
            except Exception as e:
                logger.error(f"Error performing check-in: {e}")
                message['status'] = f'Error: {str(e)}'
                message_list.append(MESSAGE_TEMPLATE.format(**message))
                return ''.join(message_list)
            
            logger.info('Check-in completed')
            return ''.join(message_list)
            
        except Exception as e:
            logger.error(f"Critical error during check-in: {e}")
            return f"Critical error: {str(e)}"
