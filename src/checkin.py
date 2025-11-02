"""
Main module for performing daily check-ins.
"""
import logging
from datetime import datetime
from typing import List, Dict, Any
try:
    from .config import (
        get_app_settings,
        load_accounts,
        GAME_CONFIGS,
        AccountConfig,
        GameConfig
    )
    from .notify import TelegramNotifier
    from .sign import Sign
except ImportError:
    # For running as script
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.config import (
        get_app_settings,
        load_accounts,
        GAME_CONFIGS,
        AccountConfig,
        GameConfig
    )
    from src.notify import TelegramNotifier
    from src.sign import Sign

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


class CheckInManager:
    """Manager for handling check-ins."""
    
    def __init__(self):
        """Initialize manager."""
        self.telegram = TelegramNotifier()
        self.accounts = load_accounts()
        logger.info(f"Loaded accounts: {len(self.accounts)}")
    
    def run_check_in_for_game(
        self,
        game_name: str,
        game_config: GameConfig,
        account: AccountConfig
    ) -> Dict[str, Any]:
        """
        Perform check-in for specific game and account.
        
        Args:
            game_name: Game name
            game_config: Game configuration
            account: Account configuration
            
        Returns:
            Dictionary with result: success, message, account_id
        """
        account_id = account.account_id
        logger.info(f'Preparing check-in for {game_name}, account {account_id}...')
        
        try:
            sign_handler = Sign(account.cookies, game_config)
            msg = sign_handler.run()
            
            return {
                'success': True,
                'message': msg,
                'account_id': account_id,
                'game': game_name
            }
            
        except IndexError:
            cookie_values = ["account_id", "cookie_token", "ltoken", "ltuid", "mi18nLang", "_MHYUUID"]
            missing = [val for val in cookie_values if val not in account.cookies]
            
            if missing:
                logger.error(f'Missing fields in cookies: {", ".join(missing)}')
            
            error_msg = (
                f"{game_name} Check-In: Try these troubleshooting steps:\n"
                f"- Log out and log back in\n"
                f"- Make sure you are on the Daily Rewards page, not the HoyoLab Forums page\n"
                f"- Try incognito mode\n"
                f"- Try clearing browser history/cache\n"
                f"- Try using another browser\n"
            )
            
            return {
                'success': False,
                'message': error_msg,
                'account_id': account_id,
                'game': game_name
            }
            
        except Exception as e:
            logger.error(f"{game_name} Check-In for account {account_id}: {e}")
            return {
                'success': False,
                'message': f'{game_name} Check-In for account {account_id}:\n {e}',
                'account_id': account_id,
                'game': game_name
            }
    
    def run_check_in_for_account(
        self,
        account: AccountConfig
    ) -> Dict[str, Any]:
        """
        Perform check-in for account in all enabled games.
        
        Args:
            account: Account configuration
            
        Returns:
            Dictionary with results for each game
        """
        results = {}
        
        for game_name in account.enabled_games:
            if game_name not in GAME_CONFIGS:
                logger.warning(f"Game {game_name} not found in configuration. Skipping.")
                continue
            
            game_config = GAME_CONFIGS[game_name]
            result = self.run_check_in_for_game(game_name, game_config, account)
            results[game_name] = result
        
        return results
    
    def run_all(self):
        """Perform check-in for all accounts."""
        if not self.accounts:
            logger.error("No accounts found. Please check configuration.")
            return
        
        all_results = []
        
        for account in self.accounts:
            logger.info(f"Processing account: {account.account_id}")
            account_results = self.run_check_in_for_account(account)
            all_results.append({
                'account_id': account.account_id,
                'telegram_chat_id': account.telegram_chat_id,
                'results': account_results
            })
        
        # Send notifications
        self._send_notifications(all_results)
    
    def _send_notifications(self, all_results: List[Dict[str, Any]]):
        """
        Send notifications about check-in results.
        
        Args:
            all_results: List of check-in results
        """
        today = datetime.now().strftime('%d.%m.%Y')
        
        # Group results by chat_id for sending
        notifications_by_chat: Dict[str, List[str]] = {}
        
        for account_result in all_results:
            chat_id = account_result.get('telegram_chat_id')
            account_id = account_result['account_id']
            results = account_result['results']
            
            if not results:
                continue
            
            # Build message for account
            messages = [f"{today}"]
            total_success = 0
            total_fail = 0
            
            for game_name, result in results.items():
                if result['success']:
                    total_success += 1
                else:
                    total_fail += 1
                
                messages.append(f"\n{game_name}:")
                messages.append(result['message'])
            
            # Status for account
            total = total_success + total_fail
            status = f"Account {account_id}: {total_success}/{total} succeeded"
            
            # Combine all messages
            full_message = '\n'.join(messages)
            
            # Group by chat_id
            if chat_id:
                if chat_id not in notifications_by_chat:
                    notifications_by_chat[chat_id] = []
                notifications_by_chat[chat_id].append(f"{status}\n{full_message}")
            else:
                # Use default_chat_id if not specified
                default_chat = self.telegram.config.default_chat_id
                if default_chat:
                    if default_chat not in notifications_by_chat:
                        notifications_by_chat[default_chat] = []
                    notifications_by_chat[default_chat].append(f"{status}\n{full_message}")
        
        # Send notifications
        for chat_id, messages in notifications_by_chat.items():
            combined_message = '\n'.join(messages)
            total_all_success = sum(1 for ar in all_results for r in ar['results'].values() if r['success'])
            total_all = sum(len(ar['results']) for ar in all_results)
            
            status_msg = f"Total: {total_all_success}/{total_all} succeeded"
            self.telegram.send(
                chat_id=chat_id,
                app='HoyoSignIn',
                status=status_msg,
                msg=combined_message
            )


def run_check_in(game_name: str = None, game_config: GameConfig = None):
    """
    Function for backward compatibility.
    Performs check-in for specific game.
    
    Args:
        game_name: Game name
        game_config: Game configuration
    """
    if game_name and game_config:
        # Old format - for backward compatibility
        manager = CheckInManager()
        accounts = load_accounts()
        
        for account in accounts:
            if game_name in account.enabled_games:
                result = manager.run_check_in_for_game(game_name, game_config, account)
                # Send notification for each account
                chat_id = account.telegram_chat_id or manager.telegram.config.default_chat_id
                if chat_id:
                    manager.telegram.send(
                        chat_id=chat_id,
                        app=f'{game_name} Helper',
                        status=f"{result['account_id']}: {'Success' if result['success'] else 'Error'}",
                        msg=result['message']
                    )


if __name__ == '__main__':
    manager = CheckInManager()
    manager.run_all()
