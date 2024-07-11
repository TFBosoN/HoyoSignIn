import os
from settings import log, req

from dotenv import load_dotenv

load_dotenv()

class Notify(object):

    def __init__(self):
        # Custom Push Config
        self.PUSH_CONFIG = ''

    def send(self, app='', status='', msg='', **kwargs):
        hide = kwargs.get('hide', '')
        if isinstance(msg, list) or isinstance(msg, dict):
            msg = '\n\n'.join(msg)
        if not hide:
            log.info(f'Sign-In result: {status}\n\n{msg}')
        
        api = os.getenv('BOT_API')
        chat = os.getenv('BOT_CHAT')
        
        if api and chat:
            self.send_telegram_notification(api, chat, app, status, msg)
        else:
            log.info('No social media notifications configured to be sent.')

    def send_telegram_notification(self, api, chat, app, status, msg):
        log.info('Sending Telegram message...')
        params = {
            'chat_id': chat,
            'text': f"{app}\n{status}\n{msg}"
        }
        
        try:
            response = req.request("GET", f"https://api.telegram.org/bot{api}/sendMessage", params=params)
            response.raise_for_status()
            log.info(response.content)
        except Exception as e:
            self.handle_notification_error(e)

    def handle_notification_error(self, error):
        error_msg = f"Error sending Telegram notification: {str(error)}\n"
        log.error(error_msg)
        with open("error_log.txt", "a") as error_file:
            error_file.write(error_msg)

if __name__ == '__main__':
    Notify().send(app='Hoyo Helper', status='Test Run', msg='Testing integration with social media APIs')
